"""
This is general gui with all elements.
"""

import tkinter

import cfg
from utils import MySep

from .ask_exit import AskExit
from .bar_menu import BarMenu
from .images_gui import Gallery
from .status_bar import StatusBar
from functools import partial

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
        cfg.ROOT.createcommand("tk::mac::Quit" , partial(AskExit, cfg.ROOT))
        if cfg.config['MINIMIZE']:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", lambda: cfg.ROOT.withdraw())
        else:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", partial(AskExit, cfg.ROOT))
        MySep(cfg.ROOT).pack(fill=tkinter.X, pady=(30, 20))
        Gallery(cfg.ROOT).pack(fill=tkinter.BOTH, expand=True)
        MySep(cfg.ROOT).pack(fill=tkinter.X, pady=10)
        StatusBar(cfg.ROOT).pack(pady=(0, 10))
        BarMenu()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')
        w, h, x, y = cfg.config['GEOMETRY']
        cfg.ROOT.geometry(f'{w}x{h}+{x}+{y}')