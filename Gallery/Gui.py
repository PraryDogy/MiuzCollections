import tkinter

import cfg
from Utils.Utils import *

from .Gallery import Gallery
from .MenuBar import Create as MenuBar
from .StatusBar import StatusBar
from tkinter.ttk import Separator

class Create:
    def __init__(self):
        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', cfg.ROOT.deiconify)
        
        cfg.ROOT.title('MiuzGallery')
        cfg.ROOT.configure(bg=cfg.BGCOLOR, padx=15, pady=0)
        cfg.ROOT.bind('<Command-w>', lambda e: cfg.ROOT.iconify())
        
        Gallery(cfg.ROOT).pack(fill=tkinter.BOTH, expand=True)
        Separator(cfg.ROOT, orient='horizontal').pack(fill=tkinter.X, pady=10)
        StatusBar(cfg.ROOT).pack(pady=(0, 10))
        
        MenuBar()

        cfg.ROOT.update_idletasks()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')
        
        x = cfg.ROOT.winfo_x()
        y = 0
        w = cfg.ROOT.winfo_width()
        h = int(cfg.ROOT.winfo_screenheight()*0.8)
        
        cfg.ROOT.geometry(f'{w}x{h}+{x}+{y}')
        