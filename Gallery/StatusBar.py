from tkinter.messagebox import NO
from tkinter.ttk import Separator

import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Gallery.Settings import Gui as Settings
from Utils.Splashscreen import SplashScreen
from Utils.Styled import *
from Utils.Utils import ReloadGallery


class BtnCmd:
    def OpenSettings(self, btn=MyButton):
        if cfg.TOP_LVL:
            return
        btn.Press()
        cfg.TOP_LVL = True
        Settings.Create()

    def Update(self, btn=MyButton):
        if cfg.TOP_LVL:
            return
        btn.Press()
        cfg.TOP_LVL = True
        SplashScreen()
        ReloadGallery()
        
    def MoreLess(self, delta, min, max, dbName):
        query = sqlalchemy.select(Config.value).where(Config.name==dbName)
        size = int(dBase.conn.execute(query).first()[0])
        
        size = size + delta
        size = min if size < min else size
        size = max if size > max else size
        
        query = sqlalchemy.update(Config).where(
            Config.name==dbName).values(value=str(size))
        dBase.conn.execute(query)
        ReloadGallery()


class StatusBar(MyFrame, BtnCmd):
    def __init__(self):        

        separ = Separator(cfg.ROOT,orient='horizontal')
        separ.pack(fill='x', pady=10)

        super().__init__(cfg.ROOT)
        self.pack(anchor='e', pady=(0, 10))

        settingLabel = MyLabel(self, text='Настройки')
        settingLabel.pack(side='left')
            
        settBtn = MyButton(self, text='⚙', padx=5)
        settBtn.configure(width=5, height=1)
        settBtn.Cmd(lambda event: self.OpenSettings(settBtn))
        settBtn.pack(side='left', padx=(0, 15))
        
        
        updLabel = MyLabel(self, text='Обновить')
        updLabel.pack(side='left')
        
        updBtn = MyButton(self, text='⟲', padx=5)
        updBtn.configure(width=5, height=1, )
        updBtn.Cmd(lambda event: self.Update(updBtn))
        updBtn.pack(side='left', padx=(0, 15))

        
        gridLbl = MyLabel(self, text='Размер фото')
        gridLbl.pack(side='left')

        lessGrid = MyButton(self, text='-', padx=5)
        lessGrid.configure(width=5, height=1, )
        lessGrid.Cmd(
            lambda event: self.MoreLess(-50, 150, 300, 'size'))
        lessGrid.pack(side='left', padx=(0, 15))

        moreGrid = MyButton(self, text='+', padx=5)
        moreGrid.configure(width=5, height=1, )
        moreGrid.Cmd(
            lambda event: self.MoreLess(+50, 150, 300, 'size'))
        moreGrid.pack(side='left', padx=(0, 15))


        clmnLbl = MyLabel(self, text='Столбцы')
        clmnLbl.pack(side='left')
    
        lessGrid = MyButton(self, text='-', padx=5)
        lessGrid.configure(width=5, height=1, )
        lessGrid.Cmd(
            lambda event: self.MoreLess(-1, 1, 10, 'clmns'))
        lessGrid.pack(side='left', padx=(0, 15))

        moreGrid = MyButton(self, text='+', padx=5)
        moreGrid.configure(width=5, height=1, )
        moreGrid.Cmd(
            lambda event: self.MoreLess(+1, 1, 10, 'clmns'))
        moreGrid.pack(side='left', padx=(0, 15))


