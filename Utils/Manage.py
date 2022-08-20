import tkinter

import cfg
from Gallery.ImgGrid.Gui import Create as ImgGridGui


def ReloadGallery():
    upFrame = cfg.ROOT.winfo_children()[0]
    scrollable = upFrame.winfo_children()[1]
    scrollable.destroy()

    imgFrame = tkinter.Frame(upFrame, bg=cfg.BGCOLOR)
    imgFrame.pack(side='left', fill='both', expand=True)
    ImgGridGui(imgFrame)


def Geometry():
    cfg.ROOT.update_idletasks()
    
    for i in cfg.ROOT.winfo_children():
        if i.winfo_name()=='!frame':
            w = i.winfo_reqwidth()            
            break
        
    h = int(cfg.ROOT.winfo_screenheight()*0.8)
    
    cfg.ROOT.geometry(f'{w}x{h}')
