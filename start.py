import cfg
from gui import gui
from scaner import scaner
from utils import smb_check

def load_all():
    gui()
    cfg.ROOT.deiconify()
    if smb_check():
        scaner()

cfg.ROOT.after(1, load_all)

cfg.ROOT.mainloop()
