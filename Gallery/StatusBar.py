import cfg
import sqlalchemy
from database import Config, Dbase
from Utils.Splashscreen import SplashScreen
from Utils.Styled import MyButton, MyFrame, MyLabel

from .SettingsWin import Settings

from .images_gui import Globals
import tkinter

class BtnCmd:
    def OpenSettings(self, btn=MyButton):
        if cfg.TOP_LVL:
            return
        btn.Press()
        cfg.TOP_LVL = True
        Settings()

    def Update(self, btn=MyButton):
        if cfg.TOP_LVL:
            return
        btn.Press()
        cfg.TOP_LVL = True
        SplashScreen()
        Globals.images_reset()
        
    def MoreLess(self, delta, min, max, dbName):
        query = sqlalchemy.select(Config.value).where(Config.name==dbName)
        size = int(Dbase.conn.execute(query).first()[0])
        
        size = size + delta
        size = min if size < min else size
        size = max if size > max else size
        
        query = sqlalchemy.update(Config).where(
            Config.name==dbName).values(value=str(size))
        Dbase.conn.execute(query)
        Globals.images_reset()


class StatusBar(MyFrame, BtnCmd):
    def __init__(self, master):                
        MyFrame.__init__(self, master)
        
        SettingsSection(self)
        UpdateSection(self)
        GridSection(self)
        ClmnSection(self)
        
        
class SettingsSection(MyLabel, MyButton, BtnCmd):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Настройки')
        self.pack(side=tkinter.LEFT)
                 
        MyButton.__init__(self, master, text='⚙', padx=5)
        self.configure(width=5, height=1)
        self.Cmd(lambda e: self.OpenSettings(self))
        self.pack(side=tkinter.LEFT, padx=(0, 15))
                

class UpdateSection(MyLabel, MyButton, BtnCmd):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Обновить')
        self.pack(side=tkinter.LEFT)
        
        MyButton.__init__(self, master, text='⟲', padx=5)
        self.configure(width=5, height=1, )
        self.Cmd(lambda e: self.Update(self))
        self.pack(side=tkinter.LEFT, padx=(0, 15))


class GridSection(MyLabel, MyButton, BtnCmd):
    def __init__(self, master):
        
        MyLabel.__init__(self, master, text='Размер фото')
        self.pack(side=tkinter.LEFT)

        MyButton.__init__(self, master, text='-', padx=5)
        self.configure(width=5, height=1)
        self.Cmd(
            lambda e: self.MoreLess(-50, 150, 300, 'size'))
        self.pack(side=tkinter.LEFT, padx=(0, 15))

        MyButton.__init__(self, master, text='+', padx=5)
        self.configure(width=5, height=1, )
        self.Cmd(
            lambda e: self.MoreLess(+50, 150, 300, 'size'))
        self.pack(side=tkinter.LEFT, padx=(0, 15))


class ClmnSection(MyLabel, MyButton, BtnCmd):
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Столбцы')
        self.pack(side=tkinter.LEFT)
    
        MyButton.__init__(self, master, text='-', padx=5)
        self.configure(width=5, height=1, )
        self.Cmd(
            lambda e: self.MoreLess(-1, 1, 10, 'clmns'))
        self.pack(side=tkinter.LEFT, padx=(0, 15))

        MyButton.__init__(self, master, text='+', padx=5)
        self.configure(width=5, height=1, )
        self.Cmd(
            lambda e: self.MoreLess(+1, 1, 10, 'clmns'))
        self.pack(side=tkinter.LEFT, padx=(0, 15))

