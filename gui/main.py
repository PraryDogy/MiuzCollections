import tkinter

import cfg

from .macosx_menu import BarMenu
from .widgets import AskExit, CSep
from .gallery import Gallery
from .st_bar import StatusBar


class MainGui:
    """
    Configures root window.
    Loads images_gui, status_bar and mac osx menu_bar.
    """
    def __init__(self):
        cfg.ROOT.title('MiuzGallery')
        cfg.ROOT.configure(bg=cfg.BGCOLOR)

        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', lambda: cfg.ROOT.deiconify())
        cfg.ROOT.createcommand("tk::mac::Quit" , AskExit)

        cfg.ROOT.bind('<Command-w>', lambda e: cfg.ROOT.withdraw())

        if cfg.config['MINIMIZE'] == 1:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", lambda: cfg.ROOT.withdraw())
        else:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", AskExit)

        CSep(cfg.ROOT).pack(fill=tkinter.X, pady=15)
        Gallery(cfg.ROOT).pack(fill=tkinter.BOTH, expand=1)
        CSep(cfg.ROOT).pack(fill=tkinter.X, pady=10)
        StatusBar(cfg.ROOT).pack(pady=(0, 10))
        
        BarMenu()

        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')
        w, h, x, y = cfg.config['GEOMETRY']
        cfg.ROOT.geometry(f'{w}x{h}+{x}+{y}')
