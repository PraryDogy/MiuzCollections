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
from . import ImgViewer


class Gallery(CFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        CFrame.__init__(self, master)
        cfg.GALLERY = self

        menu_wid = self.menu_widget(self)
        menu_wid.pack(fill=tkinter.Y, side=tkinter.LEFT)
        menu_wid: tkinter.Frame

        cfg.ROOT.update_idletasks()

        self.menu_w = menu_wid.winfo_reqwidth()

        self.thumbs_wid = self.thumbnails_widget(self)
        self.thumbs_wid.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

        cfg.ROOT.bind('<ButtonRelease-1>', self.update_gui)

    def update_gui(self, e: tkinter.Event):
        root_w = cfg.config['GEOMETRY'][0]
        new_w = cfg.ROOT.winfo_width()
        if new_w != root_w:
            cfg.config['GEOMETRY'][0] = new_w
            self.thumbnails_reload()

    def thumbnails_reload(self):
        """
        Destroys `ImagesThumbs` object and run it again.
        """
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        cfg.config['GEOMETRY'][0], cfg.config['GEOMETRY'][1] = w, h

        self.thumbs_wid.destroy()

        self.thumbs_wid = self.thumbnails_widget(self)
        self.thumbs_wid.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

    def place_thumb(self, thumbnail):
        cropped = crop_image(thumbnail)
        rgb_thumb = convert_to_rgb(cropped)
        img_tk = ImageTk.PhotoImage(rgb_thumb)

        self.compare_img['image'] = img_tk
        self.compare_img.image_names = img_tk

        self.compare_title['text'] = 'В списке сравнения:'

        self.compare_frame.pack(side=tkinter.TOP)

    def remove_thumb(self):
        self.compare_img['image'] = ''
        self.compare_title['text'] = ''
        self.compare_frame.pack_forget()

    def menu_widget(self, master):
        scrollable = tkmacosx.SFrame(
            master, bg=cfg.BGCOLOR, scrollbarwidth=7, width=cfg.THUMB_SIZE+30)

        parent = CFrame(scrollable)
        parent.pack(padx=15)

        self.compare_frame = CFrame(parent)

        self.compare_title = CLabel(self.compare_frame)
        self.compare_title.pack()

        self.compare_img = CLabel(self.compare_frame)
        self.compare_img.pack(pady=(0, 15))

        menu_frame = CFrame(parent)
        menu_frame.pack(side=tkinter.BOTTOM)

        title = CLabel(
            menu_frame, text='Коллекции', font=('Arial', 22, 'bold'))
        title.pack(pady=(0,15))

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

        last = CButton(menu_frame, text='Последние')
        last.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        last.cmd(partial(self.collection_folder, 'last', last, btns))
        last.pack(fill=tkinter.X, pady=(0, 15))
        btns.append(last)

        for name_btn, name_coll in for_btns:
            btn = CButton(menu_frame, text=name_btn)
            btn.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
            btn.cmd(partial(self.collection_folder, name_coll, btn, btns))
            btn.pack(fill=tkinter.X)
            btns.append(btn)

            if name_coll == cfg.config['CURR_COLL']:
                btn.configure(bg=cfg.BGPRESSED)

            sep = CSep(menu_frame)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X)
    
        if cfg.config['CURR_COLL'] == 'last':
            last.configure(bg=cfg.BGPRESSED)

        return scrollable

    def thumbnails_widget(self, master: tkinter):
        parent = CFrame(master)
        scrollable = tkmacosx.SFrame(parent, bg=cfg.BGCOLOR, scrollbarwidth=7)
        scrollable.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

        self.clmns = (cfg.config['GEOMETRY'][0]-self.menu_w)//cfg.THUMB_SIZE

        title = CLabel(
            scrollable, text=cfg.config['CURR_COLL'], font=('Arial', 45, 'bold'))
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

        all_src = tuple(i[1] for i in converted_years)
        self.years = set(year for _, _, year in converted_years)

        years_split = self.years_list(converted_years)

        packed_thumbs = tuple(self.pack_thumbs(scrollable, i, all_src) for i in years_split)
        packed_titles = reversed(tuple(self.pack_title(scrollable, i) for i in self.years))

        for title, row in zip(packed_titles, packed_thumbs):
            title.pack(pady=(15, 15))
            row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

        return parent

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
        self.thumbnails_reload()

    def decode_thumbs(self, thumbs: tuple):
        """
        Prepares encoded images from database for tkinter.
        * input: ((`img`, `src`, `date modified`), ...)
        * returns: list turples: (`ImageTk.PhotoImage`, `src`, `date modified`)
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

    def convert_year(self, thumbs: list):
        """
        Converts image modified date to year
        * input: ((`img`, `src`, `date modified`), ...)
        * returns: list turples: (`ImageTk.PhotoImage`, `src`, `year`)
        """
        result = []
        for img, src, modified in thumbs:
            year = datetime.fromtimestamp(modified).year
            result.append((img, src, year))
        return result

    def years_list(self, thumbs: list):
        """
        Returns list of lists.
        Splits one list of images into images lists by year.
        * param `thumbs`: list tuples (img, src, year)
        # Example

        ```
        imgs = (
            (img, src, 2020), (img2, src, 2017), (img6, src, 2020),
            (img3, src, 2017), ...
            )

        years_list(imgs)
        > [
            [(img, src, 2020), (img2, src, 2020)],
            [(img6, src, 2017), (img3, src, 2017)]
            ]
        ```
        """
        list_years = []
        for y in self.years:
            tmp = tuple(
                (img, src, year) for img, src, year in thumbs if year == y)
            list_years.append(tmp)
        list_years.reverse()
        return list_years

    def pack_thumbs(
        self, master: tkinter.Frame, thumbs: list, all_src: list):
        """
        Returns tkinter frames with packed thumbnails.

        Packs every thumbnail as tkinter label in row.
        Every row is tkinter frame for number thumbnails, based on `self.clmns`
        Binds thumbnail to mouse left click.
        Opens `img_veiewer` on thumbnail click.

        * param `thumbs`: list tuples(decoded img, src, year)
        * param `master`: tkinter frame
        * param `all_src`: list of paths of all images

        # Example
        ```
        thumbnails = list with 27 images
        clmns = 5
        > pack_thumbs function will create 5 rows with 5 images, each row
        > with 5 images. And 6st row with 2 images.
        ```
        """
        year_frame = CFrame(master)

        for i, item in enumerate(thumbs):

            if i % self.clmns == 0:
                row = CFrame(year_frame)
                row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

            thumb = CButton(row)
            thumb.configure(
                width=cfg.THUMB_SIZE, height=cfg.THUMB_SIZE, bg=cfg.BGCOLOR,
                image=item[0],text=item[1])

            thumb.image_names = item[0]
            thumb.cmd(partial(self.open_preview, item[1], all_src))

            thumb.bind('<Enter>', lambda e, a=thumb: self.enter(a))
            thumb.bind('<Leave>', lambda e, a=thumb: self.leave(a))

            thumb.pack(side=tkinter.LEFT)
        
        return year_frame

    def pack_title(self, master: tkinter.Widget, year):
        return CLabel(master, text=year, font=('Arial', 35, 'bold'))

    def enter(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGSELECTED

    def leave(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGCOLOR

    def open_preview(self, src, all_src, e):
        ImgViewer(src, all_src)