import sys
import tkinter

import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Utils.Manage import Geometry

from .ImgGrid.Gui import Create as ImgGrigGui
from .Menu.Gui import Create as MenuGui
from .MenuBar import Create as MenuBar
from .StatusBar.Gui import Create as StatusBar


class Create:
    def __init__(self):
        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', cfg.ROOT.deiconify)
        
        cfg.ROOT.title('MiuzGallery')
        cfg.ROOT.config(bg=cfg.BGCOLOR, padx=15, pady=0)

        upFrame = tkinter.Frame(cfg.ROOT, bg=cfg.BGCOLOR)
        upFrame.pack(fill='both', expand=True)

        bottomFrame = tkinter.Frame(cfg.ROOT, bg=cfg.BGCOLOR)
        bottomFrame.pack(fill='x')

        menuFrame = tkinter.Frame(upFrame, bg=cfg.BGCOLOR)
        menuFrame.pack(side='left')
        MenuGui(menuFrame)
        
        imgFrame = tkinter.Frame(upFrame, bg=cfg.BGCOLOR)
        imgFrame.pack(side='left', fill='both', expand=True)
        ImgGrigGui(imgFrame)
        
        StatusBar(bottomFrame)
        MenuBar()

        Geometry()
        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')
        cfg.ROOT.geometry(f'+{cfg.ROOT.winfo_x()}+0')
