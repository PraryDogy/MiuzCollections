import os
import subprocess
import threading
import tkinter
from functools import partial

import cfg
from utils import close_windows, encrypt_cfg, focus_last, my_copy, place_center


def close():
    close_windows()
    focus_last()


class CSep(tkinter.Frame):
    def __init__(self, master: tkinter):
        tkinter.Frame.__init__(self, master, bg=cfg.BGBUTTON, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGBUTTON, fg=cfg.BGFONT, width=13, height=1)

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
        withdraw = true
        """
        tkinter.Toplevel.__init__(self)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: close())
        self.bind('<Command-w>', lambda e: close())
        self.bind('<Escape>', lambda e: close())
        self.bind('<Command-q>', lambda e: AskExit())
        self.resizable(0,0)
        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)

    def error_exit(self):
        close()


class CloseBtn(CButton):
    def __init__(self, master: tkinter.Widget, **kwargs):
        CButton.__init__(self, master, **kwargs)
        self.cmd(lambda e: close())


class ImgBtns(CFrame):
    def __init__(self, master: tkinter, img_src, **kwargs):
        CFrame.__init__(self, master, **kwargs)

        self.img_src = img_src
        self.img_src: str

        copy_btn = CButton(self, text='Копировать имя')
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        open_btn = CButton(self, text='Открыть папку')
        open_btn.cmd(partial(self.open_folder, open_btn))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def copy_name(self, btn: CButton):
        btn.press()
        my_copy(self.img_src.split(os.sep)[-1].split('.')[0])

    def open_folder(self, btn: CButton, e: tkinter.Event):
        btn.press()
        path = os.path.split(self.img_src)[0]

        def open():
            subprocess.check_output(["/usr/bin/open", path])

        threading.Thread(target=open).start()


class InfoWidget(CFrame):
    def __init__(self, master: tkinter, ln, info1, info2, **kwargs):
        CFrame.__init__(self, master, **kwargs)

        label1 = CLabel(self)
        label1.configure(
            text=info1, justify=tkinter.LEFT,
            anchor=tkinter.E, width=ln)
        label1.pack(side=tkinter.LEFT, anchor=tkinter.E)

        CSep(self).pack(side=tkinter.LEFT, fill=tkinter.Y, padx=10)

        label2 = CLabel(self)
        label2.configure(
            text=info2, justify=tkinter.LEFT,
            anchor=tkinter.W, width=ln)
        label2.pack(side=tkinter.LEFT)


class AskExit(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.bind('<Return>', lambda e: self.on_exit())
        self.protocol("WM_DELETE_WINDOW", lambda: self.close_ask())
        self.bind('<Command-w>', lambda e: self.close_ask())
        self.bind('<Escape>', lambda e: self.close_ask())

        lbl = CLabel(self, text='Выйти?')
        lbl.pack()

        btns_frame = CFrame(self)
        btns_frame.pack()

        exit = CButton(self, text='Выйти')
        exit.cmd(lambda e: self.on_exit())

        cancel = CButton(self, text='Отмена')
        cancel.cmd(lambda e: self.close_ask())

        [i.configure(height=1, width=11) for i in (exit, cancel)]
        [i.pack(side=tkinter.LEFT, padx=5) for i in (exit, cancel)]

        place_center(self)
        self.deiconify()
        self.grab_set()

    def close_ask(self):
        self.destroy()
        focus_last()

    def on_exit(self):
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
        cfg.config['GEOMETRY'] = [w, h, x, y]
        encrypt_cfg(cfg.config)
        cfg.FLAG = False
        quit()


class SmbAlert(tkinter.Toplevel):
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
