import tkinter

import cfg
import sqlalchemy
import tkmacosx
from DataBase.Database import Config, dBase
from PIL import Image, ImageTk

from .LoadThumbs import LoadThumbs
from .Prev import Prev


class Create(Prev):
    def  __init__(self):
        '''
        We have database.db with table named Thumbs.
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
        and images size from "size" from database.db > Config > size
        '''
        selectRow = sqlalchemy.select(Config.value).where(
            Config.name=='currColl')
        self.curColl = dBase.conn.execute(selectRow).first()[0]

        self.TitlePack()
        self.ThumbnailsPack()


    def TitlePack(self):
        title = tkinter.Label(
            cfg.IMG_GRID, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR,
            text=self.curColl, font=('Arial', 45, 'bold'), pady=15)
        title.pack()
        

    def ThumbnailsPack(self):
        
        thumbs = LoadThumbs(self.curColl)

        scrollable = tkmacosx.SFrame(
            cfg.IMG_GRID, bg=cfg.BGCOLOR, scrollbarwidth=10)
        scrollable.configure(avoidmousewheel=(scrollable))
        scrollable.pack(expand=True, fill='both')
        
        selectRow = sqlalchemy.select(Config.value).where(
            Config.name=='clmns')
        сolls = int(dBase.conn.execute(selectRow).first()[0])

        if len(thumbs) < сolls:
            
            query = sqlalchemy.select(Config.value).where(Config.name=='size')
            size = int(dBase.conn.execute(query).first()[0])
            
            for i in range(0, сolls-len(thumbs)):
                new = Image.new('RGB', (size, size), cfg.BGCOLOR)
                photo = ImageTk.PhotoImage(new)
                thumbs.append((photo, None))
        
        imgRows = [thumbs[x:x+сolls] for x in range(0, len(thumbs), сolls)]

        for row in imgRows:
            
            frameRow = tkinter.Frame(scrollable, bg=cfg.BGCOLOR)
            frameRow.pack(anchor='w', fill='y', expand=True)

            for image, src in row:
                
                l2 = tkinter.Label(
                    frameRow, bg=cfg.BGCOLOR, image=image, 
                    highlightthickness=1)
                l2.image = image
                l2.bind(
                    '<Button-1>', 
                    lambda event, src=src: Prev(src)
                    )
                l2.pack(side='left')
            
        scrollable.update_idletasks()
        w = scrollable.winfo_reqwidth()

        gridW = tkinter.Frame(
            cfg.IMG_GRID, bg=cfg.BGCOLOR, width=w*1.06, height=5)
        gridW.pack()