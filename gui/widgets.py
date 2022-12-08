import os
import subprocess
import threading
import tkinter
from functools import partial

import cfg
from utils import encrypt_cfg, my_copy, place_center, close_windows


class CSep(tkinter.Frame):
    def __init__(self, master: tkinter):
        tkinter.Frame.__init__(self, master, bg=cfg.BGBUTTON, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Label.__init__(
            self, master, bg=cfg.BGBUTTON, fg=cfg.BGFONT, **kwargs)
        self.bind('<Enter>', lambda e: self.enter())
        self.bind('<Leave>', lambda e: self.leave())

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)

    def press(self):
        self.configure(bg=cfg.BGPRESSED)
        cfg.ROOT.after(100, lambda: self.configure(bg=cfg.BGBUTTON))

    def enter(self):
        if self['bg'] != cfg.BGPRESSED:
            self['bg'] = cfg.BGSELECTED

    def leave(self):
        if self['bg'] != cfg.BGPRESSED:
            self['bg'] = cfg.BGBUTTON


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Frame.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR)


class CLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR, fg=cfg.BGFONT)


class CWindow(tkinter.Toplevel):
    def __init__(self):
        """
        bg=cfg.BGCOLOR, padx=15, pady=15
        resizable 0
        center screen
        cmd+w, escape and X button bind to close window
        """
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: close_windows())
        self.bind('<Command-w>', lambda e: close_windows())
        self.bind('<Escape>', lambda e: close_windows())
        self.resizable(0,0)


class CloseBtn(CButton):
    def __init__(self, master: tkinter.Widget, **kwargs):
        CButton.__init__(self, master, **kwargs)
        self.configure(height=1, width=13)
        self.cmd(lambda e: master.winfo_toplevel().destroy())


class ImgBtns(CFrame):
    def __init__(self, master: tkinter, **kwargs):
        CFrame.__init__(self, master, **kwargs)

        copy_btn = CButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=13)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        open_btn = CButton(self, text='Открыть папку')
        open_btn.configure(height=1, width=13)
        open_btn.cmd(partial(self.open_folder, open_btn))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def copy_name(self, btn: CButton):
        btn.press()
        my_copy(cfg.IMG_SRC.split(os.sep)[-1].split('.')[0])

    def open_folder(self, btn: CButton, e: tkinter.Event):
        btn.press()
        path = os.sep.join(cfg.IMG_SRC.split(os.sep)[:-1])

        def open():
            subprocess.check_output(["/usr/bin/open", path])

        threading.Thread(target=open).start()


class AskExit(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.bind('<Return>', lambda e: self.on_exit())
        self.protocol("WM_DELETE_WINDOW", lambda: self.destroy())

        self.unbind('<Command-w>')
        self.unbind('<Escape>')
        self.bind('<Command-w>', lambda e: self.destroy())
        self.bind('<Escape>', lambda e: self.destroy())

        lbl = CLabel(self, text='Выйти?')
        lbl.pack()

        btns_frame = CFrame(self)
        btns_frame.pack()

        exit = CButton(self, text='Выйти')
        exit.cmd(lambda e: self.on_exit())

        cancel = CButton(self, text='Отмена')
        cancel.cmd(lambda e: self.destroy())

        [i.configure(height=1, width=11) for i in (exit, cancel)]
        [i.pack(side=tkinter.LEFT, padx=5) for i in (exit, cancel)]

        place_center(self)
        self.deiconify()
        self.grab_set()

    def on_exit(self):
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
        cfg.config['GEOMETRY'] = [w, h, x, y]
        encrypt_cfg(cfg.config)
        cfg.FLAG = False
        quit()


class SmbChecker(tkinter.Toplevel):
    def __init__(self):
        CWindow.__init__(self)
        self.title('Нет подключения')

        txt = 'Нет подключения к сетевому диску Miuz.'
        title_lbl = CLabel(
            self, text=txt, font=('Arial', 22, 'bold'), wraplength=350)
        title_lbl.pack(pady=(10, 20), padx=20)

        txt2 =(
            'Рекомендации:'
            '\n- Проверьте подключение к интернету.'
            '\n- Откройте любую папку на сетевом диске,'
            '\n- Укажите правильный путь до галерии фото и коллекций'
            '\n- Перезапустите приложение.'

            '\n\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        descr_lbl = CLabel(self, text=txt2, justify=tkinter.LEFT)
        descr_lbl.pack(padx=15, pady=(0, 15))

        cls_btn = CloseBtn(self, text='Закрыть')
        cls_btn.pack()

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.grab_set()
