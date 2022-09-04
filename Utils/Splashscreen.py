"""
File scaner and database thumbnails updater with gui.
"""

import threading
import tkinter

import cfg
import sqlalchemy
from database import Config, Dbase

from utils import Utils, Styled


class SplashScreen:
    """
    Creates tkinter toplevel window and run Scaner from utils.
    Destroys gui automaticaly when Scaner is done.
    """
    def __init__(self):
        if not Utils.SmbChecker().check():
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
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.stop)
        self.title('MiuzGallery')
        self.resizable(0, 0)
        cfg.ROOT.createcommand('tk::mac::ReopenApplication', self.deiconify)

        sub_title = Styled.MyLabel(self,
                    text=f'Сканирую фото за последние {cfg.FILE_AGE} дней',
                    wraplength=300)
        sub_title.pack(pady=(20, 0))

        dynamic = Utils.Styled.MyLabel(self, width=40, text='5%')
        dynamic.pack(pady=(0, 20))
        cfg.LIVE_LBL = dynamic

        skip_btn = Utils.Styled.MyButton(self, text='Пропустить')
        skip_btn.Cmd(lambda e: self.stop())
        skip_btn.pack(pady=(0, 10))

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

        Utils.Scaner.UpdateColl()

        if type_scan == 'full':
            Dbase.conn.execute(sqlalchemy.update(Config).where(
                Config.name=='typeScan').values(value=''))

            Utils.Scaner.UpdateRt(aged=False)
            return

        Utils.Scaner.UpdateRt(aged=True)
