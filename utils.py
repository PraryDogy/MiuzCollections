import json
import os
import string
import subprocess
import threading
import tkinter
from difflib import SequenceMatcher

import cv2
import numpy
from PIL import Image

from cfg import conf

__all__ = (
    "get_coll_name",
    "place_center",
    "encode_image",
    "decode_image",
    "convert_to_rgb",
    "crop_image",
    "resize_image",
    "smb_check",
    "find_tiff",
    "find_jpeg",
    "on_exit",
    "replace_bg"
    )


def reveal_finder(list_paths: list):
    paths = (
        f"\"{i}\" as POSIX file"
        for i in list_paths
        )

    paths = ", ".join(paths)

    args = (
        "-e", "tell application \"Finder\"",
        "-e", f"reveal {{{paths}}}",
        "-e", "activate",
        "-e", "end tell",
        )

    subprocess.call(["osascript", *args])


def normalize_name(name: str):
    name, ext = os.path.splitext(name)
    name = name.translate(str.maketrans("", "", string.punctuation))

    for i in conf.stopwords:
        name = name.replace(i, "")

    return name.replace(" ", "")


def find_tiff(src: str):
    path, filename = os.path.split(src)
    src_file_no_ext = normalize_name(filename)
    exts = (".tiff", ".TIFF", ".psd", ".PSD", ".psb", ".PSB", ".tif", ".TIF")
    images = []

    for root, dirs, files in os.walk(path):
        for file in files:

            if file.endswith(exts):

                file_no_ext = normalize_name(file)

                if src_file_no_ext in file_no_ext:
                    images.append(os.path.join(root, file))

                elif file_no_ext in src_file_no_ext and len(file_no_ext) > 5:
                    images.append(os.path.join(root, file))

    if images:
        threading.Thread(target=reveal_finder, args=[images]).start()
        return True
    else:
        return False


def find_jpeg(src: str):
    def task():
        subprocess.call(["open", "-R", src])
    threading.Thread(target = task).start()


def get_coll_name(src: str):
    coll = src.replace(conf.coll_folder, "")
    coll = coll.strip(os.sep)
    return coll.split(os.sep)[0]


def place_center(top_level: tkinter.Toplevel):
    """
    Place new tkinter window to center relavive main window.
    * param `top_level`: tkinter.TopLevel
    """
    x, y = conf.root.winfo_x(), conf.root.winfo_y()
    xx = x + conf.root.winfo_width()//2 - top_level.winfo_width()//2
    yy = y + conf.root.winfo_height()//2 - top_level.winfo_height()//2

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


def replace_bg(image, color: str):
    try:
        trans_mask = image[:,:,3 ] == 0
        color = color.replace("#", "")
        bg_color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        image[trans_mask] = [*bg_color, 255]
    except IndexError:
        return image
    return image


def encode_image(src):
    image = cv2.imread(src, cv2.IMREAD_UNCHANGED)

    if src.endswith((".png", ".PNG")):
        image = replace_bg(image, conf.bg_color)

    resized = resize_image(image, conf.thumb_size, conf.thumb_size, True)

    try:
        return cv2.imencode('.jpg', resized)[1].tobytes()
    except cv2.error:
        print("too big img")


def decode_image(image):
    nparr = numpy.frombuffer(image, numpy.byte)
    return cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)


def convert_to_rgb(image):
    # convert cv2 color to rgb
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # load numpy array image
    img = Image.fromarray(image_rgb)
    return img


def crop_image(img):
    width, height = img.shape[1], img.shape[0]
    if height >= width:
        delta = (height-width)//2
        cropped = img[delta:height-delta, 0:width]
    else:
        delta = (width-height)//2
        cropped = img[0:height, delta:width-delta]
    return cropped[0:conf.thumb_size, 0:conf.thumb_size]


def smb_check():
    """
    Check smb disk avability with os path exists.
    Return bool.
    """
    if not os.path.exists(conf.coll_folder):
        return False
    return True


def on_exit():
    w, h = conf.root.winfo_width(), conf.root.winfo_height()
    x, y = conf.root.winfo_x(), conf.root.winfo_y()

    conf.root_w = w
    conf.root_h = h
    conf.root_x = x
    conf.root_y = y

    conf.write_cfg()

    conf.flag = False
    quit()