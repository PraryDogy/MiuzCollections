import threading
import tkinter

import cfg
import sqlalchemy
from DataBase.Database import Config, dBase

from .Scaner import *
from .Styled import *
from .Utils import DbCkecker, SmbChecker


class SplashScreen(tkinter.Toplevel):
    def __init__(self):
        """Loads database checker, smb checker, files scaner and
        database updater.
        Methods: just run init."""
        
        DbCkecker().Check()
        
        if not SmbChecker().Check():
            return
        
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR)
        self.withdraw()
        self.Run()
                
    def Scan(self):
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

    def Skip(self):
        """Destroys tkinter topLevel window and set cfg.FLAF to False."""
        
        self.withdraw()
        self.destroy()
        cfg.FLAG = False
    
    def Run(self):        
        self.Gui()
        scanTask = threading.Thread(target=lambda: self.Scan())
        scanTask.start()
        while scanTask.is_alive(): cfg.ROOT.update()
        self.destroy()

    def Gui(self):
        self.title('MiuzGallery')
        self.resizable(0, 0)
        cfg.ROOT.createcommand('tk::mac::ReopenApplication', self.deiconify)
        
        subTitle = MyLabel(self, 
            text=f'Сканирую фото за последние {cfg.FILE_AGE} дней',
            wraplength=300)
        subTitle.pack(pady=(20, 0))
        
        dynamic = MyLabel(self, width=40, text='90%')
        dynamic.pack(pady=(0, 20))
        cfg.LIVE_LBL = dynamic

        skipBtn = MyButton(self, text='Пропустить')
        skipBtn.pack(pady=(0, 10))
             
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.deiconify()
