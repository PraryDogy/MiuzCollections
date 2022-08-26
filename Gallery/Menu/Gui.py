from calendar import prcal
import re
import tkinter

import cfg
import sqlalchemy
from DataBase.Database import Config, Thumbs, dBase

from .CollapseBtn import CollapseMenu
from .OpenCollection import OpenCollection
from Utils.Styled import *


class Create(MyFrame):
    def __init__(self):
        """
        We have list of collections created from database > Thumbs, 
        each collection is button.
        
        We have option: one or two columns for buttons, 
        collapse button always right of collection buttons.
        
        On click to collapce button we change columns with collection 
        buttons to 1 or 2.
        
        Structure:
        
        - self > Frame (both columns collection buttons), Frame (collapse)
        
        - buttonsFrame > left & space between & right columns with buttons or
          both columns is above & below
        
        - collapseFrame > collapse button
        ***
        coll = collection
        btn = button
        clps = collapse
        clmn = column
        """
        
        super().__init__(cfg.UP_FRAME)
        self.pack(side='left')
        
        getCollsList = sqlalchemy.select(Thumbs.collection)
        res = dBase.conn.execute(getCollsList).fetchall()
        res = set(i[0] for i in res)
        
        self.collsNames = list()
        for nameColl in res:
            collEdit = re.search(r'(\d{0,30}\s){,1}', nameColl).group()
            nameBtn = nameColl.replace(collEdit, '')
            self.collsNames.append((nameBtn[:13], nameColl))
            
        self.collsNames.sort()
        
        collBtnsFrame = tkinter.Frame(self, bg=cfg.BGCOLOR)
        collBtnsFrame.pack(side='left')
        self.clpsBtnFrame = tkinter.Frame(self, bg=cfg.BGCOLOR)
        self.clpsBtnFrame.pack(side='right')
               
        self.firstClmn = tkinter.Frame(collBtnsFrame, bg=cfg.BGCOLOR)
        self.between = tkinter.Frame(collBtnsFrame, bg=cfg.BGCOLOR)
        self.secClmn = tkinter.Frame(collBtnsFrame, bg=cfg.BGCOLOR)

        getMenuClmn = sqlalchemy.select(Config.value).where(
            Config.name=='menuClmn')
        dbMenuClmn = int(dBase.conn.execute(getMenuClmn).first()[0])

        if dbMenuClmn==1:
            self.firstClmn.pack(side='top')
            self.between.configure(width=0)
            self.between.pack(side='top')
            self.secClmn.pack(side='top')
            
        else:
            self.firstClmn.pack(side='left')
            self.between.configure(width=10)
            self.between.pack(side='left')
            self.secClmn.pack(side='left')
                
        self.CollectionButtonsCreate()
        self.CollapseButtonCreate()
    
    
    def CollectionButtonsCreate(self):
        '''
        We append all created buttons to this list
        for send this list to OpenCollectionFile.py > OpenCollection function.
        '''
        
        allBtns = list()
        
        for nameBtn, nameColl in self.collsNames[:len(self.collsNames)//2]:
            collBtn = tkinter.Label(
                self.firstClmn, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
                height=1, width=12,
                text=nameBtn,
                )
            
            collBtn.pack(pady=(0, 10))
            allBtns.append(collBtn)
                   
            collBtn.bind(
                '<Button-1>', 
                lambda event, 
                allBtns=allBtns, 
                currBtn=collBtn,
                coll=nameColl: 
                    OpenCollection(allBtns, currBtn, coll)) 
 
        for nameBtn, nameColl in self.collsNames[len(self.collsNames)//2:]:
            collBtn = tkinter.Label(
                self.secClmn, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
                height=1, width=12,
                text=nameBtn,
                )
                
            collBtn.pack(pady=(0, 10))
            allBtns.append(collBtn)
            
            collBtn.bind(
                '<Button-1>', 
                lambda event, 
                allBtns=allBtns, 
                currBtn=collBtn,
                coll=nameColl: 
                    OpenCollection(allBtns, currBtn, coll))
            
        getCurrColl = sqlalchemy.select(Config.value).where(
            Config.name=='currColl')
        currColl = dBase.conn.execute(getCurrColl).first()[0]
        
        for btn in allBtns:
            if btn['text'] in currColl:
                btn.configure(bg=cfg.BGPRESSED)
                
                
    def CollapseButtonCreate(self):
        leftClps = tkinter.Frame(
            self.clpsBtnFrame, bg=cfg.BGCOLOR, width=10)
        leftClps.pack(side='left')
        
        clpsBtn = tkinter.Label(
            self.clpsBtnFrame, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR, 
            width=1, height=10)
        clpsBtn.pack(side='left')

        rightClps = tkinter.Frame(
            self.clpsBtnFrame, bg=cfg.BGCOLOR, width=10)
        rightClps.pack(side='left')

        getMenuCols = sqlalchemy.select(Config.value).where(
            Config.name=='menuClmn')
        dbMenuCols = int(dBase.conn.execute(getMenuCols).first()[0])
        
        if dbMenuCols==1:
            clpsBtn.configure(text='▶')
        else:
            clpsBtn.configure(text='◀')
            
        clpsBtn.bind(
            '<Button-1>', lambda event: CollapseMenu(
                clpsBtn, self.firstClmn, self.between, self.secClmn))
        

