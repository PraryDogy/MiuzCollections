import tkinter
import cfg
from utils.utils import MyLabel, MyButton, MyFrame

def images_list():
    return [i.__dict__['image_names'] for i in list(cfg.IMAGES_COMPARE)]


class Globals:
    curr_img = tkinter.Image
    img_frame = tkinter.Label


class CompareNew(tkinter.Toplevel):
    def __init__(self):
        tkinter.Toplevel.__init__(self)

        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        

        ImageFrame(self).pack(fill=tkinter.BOTH, expand=True)
        Tumbler(self).pack()

        self.grab_set()


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'

        Globals.curr_img = images_list()[0]
        self.configure(image=Globals.curr_img)
        Globals.img_frame = self



class Tumbler(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='Переключить')
        self.cmd(lambda e: self.param())

    def param(self):
        images = images_list()

        ind = 0 if images_list().index(Globals.curr_img) == 1 else 1
        Globals.img_frame.configure(image=images[ind])
        Globals.curr_img = images[ind]
        