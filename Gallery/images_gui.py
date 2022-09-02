"""
Gui menu and images grid.
"""

import os
import re
import tkinter
import traceback
from datetime import datetime

import cfg
import cv2
import numpy
import sqlalchemy
import tkmacosx
from database import Config, Dbase, Thumbs
from PIL import Image, ImageTk
from Utils.Styled import MyButton, MyFrame, MyLabel

from .image_viewer import ImagePreview


class Globals:
    """
    Variables for current module
    """

    __getCurrColl = sqlalchemy.select(Config.value).where(
        Config.name=='currColl')
    currColl = Dbase.conn.execute(__getCurrColl).first()[0]

    # bind reset function for thumbnails frame: Images().Reset()
    images_reset = object


class Gallery(MyFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param master: tkinter frame
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        MenuFrame(self).pack(
            pady=(00, 0), padx=(0, 15), side=tkinter.LEFT, fill=tkinter.Y)
        ImagesFrame(self).pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)


class MenuFrame(tkmacosx.SFrame):
    """
    Creates tkinter scrollable Frame for menu.
    * param master: tkinter frame
    """
    def __init__(self, master):
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7, width=150)

        MenuButtons(self)

        screen_h = cfg.ROOT.winfo_screenheight()
        self['height'] = int(screen_h*0.45)

class MenuButtons(object):
    """
    Creates tkinter buttons with vertical pack.
    Buttons based on list of collections.
    List of collections based on Database > Thumbs.collection.
    * param master: tkinter frame
    """
    def __init__(self, master):
        img_src = Image.open(
            os.path.join(os.path.dirname(__file__), 'logo.png'))

        img_tk= ImageTk.PhotoImage(img_src)

        img_lbl = MyLabel(master)
        img_lbl.configure(image=img_tk)
        img_lbl.pack(pady=(0, 20))
        img_lbl.image_names = img_tk

        __query = sqlalchemy.select(Thumbs.collection)
        __res = Dbase.conn.execute(__query).fetchall()
        __colls_list = set(i[0] for i in __res)

        for_btns = []
        for coll_item in __colls_list:
            name_btn = coll_item.replace(
                re.search(r'(\d{0,30}\s){,1}', coll_item).group(),
                '')
            for_btns.append((name_btn[:13], coll_item))
        for_btns.sort()

        btns = []
        for name_btn, name_coll in for_btns:

            btn = MyButton(master, text=name_btn)
            btn.configure(height=1, width=12)
            btn.pack(pady=(0, 10))
            btns.append(btn)

            if name_coll == Globals.currColl:
                btn.configure(bg=cfg.BGPRESSED)

            btn.Cmd(lambda e, coll=name_coll, btn=btn, btns=btns:
                    self.__open_coll(coll, btn, btns))

    def __open_coll(self, coll, btn, btns):
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
        Globals.images_reset()


class ImagesFrame(tkmacosx.SFrame):
    """
    Creates tkinter scrollable frame for images.
    * param master: tkinter frame
    """
    def __init__(self, master):
        self.master = master
        Globals.images_reset = self.reset

        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7)

        ImagesThumbs(self)

        self.update_idletasks()
        w = self.winfo_reqwidth()
        self.configure(width=w*1.03)

    def reset(self):
        """
        Destroys self.Run init again
        """
        self.destroy()
        ImagesFrame(self.master).pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)


class ImagesThumbs(object):
    """
    Creates images grid based on database thumbnails.
    Grid is labels with images created with pack method.
    Number of columns in each row based on Database > Config > clmns > value.
    * param master: tkmacosx scrollable frame.
    """
    def __init__(self, master):

        title = MyLabel(
            master, text=Globals.currColl, font=('Arial', 45, 'bold'))
        title.pack(pady=(15, 15))

        clmns = Dbase.conn.execute(sqlalchemy.select(
                Config.value).where(Config.name=='clmns')).first()[0]
        clmns = int(clmns)

        thumbs = self.load_thumbs()

        if len(thumbs) == 0:
            return

        for y in self.split_years(thumbs):

            year_label = MyLabel(
                master, text=y[-1][-1], font=('Arial', 35, 'bold'))
            year_label.pack(pady=(15, 15))

            self.pack_rows(self.fill_empty(y, clmns), clmns, master)

    def load_thumbs(self):
        """
        Loads thumbnails from database > thumbnails based on size from
        database > config > size > value.
        * returns: list turples: (img, src, modified)
        """

        size = Dbase.conn.execute(
            sqlalchemy.select(Config.value).where(
                Config.name=='size')).first()[0]
        size = int(size)
        img = Thumbs.__dict__[f'img{size}']

        res = Dbase.conn.execute(
            sqlalchemy.select(img, Thumbs.src, Thumbs.modified).where(
            Thumbs.collection==Globals.currColl).order_by(
            -Thumbs.modified)).fetchall()

        thumbs = []
        for blob, src, mod in res:

            try:
                nparr = numpy.frombuffer(blob, numpy.byte)
                image1 = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)

                # convert cv2 color to rgb
                image_RGB = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)

                # load numpy array image
                image = Image.fromarray(image_RGB)
                photo = ImageTk.PhotoImage(image)
                year = datetime.fromtimestamp(mod).year
                thumbs.append((photo, src, year))

            except Exception:
                print(traceback.format_exc())

        return thumbs

    def fill_empty(self, thumbs, clmns):
        """
        Creates new images for thumbs list if thumbs list smaller than
        collumn count.
        Each new image has fill with cfg.BGCOLOR color and size based on
        database > config > size > value

        This is necessary so that the row with images has a fixed number of
        columns and tkinter root doesn't change it's size
        if the number of columns is too small.

        * returns: list of tuples (img, src, year)
        * param thumbs: list of tuples (img, src, year)
        * param clmns: int from database > config > clmns > value
        """

        if len(thumbs) < clmns and len(thumbs) != 0:
            year = thumbs[-1][-1]
            size = int(Dbase.conn.execute(
                    sqlalchemy.select(Config.value).where(
                    Config.name=='size')).first()[0])

            for _ in range(0, clmns-len(thumbs)):
                new = Image.new('RGB', (size, size), cfg.BGCOLOR)
                photo = ImageTk.PhotoImage(new)
                thumbs.append((photo, None, year))

        return thumbs

    def split_years(self, thumbs):
        """
        Splits a list into lists by year.
        * returns: list of lists
        * param thumbs: list tuples (imageTk, image src, image year modified)
        """
        years = set(year for _, _, year in thumbs)
        list_years = []

        for y in years:
            tmp = [(im, src, year) for im, src, year in thumbs if year == y]
            list_years.append(tmp)
        list_years.reverse()
        return list_years

    def pack_rows(self, thumbs, clmns, master):
        """
        Splits list of tuples by the number of lists.
        Each list is row with number of columns based on 'clmns'.

        In short we create images grid with a number columns from images list
        with tkinter pack method.
        Tkinter pack don't have 'new line' method and we need create
        tkinter frame for each row with images. For this we split big list
        into small lists, each of which is row with tkinter labels.

        * param thumbs: list tuples(imageTk, image src, image year)
        * param clmns: int from database > config > clmns > value
        * param master: tkinter frame
        """

        img_rows = [thumbs[x:x+clmns] for x in range(0, len(thumbs), clmns)]

        for row in img_rows:

            row_frame = MyFrame(master)
            row_frame.pack(fill=tkinter.Y, expand=True, anchor=tkinter.W)

            for image, src, _ in row:
                thumb = MyButton(row_frame, image=image, highlightthickness=1)
                thumb.configure(width=0, height=0, bg=cfg.BGCOLOR)
                thumb.image_names = image
                thumb.Cmd(lambda e, src=src: ImagePreview(src))
                thumb.pack(side=tkinter.LEFT)
