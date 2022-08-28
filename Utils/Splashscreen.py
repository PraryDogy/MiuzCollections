import threading
import tkinter

import cfg
import sqlalchemy
from DataBase.Database import Config, dBase

from .Scaner import *
from .Styled import *
from .Utils import DbCkecker, SmbChecker


class SplashScreen:
    def __init__(self):
        """Creates toplevel window and run Scaner from utils.
        Destroys automaticaly when Scaner done"""
        
        DbCkecker().Check()
        if not SmbChecker().Check():
            return

        gui = Gui()
        task = Scan()
        while task.is_alive(): cfg.ROOT.update()
        gui.destroy()
        cfg.TOP_LVL = False
    

class Gui(tkinter.Toplevel):
    def __init__(self):
        """Loads database checker, smb checker, files scaner and
        database updater.
        Methods: just run init."""        
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR)
        self.withdraw()
        self.attributes('-topmost', 'true')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.Gui()         

    def on_closing(self):
        cfg.TOP_LVL = False
        cfg.FLAG = False
        self.destroy()
        
    def Skip(self):
        """Destroys tkinter topLevel window and set cfg.FLAG to False."""
        
        self.withdraw()
        self.destroy()
        cfg.FLAG = False

    def Gui(self):
        self.title('MiuzGallery')
        self.resizable(0, 0)
        cfg.ROOT.createcommand('tk::mac::ReopenApplication', self.deiconify)
        
        subTitle = MyLabel(self, 
            text=f'Сканирую фото за последние {cfg.FILE_AGE} дней',
            wraplength=300)
        subTitle.pack(pady=(20, 0))
        
        dynamic = MyLabel(self, width=40, text='5%')
        dynamic.pack(pady=(0, 20))
        cfg.LIVE_LBL = dynamic

        skipBtn = MyButton(self, text='Пропустить')
        skipBtn.Cmd(lambda e: self.Skip())
        skipBtn.pack(pady=(0, 10))
             
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.deiconify()


class Scan(threading.Thread):
    def __init__(self):
        """Scan files & update db with threading.
        Just run init."""
        
        threading.Thread.__init__(self, target=self.__Scan)
        self.start()
        
    def __Scan(self):
        """Run Utils files scan & database update."""
        
        cfg.FLAG = True
        
        selectType = sqlalchemy.select(Config.value).where(
            Config.name=='typeScan')
        typeScan = dBase.conn.execute(selectType).first()[0]
        
        CollsUpd().CollsUpd()
        if typeScan == 'full':

            updateType = sqlalchemy.update(Config).where(
                Config.name=='typeScan').values(value='')
            dBase.conn.execute(updateType)
            RtUpd().RtUpd()
            return
        
        RtUpd().RtAgedUpd()
