from . import cfg, place_center, tkinter
from .settings import Settings
from .widgets import CLabel, CButton, CWindow
from . import sys

__all__ = (
    "MacMenu"
    )


class MacMenu(tkinter.Menu):
    """
    Mac osx bar menu.
    """
    def __init__(self):
        menubar = tkinter.Menu(cfg.ROOT)
        tkinter.Menu.__init__(self, menubar)
        menubar.add_cascade(label="Меню", menu=self)
        self.add_command(
            label='Настройки', command=Settings)
        self.add_command(label="О программе", command=self.about_widget)
        self.add_separator()
        self.add_command(label="Выход", command=cfg.ROOT.destroy)

        if sys.version.split()[0] != "3.10.9":
            cfg.ROOT.createcommand('tkAboutDialog', self.about_dialog)

        cfg.ROOT.configure(menu=menubar)

    def about_dialog(self):
        try:
            cfg.ROOT.tk.call('tk::mac::standardAboutPanel')
        except Exception:
            print("no dialog panel")

    def about_widget(self):
        win = CWindow()
        made = (
            f'{cfg.APP_NAME} {cfg.APP_VER}'
            '\n\nCreated by Evgeny Loshkarev'
            '\nCopyright © 2023 MIUZ Diamonds.'
            '\nAll rights reserved.'
            '\n\nEmail: evlosh@gmail.com'
            '\nTelegram: evlosh'
            )
        author = CLabel(win, text=made)
        author.pack(pady=(0, 10))
        close_btn = CButton(win, text='Закрыть')
        close_btn.pack()
        close_btn.cmd(lambda e: self.close_cmd(win))

        cfg.ROOT.update_idletasks()
        place_center(win)
        win.deiconify()
        win.wait_visibility()
        win.grab_set_global()

    def close_cmd(self, win: tkinter.Toplevel):
        win.destroy()
        cfg.ROOT.focus_force()