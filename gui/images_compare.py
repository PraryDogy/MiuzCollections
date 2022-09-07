import tkinter
import cfg


class ImagesCompare(tkinter.Toplevel):
    def __init__(self):
        tkinter.Toplevel.__init__(self)

        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        
        side = int(cfg.ROOT.winfo_screenheight()*0.8)

        