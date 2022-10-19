import subprocess
import tkinter

import cfg
from utils.utils import MyButton, MyFrame, MyLabel, my_copy


def images_list():
    """
    Returns list of tkinter image objects.
    `cfg.IMAGES_COMPARE` is set with tkinter image labels.
    """
    return [i.__dict__['image_names'] for i in list(cfg.IMAGE_FRAMES)]


def on_closing(obj):
    """
    Destroys current tkinter toplevel.
    Clears `cfg.IMAGES_COMPARE` list.
    * param `obj`: tkinter toplevel
    """

    prevs = [v for k, v in cfg.ROOT.children.items() if "preview" in k]
    [i.destroy() for i in prevs]
    cfg.IMAGE_FRAMES.clear()
    cfg.IMAGES_INFO.clear()
    cfg.IMAGES_SRC.clear()
    obj.destroy()


class Globals:
    """
    Global variables.
    * `curr_img`: tkinter image object from `images_list()` function.
    * `curr_src`: image source path.
    * `img_frame`: tkinter frame with `curr_img`
    * `info_label`: tkinter label with image info from `image_viewer`
    """
    curr_img = tkinter.Image
    curr_src = str

    img_frame = tkinter.Label
    info_label = tkinter.Label


class ImagesCompare(tkinter.Toplevel):
    """
    A new tkinter window containing two images and
    a button with an image switch.
    You can click the toggle button to see the difference between similar
    images
    """
    def __init__(self):
        prevs = [v for k, v in cfg.ROOT.children.items() if "preview" in k]
        [i.withdraw() for i in prevs]

        tkinter.Toplevel.__init__(self)
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.bind('<Command-w>', lambda e: on_closing(self))
        self.bind('<Command-q>', lambda e: quit())
        self.bind('<Escape>', lambda e: on_closing(self))

        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        ImageFrame(self).pack(fill=tkinter.BOTH, expand=True, pady=(0, 15))
        ImgButtons(self).pack(pady=(0, 15))
        NamePath(self).pack(pady=(0, 15), anchor=tkinter.CENTER)
        CloseBtn(self).pack()

        cfg.ROOT.update_idletasks()
        self.geometry(f'+{cfg.ROOT.winfo_x() + 100}+{cfg.ROOT.winfo_y()}')
        self.deiconify()


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'

        Globals.curr_img = images_list()[0]
        Globals.img_frame = self
        Globals.curr_src = cfg.IMAGES_SRC[0]

        self.configure(
            image=Globals.curr_img,
            width=Globals.curr_img.height(),
            height=Globals.curr_img.height()
            )


class ImgButtons(MyFrame):
    """
    Tkinter frame with buttons:
    * copy image name
    * open image folder
    * switch to second image
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        b_wight = 13

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=b_wight)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        open_btn = MyButton(self, text='Папка с фото')
        open_btn.configure(height=1, width=b_wight)
        open_btn.cmd(lambda e: self.open_folder(open_btn))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        toogle = MyButton(self, text='Переключить')
        toogle.configure(height=1, width=b_wight)
        toogle.cmd(lambda e: self.switch_image(toogle))
        toogle.pack(side=tkinter.LEFT, padx=(0, 0))

    def copy_name(self, btn):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        get_name = Globals.curr_src.split('/')[-1].split('.')[0]
        my_copy(get_name)

    def open_folder(self, btn):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = '/'.join(Globals.curr_src.split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])

    def switch_image(self, btn):
        """
        Switches between two images from cfg.IMAGES_COMPARE set.
        """
        btn.press()

        Globals.curr_img = [
            i for i in images_list() if i != Globals.curr_img][0]

        Globals.curr_src = [
            i for i in cfg.IMAGES_SRC if i != Globals.curr_src][0]

        image_info = [
            i for i in cfg.IMAGES_INFO if i != Globals.info_label['text']][0]

        Globals.img_frame.configure(image=Globals.curr_img)
        Globals.info_label.configure(text=image_info)


class NamePath(MyLabel):
    """
    Creates tkinter frame with image info.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyLabel.__init__(
            self, master, anchor=tkinter.W, justify=tkinter.LEFT,
            text=cfg.IMAGES_INFO[0], width=40)
        Globals.info_label = self


class CloseBtn(MyButton):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=2)
        self.cmd(lambda e: on_closing(self.winfo_toplevel()))
