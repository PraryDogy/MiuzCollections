from . import (Image, cfg, datetime, get_coll_name, on_exit, os, place_center,
               tkinter, sys)

__all__ = (
    "CSep",
    "CButton",
    "CFrame",
    "CLabel",
    "CWindow",
    "CloseBtn",
    "AskExit",
    "SmbAlert",
    "ImageInfo",
    "MacMenu",
    )


class CSep(tkinter.Frame):
    def __init__(self, master: tkinter):
        tkinter.Frame.__init__(self, master, bg=cfg.BUTTON, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(
            bg=cfg.BUTTON, fg=cfg.FONT, width=13, height=1,
            font=("San Francisco Pro", 13, "normal"))

        # self.bind('<Enter>', lambda e: self.enter())
        # self.bind('<Leave>', lambda e: self.leave())

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)

    def press(self):
        self.configure(bg=cfg.SELECTED)
        cfg.ROOT.after(100, lambda: self.configure(bg=cfg.BUTTON))

    def enter(self):
        if self['bg'] != cfg.SELECTED:
            self['bg'] = cfg.HOVERED

    def leave(self):
        if self['bg'] != cfg.SELECTED:
            self['bg'] = cfg.BUTTON


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Frame.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BG)


class CLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(
            bg=cfg.BG, fg=cfg.FONT, font=("San Francisco Pro", 13, "normal")
            )


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

        self.protocol("WM_DELETE_WINDOW", lambda: self.close_win())
        self.bind('<Command-w>', lambda e: self.close_win())
        self.bind('<Escape>', lambda e: self.close_win())

        if cfg.config["ASK_EXIT"] == 1:
            self.bind('<Command-q>', lambda e: AskExit())
        else:
            self.bind('<Command-q>', lambda e: on_exit())

        self.resizable(0,0)
        self.configure(bg=cfg.BG, padx=15, pady=15)


    def close_win(self):
        self.destroy()
        cfg.ROOT.focus_force()


class CloseBtn(CButton):
    def __init__(self, master: tkinter.Widget, **kwargs):
        CButton.__init__(self, master, **kwargs)
        self.cmd(lambda e: self.destroy())


class AskExit(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.bind('<Return>', lambda e: on_exit())
        self.protocol("WM_DELETE_WINDOW", lambda: self.close_ask())
        self.bind('<Command-w>', lambda e: self.close_ask())
        self.bind('<Escape>', lambda e: self.close_ask())

        lbl = CLabel(self, text='Выйти?')
        lbl.pack()

        btns_frame = CFrame(self)
        btns_frame.pack()

        exit = CButton(self, text='Выйти')
        exit.cmd(lambda e: on_exit())

        cancel = CButton(self, text='Отмена')
        cancel.cmd(lambda e: self.close_ask())

        [i.configure(height=1, width=11) for i in (exit, cancel)]
        [i.pack(side=tkinter.LEFT, padx=5) for i in (exit, cancel)]

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def close_ask(self):
        self.destroy()
        cfg.ROOT.focus_force()

    def exit_task(self):
        quit()


class SmbAlert(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title('Нет подключения')

        txt = 'Нет подключения к сетевому диску Miuz.'
        title_lbl = CLabel(
            self, text=txt, font=('San Francisco Pro', 22, 'bold'))
        title_lbl.pack(pady=(0, 5), padx=20)

        txt2 =(
            'Рекомендации:'
            '\n- Проверьте подключение к интернету.'
            '\n- Откройте любую папку на сетевом диске,'
            '\n- Укажите правильный путь к коллекциям в настройках'
            '\n- Перезапустите приложение.'

            '\n\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        descr_lbl = CLabel(self, text=txt2, justify=tkinter.LEFT, )
        descr_lbl.pack(padx=15, pady=(0, 5))

        btn = CButton(self, text = "Закрыть")
        btn.cmd(lambda e: self.destroy())
        btn.pack()

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()


class ImageInfo(CWindow):
    def __init__(self, src: str, win: tkinter.Toplevel):
        CWindow.__init__(self)
        self.win = win

        self.title("Инфо")
        self.geometry("400x150")
        self.resizable(1, 1)

        name = src.split(os.sep)[-1]
        filemod = datetime.fromtimestamp(os.path.getmtime(src))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
        w, h = Image.open(src).size
        filesize = round(os.path.getsize(src)/(1024*1024), 2)

        coll = f'Коллекция: {get_coll_name(src)}'
        name = f"Имя файла: {name}"
        modified = f'Дата изменения: {filemod}'
        res = f'Разрешение: {w}x{h}'
        filesize = f"Размер: {filesize}мб"
        path = f"Местонахождение: {src}"

        text = "\n".join([coll, name, modified, res, filesize, path])

        lbl = CLabel(
            self,
            text = text,
            justify = tkinter.LEFT,
            anchor = tkinter.W,
            )
        lbl.pack()

        self.protocol("WM_DELETE_WINDOW", lambda: self.close_win())
        self.bind('<Command-w>', lambda e: self.close_win())
        self.bind('<Escape>', lambda e: self.close_win())

        cfg.ROOT.update_idletasks()

        x, y = self.win.winfo_x(), self.win.winfo_y()
        xx = x + self.win.winfo_width()//2 - self.winfo_width()//2
        yy = y + self.win.winfo_height()//2 - self.winfo_height()//2

        self.geometry(f'+{xx}+{yy}')

        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def close_win(self):
        self.destroy()
        self.win.focus_force()
        if self.win.winfo_class() != "Tk":
            self.win.grab_set_global()


class MacMenu(tkinter.Menu):
    """
    Mac osx bar menu.
    """
    def __init__(self):
        menubar = tkinter.Menu(cfg.ROOT)
        tkinter.Menu.__init__(self, menubar)

        if sys.version_info.minor < 10:
            cfg.ROOT.createcommand('tkAboutDialog', self.about_dialog)

        cfg.ROOT.configure(menu=menubar)

    def about_dialog(self):
        try:
            cfg.ROOT.tk.call('tk::mac::standardAboutPanel')
        except Exception:
            print("no dialog panel")