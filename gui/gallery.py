"""
Gui menu and images grid.
"""

import os
import re
import subprocess
import tkinter
import traceback
from datetime import datetime
from functools import partial

import sqlalchemy
import tkmacosx
from PIL import ImageTk

import cfg
from database import Dbase, Thumbs
from utils import convert_to_rgb, crop_image, decode_image

from .widgets import CButton, CFrame, CLabel, CSep
from .img_viewer import PreviewWindow


class Gallery(CFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        CFrame.__init__(self, master)

        menu = MenuButtons(self)
        menu.pack(pady=(0, 0), padx=(0, 15), side=tkinter.LEFT, fill=tkinter.Y)
        cfg.ROOT.update_idletasks()
        cfg.MENU_W = menu.winfo_reqwidth()

        imgs = ImagesThumbs(self)
        imgs.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)

        cfg.ROOT.bind('<ButtonRelease-1>', self.update_gui)

    def update_gui(self, e):
        root_w = cfg.config['GEOMETRY'][0]
        new_w = cfg.ROOT.winfo_width()
        if new_w != int(root_w):
            cfg.config['GEOMETRY'][0] = new_w
            cfg.THUMBNAILS_RELOAD()


class MenuButtons(tkmacosx.SFrame):
    """
    Creates tkinter buttons with vertical pack.
    Buttons based on list of collections.
    List of collections based on Database > Thumbs.collection.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        self.master = master
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7, width=170)
        title = CLabel(
            self, text='Коллекции', font=('Arial', 22, 'bold'))
        title.pack(pady=(20, 20), padx=(0, 15))

        load_colls = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)).fetchall()
        colls_list = set(i[0] for i in load_colls)
        for_btns = []
        for coll_item in colls_list:
            name_btn = coll_item.replace(
                re.search(r'(\d{0,30}\s){,1}', coll_item).group(), '')
            for_btns.append((name_btn[:13], coll_item))
        for_btns.sort()
        btns = []
        last = CButton(self, text='Последние')
        last.configure(height=1, width=13, pady=5, anchor=tkinter.W, padx=10)
        last.cmd(partial(self.collection_folder, 'last', last, btns))
        last.pack(fill=tkinter.X, padx=(0, 15), pady=(0, 15))
        btns.append(last)

        for name_btn, name_coll in for_btns:
            btn = CButton(self, text=name_btn)
            btn.configure(pady=5, anchor=tkinter.W, padx=10)
            btn.pack(fill=tkinter.X, padx=(0, 15))
            btns.append(btn)
            if name_coll == cfg.config['CURR_COLL']:
                btn.configure(bg=cfg.BGPRESSED)
            btn.cmd(partial(self.collection_folder, name_coll, btn, btns))
            sep = CSep(self)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X, padx=(0, 15))
        if cfg.config['CURR_COLL'] == 'last':
            last.configure(bg=cfg.BGPRESSED)

    def collection_folder(self, coll: str, btn: CButton, btns: list, e):
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
            btn['bg'] = cfg.BGSELECTED
            cfg.ROOT.after(200, lambda: btn.configure(bg=cfg.BGPRESSED))
            coll_path = os.path.join(os.sep, cfg.config['COLL_FOLDER'], coll)
            subprocess.check_output(["/usr/bin/open", coll_path])
            return
        for btn_item in btns:
            btn_item['bg'] = cfg.BGBUTTON
        btn['bg'] = cfg.BGPRESSED
        cfg.config['CURR_COLL'] = coll
        cfg.THUMBNAILS_RELOAD()


class ImagesThumbs(tkmacosx.SFrame):
    """
    Creates images grid based on database thumbnails.
    Grid is labels with images created with pack method.
    Number of columns in each row based on Database > Config > clmns > value.
    * param `master`: tkmacosx scrollable frame.
    """
    def __init__(self, master):
        self.master = master
        cfg.THUMBNAILS_RELOAD = self.thumbnails_reload
        tkmacosx.SFrame.__init__(
            self, master, bg=cfg.BGCOLOR, scrollbarwidth=7)

        self.clmns = (cfg.config['GEOMETRY'][0]-cfg.MENU_W)//cfg.THUMB_SIZE

        title = CLabel(
            self, text=cfg.config['CURR_COLL'],
            font=('Arial', 45, 'bold'))
        title.pack(pady=(0, 15))

        if cfg.config['CURR_COLL'] == 'last':
            title.configure(text='Последние добавленные')
            res = Dbase.conn.execute(sqlalchemy.select(
                    Thumbs.img150, Thumbs.src, Thumbs.modified).order_by(
                    -Thumbs.modified).limit(120)).fetchall()
        else:
            res = Dbase.conn.execute(sqlalchemy.select(
                    Thumbs.img150, Thumbs.src, Thumbs.modified).where(
                    Thumbs.collection==cfg.config['CURR_COLL']).order_by(
                    -Thumbs.modified)).fetchall()

        decoded_images = self.decode_thumbs(res)
        converted_years = self.convert_year(decoded_images)
        thumbs = self.split_years(converted_years)

        for y in thumbs:
            year_label = CLabel(
                self, text=y[-1][-1], font=('Arial', 35, 'bold'))
            year_label.pack(pady=(15, 15))
            self.pack_rows(y, self.clmns, self, [i[1] for i in res])

    def thumbnails_reload(self):
        """
        Destroys self.Run init again
        """
        selected = ''
        if cfg.COMPARE:
            for i in cfg.THUMBS:
                if i['bg'] == cfg.BGPRESSED:
                    selected = i['text']
                    break
        cfg.THUMBS.clear()
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        cfg.config['GEOMETRY'][0], cfg.config['GEOMETRY'][1] = w, h
        self.destroy()
        thumbs = ImagesThumbs(self.master)
        thumbs.pack(expand=True, fill=tkinter.BOTH, side=tkinter.RIGHT)
        if cfg.COMPARE:
            for i in cfg.THUMBS:
                if selected in i['text']:
                    i.configure(bg=cfg.BGPRESSED)
                    break

    def decode_thumbs(self, thumbs: tuple):
        """
        Prepares encoded images from database for tkinter.
        * input: ((`img`, `src`, `date modified`), ...)
        * returns: list turples: (img ready to tkinter label, src, modified)
        """
        result = []
        for blob, src, modified in thumbs:
            try:
                decoded = decode_image(blob)
                cropped = crop_image(decoded)
                rgb = convert_to_rgb(cropped)
                img = ImageTk.PhotoImage(rgb)
                result.append((img, src, modified))

            except Exception:
                print(traceback.format_exc())

        return result

    def convert_year(self, thumbs:list):
        """
        Converts image modified date to year
        * input: ((`img`, `src`, `date modified`), ...)
        * returns: list turples: (img ready to tkinter label, src, year)
        """
        result = []
        for img, src, modified in thumbs:
            year = datetime.fromtimestamp(modified).year
            result.append((img, src, year))
        return result

    def split_years(self, thumbs: list):
        """
        Splits a list into lists by year.
        * returns: list of lists
        * param `thumbs`: list tuples (imageTk, image src, image year modified)
        """
        years = set(year for _, _, year in thumbs)
        list_years = []
        for y in years:
            tmp = tuple(
                (img, src, year) for img, src, year in thumbs if year == y)
            list_years.append(tmp)
        list_years.reverse()
        return list_years

    def pack_rows(
        self, thumbs: list, clmns: int, master: tkinter.Frame, all_src: list):
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
        * param `all_src`: list of paths of all images
        """
        img_rows = [thumbs[x:x+clmns] for x in range(0, len(thumbs), clmns)]
        for row in img_rows:
            row_frame = CFrame(master)
            row_frame.pack(fill=tkinter.Y, expand=True, anchor=tkinter.W)
            for image, src, _ in row:
                thumb = CButton(row_frame)
                thumb['width'] = cfg.THUMB_SIZE
                thumb['height'] = cfg.THUMB_SIZE
                thumb['image'] = image
                thumb['text'] = src
                thumb['bg'] = cfg.BGCOLOR
                thumb.image = image
                thumb.cmd(partial(self.open_preview, src, all_src))
                thumb.bind('<Enter>', lambda e, a=thumb: self.enter(a))
                thumb.bind('<Leave>', lambda e, a=thumb: self.leave(a))
                thumb.pack(side=tkinter.LEFT)
                cfg.THUMBS.append(thumb)

    def enter(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGSELECTED

    def leave(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGCOLOR

    def open_preview(self, src, all_src, e):
        PreviewWindow(src, all_src)