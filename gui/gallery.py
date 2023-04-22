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


def clmns_count():
    return (cfg.config['ROOT_W'] - 180)//cfg.THUMB_SIZE


def decode_thumbs(thumbs: tuple):
    """
    Prepares images from database for tkinter.
    * input: ((`img`, `src`, `date modified`), ...)
    * returns: ((`img`, `src`, `date modified`), ...)
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

def convert_year(thumbs: list):
    """
    Converts timestamp to year
    * input: ((`img`, `src`, `date modified`), ...)
    * returns: ((`img`, `src`, `year`), ...)
    """
    result = []
    for img, src, modified in thumbs:
        year = datetime.fromtimestamp(modified).year
        result.append((img, src, year))
    return result


class Gallery(CFrame):
    """
    Creates tkinter frame with menu and grid of images.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        CFrame.__init__(self, master)
        cfg.GALLERY = self

        self.menu_parrent = self.load_menu_parent(self)
        self.menu_parrent.pack(fill=tkinter.Y, side=tkinter.LEFT)

        self.menu_buttons = self.load_menu_buttons()
        self.menu_buttons.pack()

        cfg.ROOT.update_idletasks()

        self.thumbs_widget = self.load_thumbs_widget(self)
        self.thumbs_widget.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

        self.clmns = 0

        cfg.ROOT.bind('<ButtonRelease-1>', self.update_gui)

    def load_menu_parent(self, master):
        frame = tkmacosx.SFrame(
            master,
            bg = cfg.BGCOLOR,
            scrollbarwidth = 7,
            width = 180
            )

        parent = CFrame(frame)
        parent.pack(padx=15)

        self.compare_frame = CFrame(parent)

        self.compare_title = CLabel(self.compare_frame)
        self.compare_title.pack()

        self.compare_img = CLabel(self.compare_frame)
        self.compare_img.pack(pady=(0, 15))

        menu_frame = CFrame(parent)
        menu_frame.pack(side=tkinter.BOTTOM)

        return frame

    def load_menu_buttons(self):
        frame = CFrame(self.menu_parrent)

        title = CLabel(
            frame, text='Коллекции', font=('Arial', 22, 'bold'))
        title.pack(pady=(0,15))

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(Thumbs.collection)
            .distinct()
            ).fetchall()
        colls_list = (i[0] for i in colls_list)


        menus = {
            coll: re.sub(r'[^a-zA-Zа-яА-Я ]+', '', coll).lstrip()[:13]
            for coll in colls_list
            }

        menus = dict(
            sorted(
                menus.items(),
                key=lambda item: item[1].casefold()
                ))

        btns = []

        last = CButton(frame, text='Последние')
        last.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
        last.cmd(partial(self.open_coll_folder, 'last', last, btns))
        last.pack(fill=tkinter.X, pady=(0, 15))
        btns.append(last)

        for full_name, name in menus.items():
            btn = CButton(frame, text = name)
            btn.configure(width=13, pady=5, anchor=tkinter.W, padx=10)
            btn.cmd(partial(self.open_coll_folder, full_name, btn, btns))
            btn.pack(fill=tkinter.X)
            btns.append(btn)

            if full_name == cfg.config['CURR_COLL']:
                btn.configure(bg=cfg.BGPRESSED)

            sep = CSep(frame)
            sep['bg'] = '#272727'
            sep.pack(fill=tkinter.X)
    
        if cfg.config['CURR_COLL'] == 'last':
            last.configure(bg=cfg.BGPRESSED)

        return frame

    def load_thumbs_widget(self, master: tkinter):
        frame = CFrame(master)
        scrollable = tkmacosx.SFrame(frame, bg=cfg.BGCOLOR, scrollbarwidth=7)
        scrollable.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

        self.clmns = clmns_count()

        title = CLabel(
            scrollable,
            text=cfg.config['CURR_COLL'],
            font=('Arial', 45, 'bold')
            )
        title.pack(pady=(0, 15))

        if cfg.config['CURR_COLL'] == 'last':
            title.configure(text='Последние добавленные')

            res = Dbase.conn.execute(
                sqlalchemy.select(
                    Thumbs.img150,
                    Thumbs.src,
                    Thumbs.modified
                    ).order_by(-Thumbs.modified)
                    ).fetchall()
        else:
            res = Dbase.conn.execute(
                sqlalchemy.select(
                    Thumbs.img150,
                    Thumbs.src,
                    Thumbs.modified
                    ).where(
                    Thumbs.collection == cfg.config['CURR_COLL']
                    ).order_by(
                    -Thumbs.modified)
                    ).fetchall()

        thumbs = decode_thumbs(res)
        thumbs = convert_year(thumbs)
        all_src = [src for img, src, year in thumbs]

        thumbs_dict = {}
        for img, src, year in thumbs:
            thumbs_dict.setdefault(year, []).append((img, src))

        for year, img_list in thumbs_dict.items():

            year_frame = CLabel(
                scrollable,
                font=('Arial', 35, 'bold'),
                text=year,
                )
            year_frame.pack(pady=15)

            img_row = CFrame(scrollable)
            img_row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

            for x, (img, src) in enumerate(img_list, 1):

                thumb = CButton(img_row)
                thumb.configure(
                    width = cfg.THUMB_SIZE,
                    height = cfg.THUMB_SIZE,
                    bg=cfg.BGCOLOR,
                    image = img,
                    text = src
                    )
                thumb.pack(side=tkinter.LEFT)

                thumb.image_names = img
                thumb.cmd(partial(self.open_preview, src, all_src))

                thumb.bind('<Enter>', lambda e, a=thumb: self.enter(a))
                thumb.bind('<Leave>', lambda e, a=thumb: self.leave(a))

                if x % self.clmns == 0:
                    img_row = CFrame(scrollable)
                    img_row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

        return frame

    def update_gui(self, e: tkinter.Event):
        old_w = cfg.config['ROOT_W']
        new_w = cfg.ROOT.winfo_width()

        if new_w != old_w:
            cfg.config['ROOT_W'] = new_w

            if self.clmns != clmns_count():
                self.reload_thumbs()

    def reload_thumbs(self):
        """
        External use
        Destroys `ImagesThumbs` object and run it again.
        """
        w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
        cfg.config['ROOT_W'], cfg.config['ROOT_H'] = w, h

        self.thumbs_widget.destroy()

        self.thumbs_widget = self.load_thumbs_widget(self)
        self.thumbs_widget.pack(expand=1, fill=tkinter.BOTH, side=tkinter.RIGHT)

    def reload_menu(self):
        """
        External use
        """
        self.menu_buttons.destroy()
        self.menu_buttons = self.load_menu_buttons()
        self.menu_buttons.pack()
        return

    def place_thumb(self, thumbnail):
        """
        External use
        """
        cropped = crop_image(thumbnail)
        rgb_thumb = convert_to_rgb(cropped)
        img_tk = ImageTk.PhotoImage(rgb_thumb)

        self.compare_img['image'] = img_tk
        self.compare_img.image_names = img_tk

        self.compare_title['text'] = 'В списке сравнения:'

        self.compare_frame.pack(side=tkinter.TOP)

    def remove_thumb(self):
        """
        External use
        """
        self.compare_img['image'] = ''
        self.compare_title['text'] = ''
        self.compare_frame.pack_forget()

    def open_coll_folder(self, coll: str, btn: CButton, btns: list, e):
        if coll != "last":
            coll_path = os.path.join(
                cfg.config['COLL_FOLDER'],
                coll
                )
        else:
            coll_path = cfg.config['COLL_FOLDER']

        if btn['bg'] == cfg.BGPRESSED:
            btn['bg'] = cfg.BGSELECTED

            cfg.ROOT.after(
                200,
                lambda: btn.configure(bg=cfg.BGPRESSED)
                )

            subprocess.check_output(["/usr/bin/open", coll_path])
            return

        for btn_item in btns:
            btn_item['bg'] = cfg.BGBUTTON

        btn['bg'] = cfg.BGPRESSED
        cfg.config['CURR_COLL'] = coll

        self.reload_thumbs()

    def enter(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGSELECTED

    def leave(self, thumb: CButton):
        if thumb['bg'] != cfg.BGPRESSED:
            thumb['bg'] = cfg.BGCOLOR

    def open_preview(self, src, all_src, e):
        ImgViewer(src, all_src)