import re
import tkinter
import traceback

import cfg
import cv2
import numpy
import sqlalchemy
import tkmacosx
from DataBase.Database import Config, Thumbs, dBase
from PIL import Image, ImageTk
from Utils.Styled import *
from Utils.Utils import *

from .ImageShow import Prev


class Globals:
    """variables for current module"""

    __getCurrColl = sqlalchemy.select(Config.value).where(
        Config.name=='currColl')
    currColl = dBase.conn.execute(__getCurrColl).first()[0]

    # bind reset function for title frame: Title().Reset()
    titleReset = object

    # bind reset function for thumbnails frame: Images().Reset()
    imagesReset = object


class GalleryReset:
    def __init__(self):
        """Destroys title frame & images frame and create again."""
        Globals.titleReset()
        Globals.imagesReset()


class Gallery(MyFrame):
    def  __init__(self, master):
        """General frame:
        up: title
        bottom: left menu, right images"""

        MyFrame.__init__(self, master)
        Title(self)
        Scrollables(self)


class Title(MyLabel):
    def __init__(self, master):
        """Label, gets text from database > Config > currColl
        : don't need's pack
        : methods Reset
        : args master frame"""

        self.master = master
        MyLabel.__init__(
            self, master, text=Globals.currColl, font=('Arial', 45, 'bold'))
        self.pack(pady=15, side=tkinter.TOP)
        Globals.titleReset = self.Reset

    def Reset(self):
        self.destroy()
        self.__init__(self.master)


class Scrollables(MyFrame):
    def __init__(self, master):
        """Creates frame for menu and images.
        : don't need's pack
        : read Gallery notes"""

        MyFrame.__init__(self, master)
        self.pack(expand=True, fill=tkinter.BOTH, side=tkinter.BOTTOM)

        Menu(self)
        Images(self)


class Menu(tkmacosx.SFrame):
    def __init__(self, master):
        """Creates tkinter scrollable Frame for menu.
        : don't need's pack"""

        tkmacosx.SFrame.__init__(self, 
            master, bg=cfg.BGCOLOR, scrollbarwidth=1, width=150)
        self.pack(
            expand=True, fill=tkinter.Y, padx=(0, 15), side=tkinter.LEFT)
        MenuButtons(self)


class MenuButtons:
    def __init__(self, master):
        """This is menu with buttons, based on list of collections. 
        Database > Thumbs.collection creates list of collections. 
        Button command: open collection, 
        where collection name is button name."""

        __getCollsList = sqlalchemy.select(Thumbs.collection)
        __res = dBase.conn.execute(__getCollsList).fetchall()
        __collsList = set(i[0] for i in __res)
        
        collNames = list()
        for nameColl in __collsList:
            collEdit = re.search(r'(\d{0,30}\s){,1}', nameColl).group()
            nameBtn = nameColl.replace(collEdit, '')
            collNames.append((nameBtn[:13], nameColl))
        collNames.sort()

        btns = list()

        for nameBtn, nameColl in collNames:

            btn = MyButton(master, text=nameBtn)
            btn.configure(height=1, width=12)
            btn.pack(pady=(0, 10))
            btns.append(btn)

            if nameColl == Globals.currColl:
                btn.configure(bg=cfg.BGPRESSED)

            btn.Cmd(
                lambda e, coll=nameColl, btn=btn, btns=btns: 
                    self.OpenCollection(coll, btn, btns)) 

    def OpenCollection(self, coll, btn, btns):
        updateRow = sqlalchemy.update(Config).where(
                Config.name=='currColl').values(value=coll)
        dBase.conn.execute(updateRow)
        Globals.currColl = coll

        for b in btns:
            b['bg'] = cfg.BGBUTTON
        btn['bg'] = cfg.BGPRESSED
        GalleryReset()


class Images(tkmacosx.SFrame):
    def __init__(self, master):
        """Creates tkinter scrollable Frame for images.
        : don't need's pack"""
        self.master = master
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=1)
        ImagesThumbs(self)
        self.update_idletasks()
        w = self.winfo_reqwidth()
        self.configure(width=w*1.03)
        self.pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        Globals.imagesReset = self.Reset
        
    def Reset(self):
        self.destroy()
        self.__init__(self.master)


class ImagesThumbs():
    def __init__(self, master) -> None:
        _query = sqlalchemy.select(Config.value).where(
            Config.name=='clmns')
        сlmnCount = int(dBase.conn.execute(_query).first()[0])

        thumbs = self.LoadThumbs()
        if len(thumbs) < сlmnCount:
            
            query = sqlalchemy.select(Config.value).where(Config.name=='size')
            size = int(dBase.conn.execute(query).first()[0])
            
            for i in range(0, сlmnCount-len(thumbs)):
                new = Image.new('RGB', (size, size), cfg.BGCOLOR)
                photo = ImageTk.PhotoImage(new)
                thumbs.append((photo, None))
        
        imgRows = [
            thumbs[x:x+сlmnCount] for x in range(0, len(thumbs), сlmnCount)]
        
        for row in imgRows:
            frameRow = MyFrame(master)
            frameRow.pack(fill='y', expand=True, anchor='w')

            for image, src in row:

                l2 = MyButton(frameRow, image=image, highlightthickness=1)
                l2.configure(width=0, height=0, bg=cfg.BGCOLOR)
                l2.image = image
                l2.Cmd(lambda e, src=src: Prev(src))
                l2.pack(side='left')

    def LoadThumbs(self):
        """return list turples: (img, src)"""
        
        query = sqlalchemy.select(Config.value).where(Config.name=='size')
        size = int(dBase.conn.execute(query).first()[0])

        for i in [Thumbs.img150, Thumbs.img200, Thumbs.img250, Thumbs.img300]:
            if str(size) in str(i):
                img = i
            
        query = sqlalchemy.select(img, Thumbs.src).where(
            Thumbs.collection==Globals.currColl).order_by(
                -Thumbs.modified)
        res = dBase.conn.execute(query).fetchall()

        thumbs = list()

        for blob, src in res:
            try:
                nparr = numpy.frombuffer(blob, numpy.byte)
                image1 = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
                            
                # convert cv2 color to rgb
                imageRGB = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
                
                # load numpy array image
                image = Image.fromarray(imageRGB)
                photo = ImageTk.PhotoImage(image)

                thumbs.append((photo, src))

            except Exception:
                print(traceback.format_exc())

        return thumbs
