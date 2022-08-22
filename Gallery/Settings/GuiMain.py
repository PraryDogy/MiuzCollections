import os
import sys
import tkinter

import cfg
import sqlalchemy
import tkmacosx
from DataBase.Database import Config, dBase
from Utils.Styled import *


class TkObjects:
    genFrame = tkinter.Frame
    expFrame = tkinter.Frame
    
    genBtn = tkinter.Button
    expBtn = tkinter.Button

    belowMenu = tkinter.Frame


class Create(tkinter.Toplevel):
    def __init__(self):
        """Create tk TopLevel with tkinter.Labels and buttons. 
        Methods: just run class. 
        Imports: ManageDb from DataBase package."""

        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR)

        self.resizable(0,0)
        self.attributes('-topmost', 'true')
        self.title('Настройки')

        frameL = MyFrame(self)
        frameL.pack(side='left', padx=10, pady=10)

        frameR = MyFrame(self)
        frameR.pack(side='right', padx=10, pady=10)

        LeftMenu(frameL).pack()

        General(frameR).pack()
        Expert(frameR)
        
        BelowMenu(frameR).pack(anchor='se')

        cfg.ROOT.eval(f'tk::PlaceWindow {self} center') 


class LeftMenu(MyFrame, TkObjects):
    def __init__(self, master):
        super().__init__(master)

        genBtn = MyButton(
            self, lambda event: self.CloseExp(), 'Основные')
        genBtn.configure(bg=cfg.BGPRESSED)
        genBtn.pack()

        expertBtn = MyButton(
            self, lambda event: self.CloseGen(), 'Эксперт')
        expertBtn.pack()

        TkObjects.genBtn = genBtn
        TkObjects.expBtn = expertBtn
        
    def CloseGen(self):
        TkObjects.genFrame.pack_forget()
        TkObjects.belowMenu.pack_forget()
        
        TkObjects.expBtn.configure(bg=cfg.BGPRESSED)
        TkObjects.genBtn.configure(bg=cfg.BGBUTTON)
        
        TkObjects.expFrame.pack(expand=True, fill='both')
        TkObjects.belowMenu.pack()
        

    def CloseExp(self):
        TkObjects.expFrame.pack_forget()
        TkObjects.belowMenu.pack_forget()
        
        TkObjects.genBtn.configure(bg=cfg.BGPRESSED)
        TkObjects.expBtn.configure(bg=cfg.BGBUTTON)
        
        TkObjects.genFrame.pack()
        TkObjects.belowMenu.pack()
        
        
class BelowMenu(MyFrame, TkObjects):
    def __init__(self, master):
        super().__init__(master)
        TkObjects.belowMenu = self
        
        buttonOk = MyButton(
            self, lambda event: self.winfo_toplevel().destroy(), 'Ok')
        buttonOk.pack(side='left', padx=10)

        buttonCancel = MyButton(
            self, lambda event: self.winfo_toplevel().destroy(), 'Cancel')
        buttonCancel.pack(side='left')
        

class General(MyFrame, TkObjects):
    def __init__(self, master):
        super().__init__(master)
        TkObjects.genFrame = self

        descr = (
            'При запуске программа сканирует и обновляет фото'
            f'\nза последние {cfg.FILE_AGE} дней.'
            
            '\n\nНажмите "Обновить", чтобы обновить фотографии'
            '\nтекущей коллекции за все время с 2018 года.'
            
            '\n\nНажмите "Полное сканирование", чтобы обновить все'
            '\nфотографии за все время c 2018 года.'
            )
        
        descrLabel = MyLabel(self)
        descrLabel.config(anchor='w', padx=5, text=descr, justify='left')
        descrLabel.pack(fill='x')

        scanBtn = MyButton(
            self, lambda event: self.RunScan(), 'Полное сканирование')
        scanBtn.pack(anchor='center', pady=10)
        
        belowBtn = MyFrame(self)
        belowBtn.configure(height=10)
        belowBtn.pack()
        

    def RunScan(self):
        query = sqlalchemy.update(Config).where(
            Config.name=='typeScan').values(value='full')
        dBase.conn.execute(query)
        os.execv(sys.executable, ['python'] + sys.argv)


class Expert(tkmacosx.SFrame, TkObjects):
    def __init__(self, master):
        super().__init__(master)
        
        self.configure(bg=cfg.BGCOLOR, scrollbarwidth=10)
        self.configure(avoidmousewheel=(self))
        
        TkObjects.expFrame = self
        
        
        for i in range(0, 10):
            l = tkinter.Label(self, width=10, height=10, text='hello')
            l.pack(pady=5)
        
        h = int(cfg.ROOT.winfo_screenheight()*0.5)
        self.configure(height=h)
