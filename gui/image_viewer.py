"""
Gui for view image.
"""

import os
import subprocess
import tkinter
from datetime import datetime
from turtle import width

import cfg
from PIL import Image, ImageTk
from utils.utils import (MyButton, MyFrame, MyLabel, SmbChecker, get_coll_name,
                         my_copy)

from .images_compare import ImagesCompare

vars = {
    'img_src': '', 
    'img_info': '',
    'img_frame': '',
    'curr_img': '',
    }


def on_closing(obj=tkinter.Frame):
    """
    Destroys current tkinter toplevel.
    Clears `cfg.IMAGES_COMPARE` list.
    * param `obj`: tkinter toplevel
    """

    obj.destroy()


class ImagePreview(tkinter.Toplevel):
    """
    Creates new window (tkinter Top Level) with image & buttons.
    * param `src`: source path of image.
    """
    def __init__(self, src):
        vars['img_src'] = src

        tkinter.Toplevel.__init__(self)
        self.withdraw()

        if not SmbChecker().check():
            return

        if src is None:
            return

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.bind('<Command-w>', lambda e: on_closing(self))
        self.bind('<Escape>', lambda e: on_closing(self))

        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        ImgSrc(self)
        ImageFrame(self).pack(fill=tkinter.BOTH, expand=True)
        ImgButtons(self).pack(pady=(15, 15))
        ImgInfo(self).pack(pady=(0, 15), padx=15)
        CloseButton(self).pack()

        cfg.ROOT.update_idletasks()

        self.geometry(f'+{cfg.ROOT.winfo_x() + 100}+{cfg.ROOT.winfo_y()}')
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
        vars['curr_img'] = Image.open(vars['img_src'])

        self['bg']='black'
        self.bind("<Configure>", lambda e: self.resize(e))

    def resize(self, e):
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

        filesize = round(os.path.getsize(vars['img_src'])/(1024*1024), 2)
        filemod = datetime.fromtimestamp(os.path.getmtime(vars['img_src']))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
        img_w, img_h = vars['curr_img'].width, vars['curr_img'].height
        name = vars['img_src'].split(os.sep)[-1]

        txt = (f'Коллекция: {get_coll_name(vars["img_src"])}'
                f'\nИмя: {name}'
                f'\nПуть: {vars["img_src"]}'
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
            open_btn = MyButton(self, text='Папка с фото')
            open_btn.configure(height=1, width=b_wight)
            open_btn.cmd(lambda e: self.open_folder(open_btn))
            open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def compare(self, btn):
        """
        Compares two images and open gui with result.
        * param `btn`: current tkinter button.
        """
        btn.press()

        prevs = [i for i in cfg.ROOT.children if 'preview' in i]
        if len(prevs) != 2:

            old_txt = vars['img_info']['text']
            txt = '\n\n\nДолжно быть открыто только два изображения.\n\n'
            vars['img_info']['text'] = txt
            vars['img_info']['anchor'] = tkinter.CENTER
            cfg.ROOT.after(
                1500, lambda: vars['img_info'].configure(text=old_txt))
            cfg.ROOT.after(
                1500, lambda: vars['img_info'].configure(anchor=tkinter.W))
            return

        ImagesCompare()

    def copy_name(self, btn):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        my_copy(vars['img_src'].split('/')[-1].split('.')[0])

    def open_folder(self, btn):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = '/'.join(vars['img_src'].split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])


class CloseButton(MyButton):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=2)
        self.cmd(lambda e: on_closing(self.winfo_toplevel()))
