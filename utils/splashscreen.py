"""
File scaner and database thumbnails updater with gui.
"""

import threading
import tkinter

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

        gui = Gui()
        task = Scan()
        while task.is_alive():
            cfg.ROOT.update()
        gui.destroy()


class Gui(tkinter.Toplevel):
    """
    Loads database checker, smb checker, files scaner and
    database updater.
    """
    def __init__(self):
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.stop)
        self.bind('<Command-w>', lambda e: self.stop())
        self.bind('<Command-q>', lambda e: quit())

        self.title('MiuzGallery')
        self.resizable(0, 0)

        sub_title = MyLabel(self,
                    text=f'Сканирую фото за последние {cfg.FILE_AGE} дней',
                    wraplength=300)
        sub_title.pack(pady=(20, 0))

        dynamic = MyLabel(self, width=40, text='5%')
        dynamic.pack(pady=(0, 20))
        cfg.LIVE_LBL = dynamic

        skip_btn = MyButton(self, text='Пропустить')
        skip_btn.cmd(lambda e: self.stop())
        skip_btn.pack(pady=(0, 10))

        if cfg.ROOT.state() != 'withdrawn':
            place_center(self)
        else:
            cfg.ROOT.eval(f'tk::PlaceWindow {self} center')

        self.deiconify()
        self.grab_set()

    def stop(self):
        """
        Stops threading Scaner and destroys gui.
        """
        cfg.FLAG = False
        self.destroy()


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
