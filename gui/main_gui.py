"""
This is general gui with all elements.
"""

import tkinter
from tkinter.ttk import Separator

import cfg

from .ask_exit import AskExit
from .bar_menu import BarMenu
from .images_gui import Gallery
from .status_bar import StatusBar


class MainGui:
    """
    Configures root window.
    Loads images_gui, status_bar and mac osx menu_bar.
    """
    def __init__(self):
        cfg.ROOT.title('MiuzGallery')
        cfg.ROOT.configure(bg=cfg.BGCOLOR, padx=15, pady=0)

        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', lambda: cfg.ROOT.deiconify())
        cfg.ROOT.bind('<Command-w>', lambda e: cfg.ROOT.withdraw())
        cfg.ROOT.createcommand("tk::mac::Quit" , self.on_exit)
        cfg.ROOT.protocol("WM_DELETE_WINDOW", self.on_exit)

        Separator(cfg.ROOT, orient='horizontal').pack(
            fill=tkinter.X, pady=(30, 20))

        Gallery(cfg.ROOT).pack(fill=tkinter.BOTH, expand=True)

        Separator(cfg.ROOT, orient='horizontal').pack(fill=tkinter.X, pady=10)
        
        StatusBar(cfg.ROOT).pack(pady=(0, 10))

        BarMenu()

        cfg.ROOT.update_idletasks()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')

        cfg.ROOT.geometry(f'{cfg.config["ROOT_SIZE"]}{cfg.config["ROOT_POS"]}')

    def on_exit(self):
        AskExit(cfg.ROOT)
