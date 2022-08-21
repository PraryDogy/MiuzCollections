import tkinter
from tkinter.ttk import Separator

import cfg
from Gallery.Settings import GuiMain as Settings

from .ClmnBtnCmd import Cmd as ClmnCmd
from .GridBtnCmd import Cmd as GridCmd
from .UpdaterGui import Create as UpdaterGui


class Create:
    def __init__(self, bottomFrame):        

        separ = Separator(bottomFrame,orient='horizontal')
        separ.pack(fill='x')

        self.stBar = tkinter.Frame(
            bottomFrame, bg=cfg.BGCOLOR, height=10, pady=5)
        self.stBar.pack(anchor='e')



        settingLabel = tkinter.Label(
            self.stBar, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, text='Настройки')
        settingLabel.pack(side='left')
            
        settingsBtn = tkinter.Label(
            self.stBar, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=7, font=('', 10, ''), text='⚙', padx=5)
        settingsBtn.bind('<Button-1>', lambda event: Settings.Create())
        settingsBtn.pack(side='left')

        rightSettings = tkinter.Frame(self.stBar, bg=cfg.BGCOLOR, width=15)
        rightSettings.pack(side='left')
        
        
        
        updaterLabel = tkinter.Label(
            self.stBar, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, text='Обновить')
        updaterLabel.pack(side='left')
        
        updaterBtn = tkinter.Label(
            self.stBar, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=7, font=('', 10, ''), text='⟲', padx=5)
        updaterBtn.pack(side='left')
        updaterBtn.bind('<Button-1>', lambda event: UpdaterGui())

        rightUpdater = tkinter.Frame(self.stBar, bg=cfg.BGCOLOR, width=15)
        rightUpdater.pack(side='left')     
        
        
        gridLbl = tkinter.Label(
            self.stBar, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, text='Размер фото')
        gridLbl.pack(side='left')

        lessGrid = tkinter.Label(
            self.stBar, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            text='-', width=7, font=('', 10, ''))
        lessGrid.bind('<Button-1>', lambda event: GridCmd(moreless='-'))
        lessGrid.pack(side='left')

        rightLessGrid = tkinter.Frame(self.stBar,width=15,bg=cfg.BGCOLOR)
        rightLessGrid.pack(side='left')
   
        moreGrid = tkinter.Label(
            self.stBar, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            text='+', width=7, font=('', 10, ''))
        moreGrid.bind('<Button-1>', lambda event: GridCmd(moreless='+'))
        moreGrid.pack(side='left')

        rightMore = tkinter.Frame(self.stBar, width=15, bg=cfg.BGCOLOR)
        rightMore.pack(side='left')


        clmnLbl = tkinter.Label(
            self.stBar, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, text='Столбцы')
        clmnLbl.pack(side='left')
        
        clmnLess = tkinter.Label(
            self.stBar, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            text ='-', width=7, font=('', 10, ''))
        clmnLess.bind('<Button-1>', lambda event: ClmnCmd(moreless='-'))
        clmnLess.pack(side='left')

        rightLess = tkinter.Frame(self.stBar, width=15, bg=cfg.BGCOLOR)
        rightLess.pack(side='left')

        clmnMore = tkinter.Label(
            self.stBar, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            text='+', width=7, font=('', 10, ''))
        clmnMore.bind('<Button-1>', lambda event: ClmnCmd(moreless='+'))
        clmnMore.pack(side='left')
        