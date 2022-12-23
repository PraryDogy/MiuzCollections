import cfg
from gui import MainGui
from scaner import scaner
from utils import smb_check

def load_all():
    MainGui()
    cfg.ROOT.deiconify()
    if smb_check():
        scaner()

cfg.ROOT.after(1, load_all)

cfg.ROOT.mainloop()
