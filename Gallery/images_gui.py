"""
Gui menu and images grid.
"""

import re
import tkinter
import traceback

import cfg
import cv2
import numpy
import sqlalchemy
import tkmacosx
from database import Config, Dbase, Thumbs
from PIL import Image, ImageTk
from Utils.Styled import MyButton, MyFrame, MyLabel
# from Utils.Utils import *

from .image_viewer import ImagePreview


class Globals:
    """
    Variables for current module
    """

    __getCurrColl = sqlalchemy.select(Config.value).where(
        Config.name=='currColl')
    currColl = Dbase.conn.execute(__getCurrColl).first()[0]

    # bind reset function for title frame: Title().Reset()
    title_reset = object

    # bind reset function for thumbnails frame: Images().Reset()
    images_reset = object


class GalleryReset:
    """
    Destroys title frame & images frame and create again.
    """
    def __init__(self):
        Globals.title_reset()
        Globals.images_reset()


class Gallery(MyFrame):
    """
    General frame:
    *up: title
    *bottom: left menu, right images
    """
    def  __init__(self, master):

        MyFrame.__init__(self, master)
        Title(self)
        Scrollables(self)


class Title(MyLabel):
    """
    Label, gets text from database > Config > currColl
    * don't need's pack
    * methods: reset
    * param master: tkinter frame
    """
    def __init__(self, master):
        self.master = master
        MyLabel.__init__(
            self, master, text=Globals.currColl, font=('Arial', 45, 'bold'))
        self.pack(pady=15, side=tkinter.TOP)
        Globals.title_reset = self.reset

    def reset(self):
        """
        Destroys self.Run init again
        """
        self.destroy()
        Title(self.master)


class Scrollables(MyFrame):
    """
    Creates frame for menu and images.
    * don't need's pack
    * read Gallery notes
    * param master: tkinter frame
    """

    def __init__(self, master):
        MyFrame.__init__(self, master)
        self.pack(expand=True, fill=tkinter.BOTH, side=tkinter.BOTTOM)

        MenuFrame(self)
        ImagesFrame(self)


class MenuFrame(tkmacosx.SFrame):
    """
    Creates tkinter scrollable Frame for menu.
    * don't need's pack
    * param master: tkinter frame
    """
    def __init__(self, master):
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=1, width=150)
        self.pack(fill=tkinter.Y, padx=(0, 15), side=tkinter.LEFT)
        MenuButtons(self)


class MenuButtons(list):
    """
    This is menu with buttons, based on list of collections.
    Database > Thumbs.collection creates list of collections.
    """
    def __init__(self, master):
        __query = sqlalchemy.select(Thumbs.collection)
        __res = Dbase.conn.execute(__query).fetchall()
        __colls_list = set(i[0] for i in __res)

        for coll_item in __colls_list:
            name_btn = coll_item.replace(
                re.search(r'(\d{0,30}\s){,1}', coll_item).group(),
                '')
            self.append((name_btn[:13], coll_item))
        self.sort()

        btns = []
        for name_btn, name_coll in self:

            btn = MyButton(master, text=name_btn)
            btn.configure(height=1, width=12)
            btn.pack(pady=(0, 10))
            btns.append(btn)

            if name_coll == Globals.currColl:
                btn.configure(bg=cfg.BGPRESSED)

            btn.Cmd(lambda e, coll=name_coll, btn=btn, btns=btns:
                    self.open_coll(coll, btn, btns))

    def open_coll(self, coll, btn, btns):
        """
        Changes all buttons color to default and change color for
        pressed button.
        Updates database > config > currColl > value to collection from
        button.
        Runs GalleryReset.
        * param coll: str, stores real collection name
        * param btn: tkinter curren button object
        * param btns: list of created tkinter buttons
        """

        Dbase.conn.execute(
            sqlalchemy.update(Config).where(
                Config.name=='currColl').values(value=coll))
        Globals.currColl = coll

        for btn_item in btns:
            btn_item['bg'] = cfg.BGBUTTON
        btn['bg'] = cfg.BGPRESSED
        GalleryReset()


class ImagesFrame(tkmacosx.SFrame):
    """
    Creates tkinter scrollable Frame for images.
    * don't need's pack
    * param master: tkinter frame
    """
    def __init__(self, master):
        self.master = master
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=1)

        ImagesThumbs(self)

        self.update_idletasks()
        w = self.winfo_reqwidth()
        self.configure(width=w*1.03)

        self.pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)

        Globals.images_reset = self.reset

    def reset(self):
        """
        Destroys self.Run init again
        """
        self.destroy()
        ImagesFrame(self.master)


class ImagesThumbs(MyFrame):
    """
    Creates images grid based on database thumbnails.
    Grid is labels with images created with pack method.
    Number of columns in each row based on Database > Config > clmns > value.
    * param master: tkmacosx scrollable frame.
    """
    def __init__(self, master) -> None:
        clmns = Dbase.conn.execute(sqlalchemy.select(
            Config.value).where(Config.name=='clmns')).first()[0]
        clmns = int(clmns)

        thumbs = self.load_thumbs()
        if len(thumbs) < clmns:

            query = sqlalchemy.select(Config.value).where(Config.name=='size')
            size = int(Dbase.conn.execute(query).first()[0])

            for i in range(0, clmns-len(thumbs)):
                new = Image.new('RGB', (size, size), cfg.BGCOLOR)
                photo = ImageTk.PhotoImage(new)
                thumbs.append((photo, None))

        img_rows = [thumbs[x:x+clmns] for x in range(0, len(thumbs), clmns)]
        for row in img_rows:

            MyFrame.__init__(self, master)
            self.pack(fill=tkinter.Y, expand=True, anchor=tkinter.W)

            for image, src in row:
                thumb = MyButton(self, image=image, highlightthickness=1)
                thumb.configure(width=0, height=0, bg=cfg.BGCOLOR)
                thumb.image_names = image
                thumb.Cmd(lambda e, src=src: ImagePreview(src))
                thumb.pack(side=tkinter.LEFT)


    def load_thumbs(self):
        """
        Loads thumbnails from database > thumbnails based on size from
        database > config > size > value.
        * returns: list turples: (img, src)
        """

        size = Dbase.conn.execute(
            sqlalchemy.select(Config.value).where(
                Config.name=='size')).first()[0]
        size = int(size)

        for i in [Thumbs.img150, Thumbs.img200, Thumbs.img250, Thumbs.img300]:
            if str(size) in str(i):
                img = i

        res = Dbase.conn.execute(
            sqlalchemy.select(img, Thumbs.src).where(
                    Thumbs.collection==Globals.currColl).order_by(
                        -Thumbs.modified)).fetchall()

        thumbs = []
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
