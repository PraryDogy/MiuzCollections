import json
import os
import sys
import tkinter
from tkinter.ttk import Separator

import cfg
import sqlalchemy
import tkmacosx
from DataBase.Database import Config, dBase
from PIL import Image, ImageOps, ImageTk
from Utils.ClipBoard import *
from Utils.Styled import *

from .Descriptions import descriptions


class TkObjects:
    
    genFrame = tkinter.Frame
    expFrame = tkinter.Frame
    genBtn = tkinter.Button
    expBtn = tkinter.Button
    belowMenu = tkinter.Frame
    inserts = list()


class Create(tkinter.Toplevel):
    def __init__(self):
        """Create tk TopLevel with tkinter.Labels and buttons. 
        Methods: just run class. 
        Imports: ManageDb from DataBase package."""

        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        
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

        General(frameUp).pack(fill='both', expand=True)
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
            self, lambda event: self.saveIns(), 'Сохранить')
        buttonOk.pack(side='left', padx=10)

        buttonCancel = MyButton(
            self, lambda event: self.winfo_toplevel().destroy(), 'Отмена')
        buttonCancel.pack(side='left')
    
    def saveIns(self):
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)

        try:
            newValues = [i.get() for i in TkObjects.inserts]
            for key, ins in zip(data, newValues):
                data[key] = ins
            with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
                json.dump(data, file, indent=4)
            self.winfo_toplevel().destroy()
        
        except tkinter.TclError:
            self.winfo_toplevel().destroy()

        
class General(MyFrame, TkObjects):
    def __init__(self, master):
        super().__init__(master)
        TkObjects.genFrame = self
        
        txt1 = (
            'При запуске программа сканирует и обновляет фото'
            f'\nвсех коллекций за последние {cfg.FILE_AGE} дней.'
            
            '\n\nНажмите "Обновить", чтобы обновить фотографии'
            '\nтекущей коллекции за все время с 2018 года.'
            )
        
        descrLabel = MyLabel(self)
        descrLabel.config(
            anchor='w', padx=5, text=txt1, justify='left')
        descrLabel.pack(pady=(30, 0))

        pathh = os.path.join(os.path.dirname(__file__), 'upd.jpg')
        imgSrc = Image.open(pathh)
        imgCopy= imgSrc.copy()
        imgRes = ImageOps.contain(imgCopy, (350,350))        
        imgTk = ImageTk.PhotoImage(imgRes)
         
        imgLbl = MyLabel(self)
        imgLbl.configure(image=imgTk)
        imgLbl.pack()
        imgLbl.image = imgTk

        sep = Separator(self, orient='horizontal')
        sep.pack(padx=40, pady=20, fill='x')
        
        txt2 = (       
            'Нажмите "Полное сканирование", чтобы обновить'
            '\nфотографии всех коллекций за все время c 2018 года.'
            )
        descrLabel2 = MyLabel(self)
        descrLabel2.config(
            anchor='w', padx=5, text=txt2, justify='left')
        descrLabel2.pack()
        
        scanBtn = MyButton(
            self, lambda event: self.RunScan(), 'Полное сканирование')
        scanBtn.pack(anchor='center', pady=10)

        sep = Separator(self, orient='horizontal')
        sep.pack(padx=40, pady=20, fill='x')
        
        name = (
            f'MiuzGallery {cfg.APP_VER}'
            '\n\n'
            )
        made = (
            'Created by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.'
            '\n'
            )

        createdBy = MyLabel(self)
        createdBy.configure(text=name+made, justify='left', padx=5)
        createdBy.pack(pady=20, anchor='w')
        

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
        
        for key, value in data.items():
            
            desrc = MyLabel(self)
            desrc.pack(anchor='w', pady=(30, 0), padx=(0, 15))
            labelsInserts.append(desrc)
            
            ins = tkinter.Entry(
                self, 
                bg=cfg.BGBUTTON, 
                fg=cfg.FONTCOLOR,
                insertbackground=cfg.FONTCOLOR,
                selectbackground=cfg.BGPRESSED,
                highlightthickness=5,
                highlightbackground=cfg.BGBUTTON,
                highlightcolor=cfg.BGBUTTON,
                bd=0,
                justify='center',
                )
            ins.insert(0, value)
            ins.pack(fill='x', pady=(0, 10), padx=(5, 15))
            TkObjects.inserts.append(ins)
            
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
            
        for ins, descr in zip(labelsInserts, descriptions):
            ins.configure(text=descr, justify='left', wraplength=340)

        restoreBtn = MyButton(self, '', 'По умолчанию')
        restoreBtn.configure(height=1, width=15)
        restoreBtn.bind(
            '<Button-1>', 
            lambda event, btn=restoreBtn: self.Restore(btn)
            )
        restoreBtn.pack(pady=(20, 15))
        
    def Restore(self, btn):
        btn.configure(bg=cfg.BGPRESSED)
        data = cfg.defaults
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(data, file, indent=4)
        
        cfg.ROOT.after(100, lambda: btn.configure(bg=cfg.BGBUTTON))
        
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)
        
        for item, ins in zip(data.values(), TkObjects.inserts):
            ins.delete(0, 'end')
            ins.insert(0, item)
                
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
