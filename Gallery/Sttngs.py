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
from Utils.Styled import *
from Utils.Utils import MyCopy, MyPaste

from .Descriptions import descriptions


class Globals:
    
    genFrame = tkinter.Frame
    expFrame = tkinter.Frame
    genBtn = tkinter.Button
    expBtn = tkinter.Button
    belowMenu = tkinter.Frame
    inserts = list()


class Settings(tkinter.Toplevel):
    def __init__(self):        
        """Tkinter toplevel with settings gui.
        Methods: just run init."""
        
        tkinter.Toplevel.__init__(self, cfg.ROOT, bg=cfg.BGCOLOR)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        
        self.withdraw()
        self.resizable(0,0)
        self.attributes('-topmost', 'true')
        self.title('Настройки')
        self.geometry(f'570x650')
        self.configure(padx=10, pady=10)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        self.deiconify()
        
    def on_closing(self):
        cfg.TOP_LVL = False
        self.destroy()

class LeftMenu(MyFrame):
    def __init__(self, master):
        MyFrame.__init__(self, master)
        genBtn = MyButton(self, text='Основные')
        genBtn.configure(bg=cfg.BGPRESSED)
        
        genBtn.Cmd(
            lambda e: self.Change(
                Globals.expFrame, 
                Globals.genFrame,
                Globals.genBtn,
                Globals.expBtn
                )
                )
        genBtn.pack()

        expertBtn = MyButton(
            self, text = 'Эксперт')

        expertBtn.Cmd(
            lambda e: self.Change(
                Globals.genFrame, 
                Globals.expFrame,
                Globals.expBtn, 
                Globals.genBtn
                )
                )
        expertBtn.pack()

        Globals.genBtn = genBtn
        Globals.expBtn = expertBtn
        
    def Change(self, frameForget=tkinter.Frame, framePack=tkinter.Frame, 
                    btnPress=tkinter.Button, btnUnpress=tkinter.Button):

        frameForget.pack_forget()
        framePack.pack(fill='both', expand=True)

        btnPress.configure(bg=cfg.BGPRESSED)
        btnUnpress.configure(bg=cfg.BGBUTTON)

        
class BelowMenu(MyFrame):
    def __init__(self, master):
        MyFrame.__init__(self, master)
        Globals.belowMenu = self
        
        btnSave = MyButton(self, text='Сохранить')
        btnSave.Cmd(lambda e: self.saveIns())
        btnSave.pack(side='left', padx=10)

        btnCancel = MyButton(self, text='Отмена')
        btnCancel.Cmd(lambda e: self.cancel())
        btnCancel.pack(side='left')
    
    def cancel(self):
        cfg.TOP_LVL = False
        self.winfo_toplevel().destroy()
        
    def saveIns(self):
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)

        newValues = [i.get() for i in Globals.inserts]
        for key, ins in zip(data, newValues):
            data[key] = ins
            
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(data, file, indent=4)
            
        Globals.inserts.clear()
        
        cfg.TOP_LVL = False
        self.winfo_toplevel().destroy()

        
class General(MyFrame):
    def __init__(self, master):
        MyFrame.__init__(self, master, padx=15)
        Globals.genFrame = self

        title = MyLabel(self, text='Основные', font=('Arial', 22, 'bold'))
        title.pack(pady=10)
        
        txt1 = (
            'При запуске программа сканирует и обновляет фото'
            f'\nвсех коллекций за последние {cfg.FILE_AGE} дней.'
            '\nНажмите "Обновить", чтобы повторно запустить сканирование.'
            )
        
        descrLabel = MyLabel(self)
        descrLabel.configure(
            text=txt1, justify='left', wraplength=350)
        descrLabel.pack(pady=(0, 10), anchor='w')

        pathh = os.path.join(os.path.dirname(__file__), 'upd.jpg')
        imgSrc = Image.open(pathh)
        imgCopy= imgSrc.copy()
        imgRes = ImageOps.contain(imgCopy, (335,335))        
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
        descrLabel2.configure(
            text=txt2, justify='left', wraplength=350)
        descrLabel2.pack(pady=(0, 10), anchor='w')
        
        scanBtn = MyButton(self, text='Полное сканирование')
        scanBtn.Cmd(lambda e: self.RunScan())
        scanBtn.pack(anchor='center')

        sep = Separator(self, orient='horizontal')
        sep.pack(padx=40, pady=(25, 20), fill='x')
        
        made = (
            f'{cfg.APP_NAME} {cfg.APP_VER}'
            '\nCreated by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.'
            )

        createdBy = MyLabel(self)
        createdBy.configure(
            text=made, justify='left')
        createdBy.pack(anchor='w')
        

    def RunScan(self):
        query = sqlalchemy.update(Config).where(
            Config.name=='typeScan').values(value='full')
        dBase.conn.execute(query)
        os.execv(sys.executable, ['python'] + sys.argv)


class Expert(tkmacosx.SFrame):
    def __init__(self, master):
        tkmacosx.SFrame.__init__(self, master, padx=15)
        self.configure(bg=cfg.BGCOLOR, scrollbarwidth=0)
        self.configure(avoidmousewheel=(self))
        Globals.expFrame = self

        title = MyLabel(self, text='Эксперт', font=('Arial', 22, 'bold'))
        title.pack(pady=10)
        
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)
        
        labelsInserts = list()
        
        for key, value in data.items():
            
            desrc = MyLabel(self, wraplength=350)
            desrc.pack(anchor='w', pady=(0, 10))
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
                width=35
                )
            ins.insert(0, value)
            ins.pack(pady=(0, 10))
            Globals.inserts.append(ins)
            
            frameBtns = MyFrame(self)
            frameBtns.pack()
            
            btnCopy = MyButton(frameBtns, text='Копировать')
            btnCopy.configure(height=1, width=9)
            btnCopy.Cmd(
                lambda e, ins=ins, btn=btnCopy: self.CopyIns(ins, btn)
                )
            btnCopy.pack(side='left', padx=(0, 10))
            
            btnPaste = MyButton(frameBtns, text='Вставить')
            btnPaste.configure(height=1, width=9)
            btnPaste.Cmd(
                lambda e, ins=ins, btn=btnPaste: self.PasteIns(ins, btn)
                )
            btnPaste.pack(side='right', padx=(0, 10))

            sep = Separator(self, orient='horizontal')
            sep.pack(padx=40, pady=20, fill='x')
        
        for ins, descr in zip(labelsInserts, descriptions):
            ins.configure(text=descr, justify='left', wraplength=340)

        restoreBtn = MyButton(self, text='По умолчанию')
        restoreBtn.configure(height=1, width=12)
        restoreBtn.Cmd(
            lambda e, btn=restoreBtn: self.Restore(btn)
            )
        restoreBtn.pack(pady=(0, 15))
        
    def Restore(self, btn):
        btn.configure(bg=cfg.BGPRESSED)
        data = cfg.defaults
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(data, file, indent=4)
        
        cfg.ROOT.after(100, lambda: btn.configure(bg=cfg.BGBUTTON))
        
        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
            data = json.load(file)
        
        for item, ins in zip(data.values(), Globals.inserts):
            ins.delete(0, 'end')
            ins.insert(0, item)
                
    def CopyIns(self, ins, btn):
        btn.configure(bg=cfg.BGPRESSED)
        text = ins.get()
        MyCopy(text)
        cfg.ROOT.after(100, lambda: btn.configure(bg=cfg.BGBUTTON))
    
    def PasteIns(self, ins, btn):
        btn.configure(bg=cfg.BGPRESSED)
        text = MyPaste()
        ins.delete(0, 'end')
        ins.insert(0, text)
        cfg.ROOT.after(100, lambda: btn.configure(bg=cfg.BGBUTTON))
