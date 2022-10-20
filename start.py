"""
Run file
"""

import cfg
from gui import main_gui
from utils.scaner import Scaner


def load_all():
    """
    Loads splashscreen with thumbnails updater first.≥
    Then loads main gui with thumbnails.
    """
    main_gui.MainGui()
    cfg.ROOT.deiconify()
    Scaner()

cfg.ROOT.after(1, load_all)

cfg.ROOT.mainloop()
