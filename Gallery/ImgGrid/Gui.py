from re import T
import tkinter

import cfg
import sqlalchemy
import tkmacosx
from DataBase.Database import Config, dBase
from PIL import Image, ImageTk
from Utils.Styled import *

from .LoadThumbs import LoadThumbs
from .Prev import Prev


class Create(MyFrame):
    def  __init__(self):
        """We have database.db with table named Thumbs.
        In Thumbs: img150, img200, img250, img300, src, collection, modified.
        
        We create tkinter table with pack method.
        
        Each ceil in table is tkinter Label with img from Thumbs (150-300).
        Each label binded to mouse click, click is open full size image.
        
        We get images from selected collection only.
        Selected collection is "curColl" from Config table from database.db
        
        Each collection name equal folder name in "collection dir".
        We get collection folders list with Utils > CollectionScan.py
        
        We get images by selected collection and split this list to parts.
        Each part equal count from Config table > clmns.
        Clmns is number of columns in our images grid.
        
        Generally:
        We get images filtered by selected collection
        and create images grid with number columns from clmns
        and images size from "size" from database.db > Config > size"""
        
        super().__init__(cfg.UP_FRAME)
        cfg.GRID_GUI = Create
        cfg.IMG_GRID = self
        self.Gui()
        
    def Gui(self):
        selectRow = sqlalchemy.select(Config.value).where(
            Config.name=='currColl')
        curColl = dBase.conn.execute(selectRow).first()[0]

        title = MyLabel(
            self, text=curColl, font=('Arial', 45, 'bold'), pady=15)
        title.pack()


        scrollable = tkmacosx.SFrame(
            self, bg=cfg.BGCOLOR, scrollbarwidth=10)
        scrollable.configure(avoidmousewheel=(scrollable))
        scrollable.pack(expand=True, fill='both')
        
        selectRow = sqlalchemy.select(Config.value).where(
            Config.name=='clmns')
        сolls = int(dBase.conn.execute(selectRow).first()[0])

        thumbs = LoadThumbs(curColl)
        if len(thumbs) < сolls:
            
            query = sqlalchemy.select(Config.value).where(Config.name=='size')
            size = int(dBase.conn.execute(query).first()[0])
            
            for i in range(0, сolls-len(thumbs)):
                new = Image.new('RGB', (size, size), cfg.BGCOLOR)
                photo = ImageTk.PhotoImage(new)
                thumbs.append((photo, None))
        
        imgRows = [thumbs[x:x+сolls] for x in range(0, len(thumbs), сolls)]
        for row in imgRows:
            
            frameRow = MyFrame(scrollable)
            frameRow.pack(fill='y', expand=True, anchor='w')

            for image, src in row:

                l2 = MyButton(frameRow, image=image, highlightthickness=1)
                l2.configure(width=0, height=0, bg=cfg.BGCOLOR)
                l2.image = image
                l2.Cmd(lambda event, src=src: Prev(src))
                l2.pack(side='left')
                            
        scrollable.update_idletasks()
        w = scrollable.winfo_reqwidth()

        gridW = tkinter.Frame(
            self, bg=cfg.BGCOLOR, width=w*1.06, height=5)
        gridW.pack()
        