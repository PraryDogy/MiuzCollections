import cfg
from gui import InitGui
from scaner import scaner
from utils import smb_check
from gui.widgets import SmbAlert

def load_all():
    InitGui()
    cfg.ROOT.deiconify()
    if smb_check():
        scaner()
    else:
        SmbAlert()

cfg.ROOT.after(1, load_all)

cfg.ROOT.mainloop()
