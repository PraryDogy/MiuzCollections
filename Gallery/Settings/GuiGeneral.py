import os
from re import T
import sys
import tkinter
from tkinter.ttk import Separator

import cfg
import sqlalchemy
from DataBase.Database import Config, dBase
from Utils.Styled import *


class FullScan(MyFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

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
        descrLabel.pack(fill='x', pady=10)

        scanBtn = MyButton(
            self, lambda event: self.RunScan(), 'Полное сканирование')
        scanBtn.pack(anchor='center')
        
        sep = Separator(self, orient='horizontal')
        sep.pack(fill='x', pady=10)
    

    def RunScan(self):
        query = sqlalchemy.update(Config).where(
            Config.name=='typeScan').values(value='full')
        dBase.conn.execute(query)
        os.execv(sys.executable, ['python'] + sys.argv)


class About(MyFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(anchor='nw')

        descr = (
            'Created by Evgeny Loshkarev'
            '\nEmail: evlosh@gmail.com'
            '\nTelegram: evlosh'
            '\n'
            )

        createdBy = MyLabel(self)
        createdBy.configure(text=descr, justify='left')
        createdBy.pack()