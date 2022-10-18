"""
File scaner and database thumbnails updater with gui.
"""

import threading

import cfg
import sqlalchemy
from database import Config, Dbase

from .scaner import UpdateCollections, UpdateRetouched
from .utils import MyButton, MyLabel, SmbChecker, place_center


class SplashScreen:
    """
    Creates tkinter toplevel window and run Scaner from utils.
    Destroys gui automaticaly when Scaner is done.
    """
    def __init__(self):
        if not SmbChecker().check():
            return

        task = Scan()
        while task.is_alive():
            cfg.ROOT.update()

        cfg.IMAGES_RESET()

class Scan(threading.Thread):
    """
    Scans files and updates database thumbnails with Scaner from utils.
    """
    def __init__(self):
        threading.Thread.__init__(self, target=self.__scan)
        self.start()

    def __scan(self):
        """Run Files Scaner & Database Updater from utils"""

        cfg.FLAG = True

        type_scan = Dbase.conn.execute(sqlalchemy.select(Config.value).where(
            Config.name=='typeScan')).first()[0]

        UpdateCollections()

        if type_scan == 'full':
            Dbase.conn.execute(sqlalchemy.update(Config).where(
                Config.name=='typeScan').values(value=''))

            UpdateRetouched(aged=False)
            return

        UpdateRetouched(aged=True)
