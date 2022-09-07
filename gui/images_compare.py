import threading
import tkinter

import cfg
import cv2
from PIL import Image, ImageTk
from utils.utils import Compare, MyLabel
import numpy

class ImagesCompare(tkinter.Toplevel):
    def __init__(self):
        tkinter.Toplevel.__init__(self)
        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.8)}x{side}+{0}+{0}')

        anal_lbl = tkinter.Label(self, text='Анализирую')
        anal_lbl.pack()

        tsk = threading.Thread(target=Compare)
        tsk.start()

        while tsk.is_alive():
            cfg.ROOT.update()

        if cfg.IMAGES_COMPARED[0] is None:
            error = tkinter.Label(self, text='Ошибочка')
            error.pack()
            return

        anal_lbl.destroy()
        
        ImageFrame(
            self, cfg.IMAGES_COMPARED[0]).pack(
                fill=tkinter.BOTH, expand=True, side=tkinter.LEFT)
        
        ImageFrame(
            self, cfg.IMAGES_COMPARED[1]).pack(
                fill=tkinter.BOTH, expand=True, side=tkinter.RIGHT)


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master, image):
        self.master = master

        conv = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_RGB = Image.fromarray(conv)

        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self.bind("<Configure>", lambda e: self.resize(e, image_RGB))

    def resize(self, e, img):
        """
        Fits image to label size.
        * param `img`: current image.
        """
        size = (e.width, e.height)
        img.thumbnail(size)
        img = ImageTk.PhotoImage(img)

        self.configure(image=img)
        self.image_names = img
