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

import cv2
import numpy
from cryptography.fernet import Fernet
from PIL import Image

import cfg


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


def resize_image(img, widget_w, widget_h, thumbnail: bool):
    h, w = img.shape[:2]
    aspect = w/h
    if thumbnail:
        if aspect > 1:
            new_h, new_w = widget_h, round(widget_h*aspect)
        elif aspect < 1:
            new_h, new_w = round(widget_w/aspect), widget_w
        elif aspect == 1:
            new_h, new_w = widget_h, widget_h
    else:
        f1 = widget_w / w
        f2 = widget_h / h
        # f = min(f1, f2)
        f = f2
        new_w, new_h = (int(w * f), int(h * f))

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


def get_windows():
    all = tuple(i for i in cfg.ROOT.winfo_children())
    return tuple(i for i in all if isinstance(i, tkinter.Toplevel))


def close_windows():
    "Close all top levels"
    if cfg.COMPARE:
        cfg.COMPARE = False

    [i.destroy() for i in get_windows()]
    cfg.ROOT.focus_force()


def focus_last():
    "Sets focus to last opened window or root"
    wins = get_windows()
    [wins[-1].focus_force() if len(wins) > 0 else cfg.ROOT.focus_force()]
