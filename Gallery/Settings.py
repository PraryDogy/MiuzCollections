import os
import sys
import tkinter
from tkinter.ttk import Separator

import cfg
import sqlalchemy
from DataBase.Database import Config, dBase


class Create:
    def __init__(self):
        '''
        Create tk TopLevel with tkinter.Labels and buttons\n
        Methods: just run class\n
        Imports: ManageDb from DataBase package
        '''
        self.newWin = tkinter.Toplevel(
            cfg.ROOT, padx=15, pady=15, bg=cfg.BGCOLOR)
        self.newWin.resizable(0,0)
        self.newWin.attributes('-topmost', 'true')

        self.newWin.title('Настройки')

        self.ScanFrame()
        self.ExpertFrame()
        self.AboutFrame()
        self.CloseFrame() 
        cfg.ROOT.eval(f'tk::PlaceWindow {self.newWin} center')        


    def ScanFrame(self):
        scanFrame = tkinter.Frame(self.newWin, bg=cfg.BGCOLOR)
        scanFrame.pack(anchor='w')

        descr = (
            'При запуске программа сканирует и обновляет фото'
            f'\nза последние {cfg.FILE_AGE} дней.'
            
            '\n\nНажмите "Обновить", чтобы обновить фотографии'
            '\nтекущей коллекции за все время с 2018 года.'
            
            '\n\nНажмите "Полное сканирование", чтобы обновить все'
            '\nфотографии за все время c 2018 года.'
            )
        
        descrLabel = tkinter.Label(
            scanFrame, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
            anchor='w', padx=5, text=descr, justify='left')
        descrLabel.pack(fill='x')

        belowDescr = tkinter.Frame(scanFrame, bg=cfg.BGCOLOR, height=10)
        belowDescr.pack()


        def FullScan():
            query = sqlalchemy.update(Config).where(
                Config.name=='typeScan').values(value='full')
            dBase.conn.execute(query)
            os.execv(sys.executable, ['python'] + sys.argv)
            
        scanBtn = tkinter.Label(
            scanFrame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
            height=2, width=17, text='Полное сканирование')
        scanBtn.pack(anchor='center')
        scanBtn.bind('<Button-1>', lambda event: FullScan())

        belowScan = tkinter.Frame(scanFrame ,height=10, bg=cfg.BGCOLOR)
        belowScan.pack()

        sep = Separator(scanFrame, orient='horizontal')
        sep.pack(fill='x')

        belowSep = tkinter.Frame(scanFrame ,height=10, bg=cfg.BGCOLOR)
        belowSep.pack()      

    def ExpertFrame(self):
        expFrame = tkinter.Frame(self.newWin, bg=cfg.BGCOLOR)
        expFrame.pack(anchor='w', fill='x')

        txt = (
            'Если изменился адрес сетевого диска,'
            '\nвы можете изменить его в экспертных настройках.')

        descrLabel = tkinter.Label(
            expFrame, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR,
            anchor='w', padx=5, text=txt, justify='left')
        descrLabel.pack(fill='x')

        belowDescr= tkinter.Frame(expFrame ,height=10, bg=cfg.BGCOLOR)
        belowDescr.pack()

        expBtn = tkinter.Label(
            expFrame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
            height=2, width=17, text='Режим эксперта')
        expBtn.pack(anchor='center')
        expBtn.bind('<Button-1>', lambda event:print('111'))

        belowBtn= tkinter.Frame(expFrame ,height=10, bg=cfg.BGCOLOR)
        belowBtn.pack()

        sep = Separator(expFrame, orient='horizontal')
        sep.pack(fill='x')

        belowSep = tkinter.Frame(expFrame ,height=10, bg=cfg.BGCOLOR)
        belowSep.pack()  


    def AboutFrame(self):
        aboutFrame = tkinter.Frame(self.newWin, bg=cfg.BGCOLOR)
        aboutFrame.pack(anchor='nw')

        descr = (
            'Created by Evgeny Loshkarev'
            '\nEmail: evlosh@gmail.com'
            '\nTelegram: evlosh'
            '\n'
            )

        createdBy = tkinter.Label(
            aboutFrame, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR, 
            text=descr, justify='left')
        createdBy.pack()


    def CloseFrame(self):
        closeFrame = tkinter.Frame(self.newWin, bg=cfg.BGCOLOR)
        closeFrame.pack(anchor='center')
        
        closeButton = tkinter.Label(
            closeFrame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            height=2, width=17, text='Закрыть')
        closeButton.bind('<Button-1>', lambda event: self.newWin.destroy())
        closeButton.pack()
        
