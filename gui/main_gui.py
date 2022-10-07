"""
This is general gui with all elements.
"""

import tkinter
from tkinter.ttk import Separator

import cfg

from .images_gui import Gallery
from .bar_menu import BarMenu
from .status_bar import StatusBar


def unhide():
    cfg.ROOT.deiconify()



class MainGui:
    """
    Configures root window.
    Loads images_gui, status_bar and mac osx menu_bar.
    """
    def __init__(self):
        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', unhide)

        cfg.ROOT.title('MiuzGallery')
        cfg.ROOT.configure(bg=cfg.BGCOLOR, padx=15, pady=0)
        cfg.ROOT.bind('<Command-w>', lambda e: cfg.ROOT.iconify())

        Separator(cfg.ROOT, orient='horizontal').pack(
            fill=tkinter.X, pady=(30, 20))
        Gallery(cfg.ROOT).pack(fill=tkinter.BOTH, expand=True,)
        Separator(cfg.ROOT, orient='horizontal').pack(fill=tkinter.X, pady=10)
        StatusBar(cfg.ROOT).pack(pady=(0, 10))

        BarMenu()

        cfg.ROOT.update_idletasks()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')

        x = cfg.ROOT.winfo_x()
        y = 0
        w = cfg.ROOT.winfo_width()
        h = int(cfg.ROOT.winfo_screenheight()*0.8)

        cfg.ROOT.geometry(f'{w}x{h}+{x}+{y}')
