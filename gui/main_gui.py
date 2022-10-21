"""
This is general gui with all elements.
"""

import json
import os
import tkinter
from tkinter.ttk import Separator

import cfg

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
        cfg.ROOT.createcommand("tk::mac::Quit" , self.on_exit)
        cfg.ROOT.bind('<Command-w>', lambda e: cfg.ROOT.iconify())
        cfg.ROOT.protocol("WM_DELETE_WINDOW", self.on_exit)

        Separator(cfg.ROOT, orient='horizontal').pack(
            fill=tkinter.X, pady=(30, 20))
        Gallery(cfg.ROOT).pack(fill=tkinter.BOTH, expand=True,)
        Separator(cfg.ROOT, orient='horizontal').pack(fill=tkinter.X, pady=10)
        StatusBar(cfg.ROOT).pack(
            pady=(0, 10), side=tkinter.RIGHT)

        BarMenu()

        cfg.ROOT.update_idletasks()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')

        cfg.ROOT.geometry(f'{cfg.config["ROOT_SIZE"]}{cfg.config["ROOT_POS"]}')

    def on_exit(self):
        cfg.FLAG = False

        cfg.ROOT.update_idletasks()
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()

        cfg.config['ROOT_SIZE'] = f'{w}x{h}'
        cfg.config['ROOT_POS'] = f'+{x}+{y}'

        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(cfg.config, file, indent=4,)
        
        quit()
