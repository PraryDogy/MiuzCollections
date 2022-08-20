import tkinter

import cfg
import sqlalchemy
import tkmacosx
from DataBase.Database import Config, dBase

from .LoadThumbs import LoadThumbs
from .Prev import Prev


class Create(Prev):
    def  __init__(self, imgGrid):
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
        self.imgGrid = tkinter.Frame(imgGrid, bg=cfg.BGCOLOR)
        self.imgGrid.pack(fill='both', expand=True)

        selectRow = sqlalchemy.select(Config.value).where(
            Config.name=='currColl')
        self.curColl = dBase.conn.execute(selectRow).first()[0]

        self.TitlePack()
        self.ThumbnailsPack()


    def TitlePack(self):
        title = tkinter.Label(
            self.imgGrid, bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR,
            text=self.curColl, font=('Arial', 45, 'bold'), pady=15)
        title.pack()
        

    def ThumbnailsPack(self):
        thumbs = LoadThumbs(self.curColl)

        scrollable = tkmacosx.SFrame(
            self.imgGrid, bg=cfg.BGCOLOR, scrollbarwidth=10)
        scrollable.config(avoidmousewheel=(scrollable))
        scrollable.pack(expand=True, fill='both')

        selectRow = sqlalchemy.select(Config.value).where(
            Config.name=='clmns')
        сolls = int(dBase.conn.execute(selectRow).first()[0])

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

        endFrame = tkinter.Frame(
            self.imgGrid, bg=cfg.BGCOLOR, width=w*1.06, height=5)
        endFrame.pack()
