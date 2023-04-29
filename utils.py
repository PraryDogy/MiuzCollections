import json
import os
import tkinter

import cv2
import numpy
from PIL import Image

import subprocess
import cfg
import threading

__all__ = (
    "write_cfg",
    "read_cfg",
    "get_coll_name",
    "place_center",
    "encode_image",
    "decode_image",
    "convert_to_rgb",
    "crop_image",
    "resize_image",
    "smb_check",
    "get_windows",
    "close_windows",
    "focus_last",
    "find_tiff",
    "find_jpeg"
    )


def find_tiff(src: str):

    def task(root, file):
        subprocess.call(["open", "-R", os.path.join(root, file)])

    path, filename = os.path.split(src)
    filename = filename.split(".")[0]

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith((".psd", ".PSD", ".tiff", ".TIFF")):
                if filename in file:
                    threading.Thread(target=task, args=[root, file]).start()
                    return True
    return False


def find_jpeg(src: str):
    def task():
        subprocess.call(["open", "-R", src])
    threading.Thread(target = task).start()



def write_cfg(data: dict):
    """
    Converts dict with json dumps and enctypt converted with fernet module.
    Writes enctypted data to `cfg.json` in `cfg.CFG_DIR`
    *param `data`: python dict
    """
    with open(os.path.join(cfg.CFG_DIR, 'cfg.json'), "w") as file:
        file.write(json.dumps(data, indent=4, ensure_ascii=True))


def read_cfg():
    """
    Decrypts `cfg.json` from `cfg.CFG_DIR` and returns dict.
    """
    with open(os.path.join(cfg.CFG_DIR, 'cfg.json'), "r") as file:
        return json.loads(file.read())


def get_coll_name(src: str):
    return src.split(cfg.config['COLL_FOLDER'])[-1].split(os.sep)[1]


def place_center(top_level: tkinter.Toplevel):
    """
    Place new tkinter window to center relavive main window.
    * param `top_level`: tkinter.TopLevel
    """
    x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
    xx = x + cfg.ROOT.winfo_width()//2 - top_level.winfo_width()//2
    yy = y + cfg.ROOT.winfo_height()//2 - top_level.winfo_height()//2

    top_level.geometry(f'+{xx}+{yy}')


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


def encode_image(src):
    image = cv2.imread(src)
    resized = resize_image(image, cfg.THUMB_SIZE, cfg.THUMB_SIZE, True)
    return cv2.imencode('.jpg', resized)[1].tobytes()


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


def smb_check():
    """
    Check smb disk avability with os path exists.
    Return bool.
    """
    if not os.path.exists(cfg.config['COLL_FOLDER']):
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
