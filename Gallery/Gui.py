import tkinter

import cfg
from Utils.Utils import *

from .ImgGrid.Gui import Create as ImgGrigGui
from .Menu.Gui import Create as MenuGui
from .MenuBar import Create as MenuBar
from .StatusBar import StatusBar


class Create:
    def __init__(self):
        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', cfg.ROOT.deiconify)
        
        cfg.ROOT.title('MiuzGallery')
        cfg.ROOT.configure(bg=cfg.BGCOLOR, padx=15, pady=0)
        cfg.ROOT.bind('<Command-w>', lambda event: cfg.ROOT.iconify())

        cfg.UP_FRAME = tkinter.Frame(cfg.ROOT, bg=cfg.BGCOLOR)
        cfg.UP_FRAME.pack(fill='both', expand=True)
        
        MenuGui()
        ImgGrigGui()
        StatusBar()
        MenuBar()

        cfg.ROOT.update_idletasks()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')
        
        x = cfg.ROOT.winfo_x()
        y = 0
        w = cfg.ROOT.winfo_width()
        h = int(cfg.ROOT.winfo_screenheight()*0.8)
        
        cfg.ROOT.geometry(f'{w}x{h}+{x}+{y}')
        