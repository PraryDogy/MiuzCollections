"""
Run file
"""

import cfg
from gui import main_gui
from utils.splashscreen import SplashScreen
from gui.images_gui import Globals


def load_all():
    """
    Loads splashscreen with thumbnails updater first.
    Then loads main gui with thumbnails.
    """
    main_gui.MainGui()
    cfg.ROOT.deiconify()
    SplashScreen()
    Globals.images_reset()

cfg.ROOT.after(1, load_all)

cfg.ROOT.mainloop()
