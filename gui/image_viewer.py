"""
Gui for view image.
"""

import os
import subprocess
import threading
import tkinter
from datetime import datetime

import cfg
from PIL import Image, ImageTk
from utils import (MyButton, MyFrame, MyLabel, get_coll_name, my_copy,
                   place_center, smb_check)

from .images_compare import ImagesCompare
from .smb_checker import SmbChecker

vars = {
    'img_src': str,
    'all_src': list,
    'img_info': tkinter.Label,
    'img_frame': tkinter.Label,
    'curr_img': Image,
    }


def pack_widgets(master):
    ImgSrc(master)
    ImageFrame(master).pack(fill=tkinter.BOTH, expand=True)

    left_frame = MyFrame(master)
    left_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    PrevItem(left_frame).pack(expand=True, fill=tkinter.BOTH)

    center_frame = MyFrame(master)
    center_frame.pack(side=tkinter.LEFT)
    ImgButtons(center_frame).pack(pady=(15, 15))
    ImgInfo(center_frame).pack(pady=(0, 15), padx=15)
    CloseButton(center_frame).pack()

    right_frame = MyFrame(master)
    right_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    NextItem(right_frame).pack(expand=True, fill=tkinter.BOTH)


class ImagePreview(tkinter.Toplevel):
    """
    Creates new window (tkinter Top Level) with image & buttons.
    * param `src`: source path of image.
    """
    def __init__(self, src, all_src):
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        if not smb_check():
            SmbChecker()
            return

        if src is None:
            return

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind('<Command-w>', lambda e: self.destroy())
        self.bind('<Escape>', lambda e: self.destroy())

        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        vars['img_src'] = src
        vars['all_src'] = all_src

        pack_widgets(self)
        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()



class ImgSrc(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, text=vars['img_src'])


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, borderwidth=0)
        vars['img_frame'] = self
        img = Image.open(vars['img_src'])
        vars['curr_img'] = img.copy()

        self['bg']='black'
        self.bind("<Configure>", lambda e: self.resize(e))

    def resize(self, e=tkinter.Event):
        """
        Fits image to label size.
        * param `img`: current image.
        """
        self.unbind("<Configure>")

        size = (e.width, e.height)
        vars['curr_img'].thumbnail(size)
        img_tk = ImageTk.PhotoImage(vars['curr_img'])

        self.configure(image=img_tk)
        self.image = img_tk


class ImgInfo(MyLabel):
    """
    Creates tkinter frame.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master)
        vars['img_info'] = self

        name = vars['img_src'].split(os.sep)[-1]
        path = vars["img_src"].replace(cfg.config["COLL_FOLDER"], "Коллекции")
        path = path.replace(cfg.config["PHOTO_DIR"], "Фото")
        img_w, img_h = vars['curr_img'].width, vars['curr_img'].height
        filesize = round(os.path.getsize(vars['img_src'])/(1024*1024), 2)
        filemod = datetime.fromtimestamp(os.path.getmtime(vars['img_src']))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")

        txt = (f'Коллекция: {get_coll_name(vars["img_src"])}'
                f'\nИмя: {name}'
                f'\nПуть: {path}'
                f'\nРазрешение: {img_w} x {img_h}'
                f'\nРазмер: {filesize} мб'
                f'\nДата изменения: {filemod}')

        self.configure(
            text=txt, justify=tkinter.LEFT, anchor=tkinter.W, width=50)


class ImgButtons(MyFrame):
    """
    Tkinter frame with button that calls images compare method.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        b_wight = 13

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=b_wight)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        comp_btn = MyButton(self, text='Сравнить')
        comp_btn.configure(height=1, width=b_wight)
        comp_btn.cmd(lambda e: self.compare(comp_btn))
        comp_btn.pack(side=tkinter.RIGHT)

        if os.path.exists(vars['img_src']):
            open_btn = MyButton(self, text='Открыть папку')
            open_btn.configure(height=1, width=b_wight)
            open_btn.cmd(lambda e: self.open_folder(open_btn))
            open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def compare(self, btn: MyButton):
        """
        Compares two images and open gui with result.
        * param `btn`: current tkinter button.
        """
        btn.press()

        prevs = [i for i in cfg.ROOT.children if 'preview' in i]
        if len(prevs) != 2:

            old_txt = vars['img_info']['text']
            txt = '\n\n\nДолжно быть открыто два изображения.\n\n'
            vars['img_info']['text'] = txt
            vars['img_info']['anchor'] = tkinter.CENTER
            cfg.ROOT.after(
                1500, lambda: vars['img_info'].configure(text=old_txt))
            cfg.ROOT.after(
                1500, lambda: vars['img_info'].configure(anchor=tkinter.W))
            return

        ImagesCompare()

    def copy_name(self, btn: MyButton):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        my_copy(vars['img_src'].split('/')[-1].split('.')[0])

    def open_folder(self, btn: MyButton):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = '/'.join(vars['img_src'].split('/')[:-1])

        def open():
            subprocess.check_output(["/usr/bin/open", path])

        threading.Thread(target=open).start()


class CloseButton(MyButton):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=2)
        self.cmd(lambda e: self.winfo_toplevel().destroy())


def switch_image(master: tkinter.Toplevel, index: int):
    try:
        vars['img_src'] = vars['all_src'][index]
    except IndexError:
        vars['img_src'] = vars['all_src'][0]
    master = master.winfo_toplevel()
    for i in master.winfo_children():
        i.destroy()


    pack_widgets(master)


class NextItem(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='Вперед')
        self.configure(bg=cfg.BGCOLOR)
        self.winfo_toplevel().bind('<Right>', lambda e: self.next_img())
        self.cmd(lambda e: self.next_img())

    def next_img(self):
        index = vars['all_src'].index(vars['img_src']) + 1
        switch_image(self, index)


class PrevItem(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='Назад')
        self.configure(bg=cfg.BGCOLOR)
        self.winfo_toplevel().bind('<Left>', lambda e: self.prev_img())
        self.cmd(lambda e: self.prev_img())

    def prev_img(self):
        index = vars['all_src'].index(vars['img_src']) - 1
        switch_image(self, index)