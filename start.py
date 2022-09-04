"""
Run file
"""

import cfg
from gui import main_gui
from utils.splashscreen import SplashScreen


def load_all():
    """
    Loads splashscreen with thumbnails updater first.
    Then loads main gui with thumbnails.
    """
    SplashScreen()
    main_gui.MainGui()
    cfg.ROOT.deiconify()


cfg.ROOT.after(1, load_all)
cfg.ROOT.mainloop()

