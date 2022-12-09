"""
Mac osx bar menus.
"""

import tkinter

import cfg
from utils import place_center

from .widgets import CLabel, CWindow, CloseBtn
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


class About(CWindow):
    def __init__(self):
        CWindow.__init__(self)
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
        close_btn = CloseBtn(self, text='Закрыть')
        close_btn.pack()

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.grab_set()
