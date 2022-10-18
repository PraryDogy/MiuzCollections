"""
Gui menu and images grid.
"""

import os
import re
import subprocess
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
from utils.utils import MyButton, MyFrame, MyLabel

from .image_viewer import ImagePreview


def get_curr_coll():
    """
    Returns name of selected collection.
    Loads from Database > Config > currColl > value.
    """
    return Dbase.conn.execute(sqlalchemy.select(Config.value).where(
        Config.name=='currColl')).first()[0]


def get_size():
    """
    Returns int selected thumbnails size.
    Loads from Database > Config > size > value
    """
    return int(Dbase.conn.execute(sqlalchemy.select(Config.value).where(
        Config.name=='size')).first()[0])


def upd_curr_coll(coll):
    """
    Updates Database > Config > currColl > value
    * param `coll`: str selected collection name
    """
    Dbase.conn.execute(sqlalchemy.update(Config).where(
        Config.name=='currColl').values(value=coll))


def load_last(img_size):
    """
    Returns tuples list (image, image source, image modified time).
    * param `img_size`: Thumbs.__dict__['img'+ `Globals().get_size()`]
    """
    return Dbase.conn.execute(sqlalchemy.select(
        img_size, Thumbs.src, Thumbs.modified).order_by(
                    -Thumbs.modified).limit(60)).fetchall()


def load_curr_coll(img_size, curr_coll):
    """
    Returns tuples list (image, image source, image modified time).
    * param `img_size`: Thumbs.__dict__['img'+ `Globals().get_size()`]
    * param `curr_coll`: from `Globals().get_curr_coll()`
    """
    return Dbase.conn.execute(sqlalchemy.select(
        img_size, Thumbs.src, Thumbs.modified).where(
            Thumbs.collection==curr_coll).order_by(
                -Thumbs.modified)).fetchall()


class Gallery(MyFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        MenuButtons(self).pack(
            pady=(0, 0), padx=(0, 15), side=tkinter.LEFT, fill=tkinter.Y)
        ImagesThumbs(self).pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)


class MenuButtons(tkmacosx.SFrame):
    """
    Creates tkinter buttons with vertical pack.
    Buttons based on list of collections.
    List of collections based on Database > Thumbs.collection.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7, width=150)

        img_src = Image.open(
            os.path.join(os.path.dirname(__file__), 'logo.png'))

        img_tk= ImageTk.PhotoImage(img_src)

        img_lbl = MyLabel(self)
        img_lbl.configure(image=img_tk)
        img_lbl.pack(pady=(0, 0))
        img_lbl.image_names = img_tk

        company_name = MyLabel(
            self, text='Коллекции', font=('Arial', 18, 'bold'))
        company_name.pack(pady=(15, 20))

        __res = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)).fetchall()
        __colls_list = set(i[0] for i in __res)

        for_btns = []
        for coll_item in __colls_list:
            name_btn = coll_item.replace(
                re.search(r'(\d{0,30}\s){,1}', coll_item).group(),
                '')
            for_btns.append((name_btn[:13], coll_item))
        for_btns.sort()

        curr_coll = get_curr_coll()
        btns = []
        for name_btn, name_coll in for_btns:

            btn = MyButton(self, text=name_btn)
            btn.configure(height=1, width=12 ,pady=1)
            btn.pack(pady=(0, 10))
            btns.append(btn)

            if name_coll == curr_coll:
                btn.configure(bg=cfg.BGPRESSED)

            btn.cmd(lambda e, coll=name_coll, btn=btn, btns=btns:
                    self.__open_coll(coll, btn, btns))

        last_imgs = MyButton(self, text='Последние')
        last_imgs.configure(height=1, width=12)
        last_imgs.cmd(lambda e: self.__open_coll('last', last_imgs, btns))
        last_imgs.pack(pady=(0, 10))
        btns.append(last_imgs)

        if curr_coll == 'last':
            last_imgs.configure(bg=cfg.BGPRESSED)

    def __open_coll(self, coll, btn, btns):
        """
        Changes all buttons color to default and change color for
        pressed button.
        Updates database > config > currColl > value to collection from
        button.
        Runs GalleryReset.
        * param `coll`: str, real collection name from path to img
        * param `btn`: tkinter curren button object
        * param `btns`: list of created tkinter buttons
        """

        if btn['bg'] == cfg.BGPRESSED:
            coll_path = os.path.join(os.sep, cfg.config['COLL_FOLDER'], coll)
            subprocess.check_output(["/usr/bin/open", coll_path])
            return

        for btn_item in btns:
            btn_item['bg'] = cfg.BGBUTTON
        btn['bg'] = cfg.BGPRESSED

        upd_curr_coll(coll)
        cfg.IMAGES_RESET()


class ImagesThumbs(tkmacosx.SFrame):
    """
    Creates images grid based on database thumbnails.
    Grid is labels with images created with pack method.
    Number of columns in each row based on Database > Config > clmns > value.
    * param `master`: tkmacosx scrollable frame.
    """
    def __init__(self, master):
        self.master = master
        cfg.IMAGES_RESET = self.reset

        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7)

        w = int(cfg.config["ROOT_SIZE"].split('x')[0])
        clmns = ((w)//158)-1

        print(w)
        print(clmns)

        img_size = Thumbs.__dict__[f'img{get_size()}']
        curr_coll = get_curr_coll()

        if curr_coll == 'last':
            res = load_last(img_size)

        else:
            res = load_curr_coll(img_size, curr_coll)

        title = MyLabel(
            self, text=curr_coll, font=('Arial', 45, 'bold'))
        title.pack(pady=(0, 15))

        if curr_coll == 'last':
            title.configure(text='Последние добавленные')

        thumbs = self.load_thumbs(res)

        if len(thumbs) == 0:
            return

        for y in self.split_years(thumbs):

            year_label = MyLabel(
                self, text=y[-1][-1], font=('Arial', 35, 'bold'))
            year_label.pack(pady=(15, 15))

            self.pack_rows(self.fill_empty(y, clmns), clmns, self)

    def reset(self):
        """
        Destroys self.Run init again
        """
        print('eee')
        self.destroy()
        ImagesThumbs(self.master).pack(
            expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)

    def load_thumbs(self, all_images):
        """
        Loads thumbnails from database > thumbnails based on size from
        database > config > size > value.
        * returns: list turples: (img, src, modified)
        """

        thumbs = []
        for blob, src, mod in all_images:
            try:
                nparr = numpy.frombuffer(blob, numpy.byte)
                image1 = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)

                # convert cv2 color to rgb
                image_rgb = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)

                # load numpy array image
                image = Image.fromarray(image_rgb)
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
        * param `thumbs`: list of tuples (img, src, year)
        * param `clmns`: int from database > config > clmns > value
        """

        if len(thumbs) < clmns and len(thumbs) != 0:
            year = thumbs[-1][-1]
            size = get_size()

            for _ in range(0, clmns-len(thumbs)):
                new = Image.new('RGB', (size, size), cfg.BGCOLOR)
                photo = ImageTk.PhotoImage(new)
                thumbs.append((photo, None, year))

        return thumbs

    def split_years(self, thumbs):
        """
        Splits a list into lists by year.
        * returns: list of lists
        * param `thumbs`: list tuples (imageTk, image src, image year modified)
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

        * param `thumbs`: list tuples(imageTk, image src, image year)
        * param `clmns`: int from database > config > clmns > value
        * param `master`: tkinter frame
        """

        img_rows = [thumbs[x:x+clmns] for x in range(0, len(thumbs), clmns)]

        for row in img_rows:

            row_frame = MyFrame(master)
            row_frame.pack(fill=tkinter.Y, expand=True, anchor=tkinter.W)

            for image, src, _ in row:
                thumb = MyButton(row_frame, image=image, highlightthickness=1)
                thumb.configure(width=0, height=0, bg=cfg.BGCOLOR)
                thumb.image_names = image
                thumb.cmd(lambda e, src=src: ImagePreview(src))
                thumb.pack(side=tkinter.LEFT)
