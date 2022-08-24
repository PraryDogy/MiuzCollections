import tkinter

import cfg
from Utils.Utils import *

from .ImgGrid.Gui import Create as ImgGrigGui
from .Menu.Gui import Create as MenuGui
from .MenuBar import Create as MenuBar
from .StatusBar.Gui import Create as StatusBar


class Create:
    def __init__(self):
        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', cfg.ROOT.deiconify)
        
        cfg.ROOT.title('MiuzGallery')
        cfg.ROOT.configure(bg=cfg.BGCOLOR, padx=15, pady=0)

        upFrame = tkinter.Frame(cfg.ROOT, bg=cfg.BGCOLOR)
        upFrame.pack(fill='both', expand=True)
        cfg.UPFRAME = upFrame
        
        bottomFrame = tkinter.Frame(cfg.ROOT, bg=cfg.BGCOLOR)
        bottomFrame.pack(fill='x')

        menuLeft = tkinter.Frame(upFrame, bg=cfg.BGCOLOR)
        menuLeft.pack(side='left')
        MenuGui(menuLeft)
        
        imgGridRight = tkinter.Frame(upFrame, bg=cfg.BGCOLOR)
        imgGridRight.pack(side='left', fill='both', expand=True)
        cfg.IMG_GRID = imgGridRight
        ImgGrigGui()
        
        StatusBar(bottomFrame)
        MenuBar()

        cfg.ROOT.update_idletasks()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')
        
        x = cfg.ROOT.winfo_x()
        y = 0
        w = cfg.ROOT.winfo_width()
        h = int(cfg.ROOT.winfo_screenheight()*0.8)
        
        cfg.ROOT.geometry(f'{w}x{h}+{x}+{y}')
        