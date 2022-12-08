"""
Mac osx bar menus.
"""

import tkinter

import cfg
from utils import place_center

from .widgets import CButton, CLabel
from .settings import Settings


class BarMenu(tkinter.Menu):
    """
    Mac osx bar menu.
    """
    def __init__(self):
        menubar = tkinter.Menu(cfg.ROOT)
        tkinter.Menu.__init__(self, menubar)
        menubar.add_cascade(label="Меню", menu=self)
        self.add_command(
            label='Настройки', command=Settings)
        self.add_command(label="О программе", command=About)
        self.add_separator()
        self.add_command(label="Выход", command=cfg.ROOT.destroy)
        cfg.ROOT.createcommand(
            'tkAboutDialog',
            lambda: cfg.ROOT.tk.call('tk::mac::standardAboutPanel'))
        cfg.ROOT.configure(menu=menubar)


class About(tkinter.Toplevel):
    def __init__(self):
        """
        Creates tkinter toplevel with info about app.
        """
        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR, pady=15, padx=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()
        self.title('О программе')
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind('<Command-w>', lambda e: self.on_exit(self))
        self.bind('<Escape>', lambda e: self.on_exit(self))
        made = (
            f'{cfg.APP_NAME} {cfg.APP_VER}'
            '\n\nCreated by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.'
            '\n\nEmail: evlosh@gmail.com'
            '\nTelegram: evlosh'
            )
        author = CLabel(self, text=made)
        author.pack(pady=(0, 10))
        close_btn = CButton(self)
        close_btn.configure(height=1, width=12, text='Закрыть')
        close_btn.cmd(lambda e: self.on_exit(self))
        close_btn.pack()
        place_center(self)
        self.deiconify()
        self.grab_set()


    def on_exit(self, win: tkinter.Toplevel):
        win.destroy()
        cfg.ROOT.focus_force()