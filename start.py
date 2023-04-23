import cfg
from gui import Gui
from scaner import scaner
from utils import smb_check
from gui.widgets import SmbAlert

def load_all():
    Gui()
    cfg.ROOT.deiconify()
    if smb_check():
        scaner()
    else:
        SmbAlert()

cfg.ROOT.after(1, load_all)

cfg.ROOT.mainloop()
