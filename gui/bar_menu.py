"""
Mac osx bar menus.
"""

import tkinter

import cfg
from utils import MyButton, MyLabel, place_center

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
        self.add_command(label="О программе", command=self.about)
        self.add_separator()
        self.add_command(label="Выход", command=cfg.ROOT.destroy)

        cfg.ROOT.createcommand(
            'tkAboutDialog',
            lambda: cfg.ROOT.tk.call('tk::mac::standardAboutPanel'))

        cfg.ROOT.configure(menu=menubar)

    def about(self):
        """
        Creates tkinter toplevel with info about app.
        """
        new_win = tkinter.Toplevel(
            cfg.ROOT, bg=cfg.BGCOLOR, pady=10, padx=10)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        new_win.withdraw()
        new_win.title('О программе')

        new_win.protocol("WM_DELETE_WINDOW", new_win.destroy)
        new_win.bind('<Command-w>', lambda e: new_win.destroy())
        new_win.bind('<Escape>', lambda e: new_win.destroy())

        name = (
            f'{cfg.APP_NAME} {cfg.APP_VER}'
            '\n\n'
            )

        made = (
            'Created by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.'
            )

        author = MyLabel(new_win, text=name+made)
        author.pack()

        descr = (
            'Email: evlosh@gmail.com'
            '\nTelegram: evlosh'
            '\n'
        )

        descr_lbl = MyLabel(new_win, text=descr)
        descr_lbl.pack()

        close_btn = MyButton(new_win)
        close_btn.configure(height=2, width=17, text='Закрыть')
        close_btn.cmd(lambda e: new_win.destroy())
        close_btn.pack()

        place_center(new_win)
        new_win.deiconify()
        new_win.grab_set()
