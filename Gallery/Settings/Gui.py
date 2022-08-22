import json
import os
import sys
import tkinter

import cfg
import sqlalchemy
import tkmacosx
from DataBase.Database import Config, dBase
from Utils.Styled import *
from Utils.ClipBoard import *

from .Descriptions import descriptions


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
        self.geometry(f'570x650')
        self.configure(padx=10, pady=10)
        
        
        frameUp = MyFrame(self)
        frameUp.pack(fill='both', expand=True)

        frameB = MyFrame(self)
        frameB.pack()

        LeftMenu(frameUp).pack(side='left', padx=(0, 10))

        General(frameUp).pack()
        Expert(frameUp)
        
        BelowMenu(frameB).pack(pady=(10,0))

        cfg.ROOT.update_idletasks()
        x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
        xx = x + int(cfg.ROOT.winfo_width()/2)-int(self.winfo_width()/2)
        yy = y + int(cfg.ROOT.winfo_height()/2)-int(self.winfo_height()/2)

        self.geometry(f'+{xx}+{yy}')


class LeftMenu(MyFrame, TkObjects):
    def __init__(self, master):
        super().__init__(master)
        genBtn = MyButton(
            self, 
            lambda event: self.Change(
                TkObjects.expFrame, TkObjects.genFrame,
                TkObjects.genBtn, TkObjects.expBtn), 
            'Основные')
        genBtn.configure(bg=cfg.BGPRESSED)
        genBtn.pack()

        expertBtn = MyButton(
            self, 
            lambda event: self.Change(
                TkObjects.genFrame, TkObjects.expFrame,
                TkObjects.expBtn, TkObjects.genBtn),
            'Эксперт')
        expertBtn.pack()

        TkObjects.genBtn = genBtn
        TkObjects.expBtn = expertBtn
        
    def Change(self, frameForget, framePack, btnPress, btnUnpress):
        frameForget.pack_forget()
        framePack.pack(fill='both', expand=True)

        btnPress.configure(bg=cfg.BGPRESSED)
        btnUnpress.configure(bg=cfg.BGBUTTON)

        
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
        descrLabel.pack()

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
        
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)

        
        labelsInserts = list()
        insterts = list()
        
        for key, value in data.items():
            
            desrc = MyLabel(self)
            desrc.pack(anchor='w', pady=(30, 0))
            labelsInserts.append(desrc)
            
            ins = tkinter.Entry(
                self, 
                bg=cfg.BGBUTTON, 
                fg=cfg.FONTCOLOR,
                insertbackground=cfg.FONTCOLOR,
                selectbackground=cfg.BGPRESSED,
                highlightthickness=0,
                bd=0,
                justify='center'
                )
            ins.insert(0, value)
            ins.pack(fill='x', pady=(0, 5), padx=(0, 10), ipady=3)
            insterts.append(ins)
            
            frameBtns = MyFrame(self)
            frameBtns.pack()
            
            btnCopy = MyButton(frameBtns, '', 'Копировать')
            btnCopy.configure(height=1, width=9)
            btnCopy.bind(
                '<Button-1>', 
                lambda event, ins=ins, btn=btnCopy: self.CopyIns(ins, btn)
                )
            btnCopy.pack(side='left', padx=(0, 10))
            
            btnPaste = MyButton(frameBtns, '', 'Вставить')
            btnPaste.configure(height=1, width=9)
            btnPaste.bind(
                '<Button-1>', 
                lambda event, ins=ins, btn=btnPaste: self.PasteIns(ins, btn)
                )
            btnPaste.pack(side='right', padx=(0, 10))
            
        for a, b in zip(labelsInserts, descriptions):
            a.configure(text=b, justify='left', wraplength=340)

    def CopyIns(self, ins, btn):
        btn.configure(bg=cfg.BGPRESSED)
        text = ins.get()
        copy(text)
        cfg.ROOT.after(100, lambda: btn.configure(bg=cfg.BGBUTTON))
    
    def PasteIns(self, ins, btn):
        btn.configure(bg=cfg.BGPRESSED)
        text = paste()
        ins.delete(0, 'end')
        ins.insert(0, text)
        cfg.ROOT.after(100, lambda: btn.configure(bg=cfg.BGBUTTON))
