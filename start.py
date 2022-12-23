import cfg
from gui import InitGui
from scaner import scaner
from utils import smb_check

def load_all():
    InitGui()
    cfg.ROOT.deiconify()
    if smb_check():
        scaner()

cfg.ROOT.after(1, load_all)

cfg.ROOT.mainloop()
