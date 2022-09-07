from email.mime import image
import tkinter

import cfg
from utils.utils import Compare, MyLabel
from PIL import Image, ImageTk


class ImagesCompare(tkinter.Toplevel):
    def __init__(self):
        tkinter.Toplevel.__init__(self)

        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        image1, image2 = Compare()
        ImageFrame(image1).pack(fill=tkinter.BOTH, expand=True, side=tkinter.LEFT)
        ImageFrame(image2).pack(fill=tkinter.BOTH, expand=True, side=tkinter.RIGHT)


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master, image):
        self.master = master
        img_src = Image.open(image)
        img_copy= img_src.copy()

        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self.bind("<Configure>", lambda e: self.resize(e, img_copy))

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