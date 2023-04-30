from . import cfg, close_windows, focus_last, on_exit, place_center, tkinter

__all__ = (
    "CSep",
    "CButton",
    "CFrame",
    "CLabel",
    "CWindow",
    "CloseBtn",
    "InfoWidget",
    "AskExit",
    "SmbAlert",
    )


def close():
    close_windows()
    focus_last()


class CSep(tkinter.Frame):
    def __init__(self, master: tkinter):
        tkinter.Frame.__init__(self, master, bg=cfg.BUTTON, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BUTTON, fg=cfg.FONT, width=13, height=1)

        self.bind('<Enter>', lambda e: self.enter())
        self.bind('<Leave>', lambda e: self.leave())

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)

    def press(self):
        self.configure(bg=cfg.PRESSED)
        cfg.ROOT.after(100, lambda: self.configure(bg=cfg.BUTTON))

    def enter(self):
        if self['bg'] != cfg.PRESSED:
            self['bg'] = cfg.SELECTED

    def leave(self):
        if self['bg'] != cfg.PRESSED:
            self['bg'] = cfg.BUTTON


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Frame.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BG)


class CLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BG, fg=cfg.FONT)


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

        if cfg.config["ASK_EXIT"] == 1:
            self.bind('<Command-q>', lambda e: AskExit())
        else:
            self.bind('<Command-q>', lambda e: on_exit())

        self.resizable(0,0)
        self.configure(bg=cfg.BG, padx=15, pady=15)

    def error_exit(self):
        close()


class CloseBtn(CButton):
    def __init__(self, master: tkinter.Widget, **kwargs):
        CButton.__init__(self, master, **kwargs)
        self.cmd(lambda e: close())


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
        self.grab_set()

    def close_ask(self):
        self.destroy()
        focus_last()

    def exit_task(self):
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
            '\n- Укажите правильный путь к коллекциям в настройках'
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
