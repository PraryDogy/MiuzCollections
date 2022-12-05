"""
* create_thumb
* my_copy
* my_paste
* smb_check
* MyButton
* MyFrame
* MyLabel
"""

import json
import os
import subprocess
import tkinter

import cfg
import cv2
import numpy
from cryptography.fernet import Fernet
from PIL import Image


def encrypt_cfg(data: dict):
    """
    Converts dict with json dumps and enctypt converted with fernet module.
    Writes enctypted data to `cfg.json` in `cfg.CFG_DIR`
    *param `data`: python dict
    """
    key = Fernet(cfg.KEY)
    encrypted = key.encrypt(json.dumps(data).encode("utf-8"))
    with open(os.path.join(cfg.CFG_DIR, 'cfg'), 'wb') as file:
        file.write(encrypted)


def get_coll_name(src: str):
    """
    Returns collection name.
    Returns `Без коллекций` if name not found.

    Looking for collection name in path like object.
    Name of collection must be follow next to `cfg.COLL_FOLDER`

    # Example
    ```
    cfg.COLL_FOLDER = "collection"
    collection_path = /path/to/collection/any_collection_name
    print(get_coll_name(collection_path))
    > any_collection_name

    cfg.COLL_FOLDER = "collection"
    collection_path = /some/path/without/coll_folder
    print(get_coll_name(collection_path))
    > Без коллекций
    ```
    """
    coll_name = 'Без коллекций'
    if cfg.config['COLL_FOLDER'] in src:
        coll_name = src.split(cfg.config['COLL_FOLDER'])[-1].split(os.sep)[1]
    return coll_name


def place_center(top_level: tkinter.Toplevel):
    """
    Place new tkinter window to center relavive main window.
    * param `top_level`: tkinter.TopLevel
    """
    x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
    xx = x + cfg.ROOT.winfo_width()//2 - top_level.winfo_width()//2
    yy = y + cfg.ROOT.winfo_height()//2 - top_level.winfo_height()//2

    top_level.geometry(f'+{xx}+{yy}')


def decode_image(image):
    """
    Decodes from bytes to numpy array. Returns numpy array.
    * param `image`: bytes image.
    """
    nparr = numpy.frombuffer(image, numpy.byte)
    return cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)


def convert_to_rgb(image):
    """
    Converts numpy array BGR to RGB, converts numpy array to img object.
    Returns converted image.
    * param `image`: BGR numpy array image.
    """
    # convert cv2 color to rgb
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # load numpy array image
    img = Image.fromarray(image_rgb)
    return img


def crop_image(img):
    """
    Crops numpy array image to square. Returns cropped image.
    * param `img`: numpy array image.
    """
    width, height = img.shape[1], img.shape[0]
    if height >= width:
        delta = (height-width)//2
        cropped = img[delta:height-delta, 0:width]
    else:
        delta = (width-height)//2
        cropped = img[0:height, delta:width-delta]
    return cropped[0:cfg.THUMB_SIZE, 0:cfg.THUMB_SIZE]


# def resize_image(img, ww, hh, thumbnail: bool):
#     print(ww, hh)
#     h, w = img.shape[:2]
#     aspect = w/h
#     hh1, ww1 = round(ww/aspect), ww
#     hh2, ww2 = hh, round(hh*aspect)
#     if thumbnail:
#         if aspect > 1:
#             hh, ww = hh2, ww2
#         elif aspect < 1:
#             hh, ww = hh1, ww1
#         elif aspect == 1:
#             hh, ww = hh, hh
#     else:
#         if aspect > 1:
#             hh, ww = hh1, ww1
#         elif aspect < 1:
#             hh, ww = hh2, ww2
#         elif aspect == 1:
#             hh, ww = hh, hh
#     return cv2.resize(img, (ww, hh), interpolation=cv2.INTER_AREA)


def resize_image(img, widget_w, widget_h, thumbnail: bool):
    h, w = img.shape[:2]
    aspect = w/h
    hh1, ww1 = round(widget_w/aspect), widget_w
    hh2, ww2 = widget_h, round(widget_h*aspect)
    if thumbnail:
        if aspect > 1:
            new_h, new_w = hh2, ww2
        if aspect < 1:
            new_h, new_w = hh1, ww1
        elif aspect == 1:
            new_h, new_w = widget_h, widget_h
    else:
        if aspect > 1:
            new_h, new_w = hh1, ww1
        elif aspect < 1:
            new_h, new_w = hh2, ww2
        elif aspect == 1:
            new_h, new_w = widget_h, widget_h
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def my_copy(output: str):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))


def my_paste():
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


def smb_check():
    """
    Check smb disk avability with os path exists.
    Return bool.
    """
    if not os.path.exists(cfg.config['PHOTO_DIR']):
        return False
    return True


class MySep(tkinter.Frame):
    def __init__(self, master, **kwargs):
        tkinter.Frame.__init__(self, master, bg=cfg.BGBUTTON, height=1)


class MyButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGBUTTON, fg=cfg.BGFONT)
        self.bind('<Enter>', lambda e: self.enter())
        self.bind('<Leave>', lambda e: self.leave())

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)

    def press(self):
        self.configure(bg=cfg.BGPRESSED)
        cfg.ROOT.after(100, lambda: self.configure(bg=cfg.BGBUTTON))

    def enter(self):
        if self['bg'] != cfg.BGPRESSED:
            self['bg'] = cfg.BGSELECTED

    def leave(self):
        if self['bg'] != cfg.BGPRESSED:
            self['bg'] = cfg.BGBUTTON

class MyFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Frame.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR)


class MyLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR, fg=cfg.BGFONT)


# unused


# class Scrollable(tkinter.Frame):
    # """
    # Example scrollable frame.
    # """
    # def __init__(self, master):
    #     tkinter.Frame.__init__(self, master)

    #     canvas = tkinter.Canvas(
    #         self, bg=cfg.BGCOLOR, highlightbackground=cfg.BGCOLOR)

    #     scrollbar = tkinter.Scrollbar(
    #         self, width=12, orient='vertical', command=canvas.yview)

    #     scrollable = tkinter.Frame(canvas)

    #     scrollable.bind("<Configure>", lambda e: canvas.configure(
    #         scrollregion=canvas.bbox("all")))

    #     canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
    #         -1*(e.delta), "units"))
    #         # lambda e: canvas.yview_scroll(-1*(e.delta/120), "units")

    #     canvas.create_window((0,0), window=scrollable, anchor='nw')
    #     canvas.configure(yscrollcommand=scrollbar.set)

    #     self.pack(fill=tkinter.BOTH, expand=True)
    #     canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
    #     scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)


    # def image_resize(self, image, width = None, height = None, inter = cv2.INTER_AREA):
    #     # initialize the dimensions of the image to be resized and
    #     # grab the image size
    #     image = cv2.imread(image)
    #     dim = None
    #     (h, w) = image.shape[:2]

    #     # if both the width and height are None, then return the
    #     # original image
    #     if width is None and height is None:
    #         return image

    #     # check to see if the width is None
    #     if width is None:
    #         # calculate the ratio of the height and construct the
    #         # dimensions
    #         r = height / float(h)
    #         dim = (int(w * r), height)

    #     # otherwise, the height is None
    #     else:
    #         # calculate the ratio of the width and construct the
    #         # dimensions
    #         r = width / float(w)
    #         dim = (width, int(h * r))

    #     # resize the image
    #     resized = cv2.resize(image, dim, interpolation = inter)

    #     # return the resized image
    #     return resized
