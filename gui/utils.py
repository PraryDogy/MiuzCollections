import os
import shutil
import string
import subprocess
import threading
import tkinter
import traceback
from time import sleep

import cv2
import numpy
import psd_tools
import sqlalchemy
import tifffile
from PIL import Image, ImageChops

from cfg import cnf
from database import *


__all__ = (
    "apply_filter",
    "black_borders",
    "cancel_utils_task",
    "convert_to_rgb",
    "copy_text",
    "crop_image",
    "db_remove_img",
    "decode_image",
    "encode_image",
    "find_tiffs",
    "focus_last_win",
    "get_coll_name",
    "on_exit",
    "paste_search",
    "place_center",
    "replace_bg",
    "resize_image",
    "reveal_coll",
    "run_applescript",
    "smb_check",
    "finder_actions"
    )




# ********************system utils********************

utils_task = threading.Thread(target=None)


def run_utils_task(fn, args=[], kwargs={}):
    global utils_task
    utils_task = threading.Thread(
        target=fn, args=args, kwargs=kwargs, daemon=True
        )
    utils_task.start()


def wait_utils_task():
    while utils_task.is_alive():
        cnf.root.update()


def cancel_utils_task():
    cnf.topbar_flag = False
    wait_utils_task()
    cnf.topbar_default()


def delay():
    sleep(2)


def dec_utils_task(task):
    def wrapper(*args, **kwargs):
        wait_utils_task()
        run_utils_task(task, args, kwargs)
        wait_utils_task()
        cnf.topbar_default()
        wait_utils_task()
        cnf.topbar_flag = True
    return wrapper


def run_applescript(applescript: str):
    args = [
        arg for row in applescript.split("\n")
        for arg in ("-e", row.strip())
        if row.strip()
        ]
    subprocess.call(["osascript"] + args)


def write_err():
    if not os.path.exists(cnf.cfg_dir):
        os.mkdir(cnf.cfg_dir)

    file = os.path.join(cnf.cfg_dir, "err.txt")

    if not os.path.exists(file):
        with open(file, "w") as err_file:
            pass

    with open(file, "r") as err_file:
        data = err_file.read()

    data = f"{data}\n\n{traceback.format_exc()}"

    with open(file, "w") as err_file:
        print(data, file=err_file)


def normalize_name(name: str):
    name, ext = os.path.splitext(name)
    name = name.translate(str.maketrans("", "", string.punctuation))

    for i in ("preview", "1x1", "1х1", "crop", "копия", "copy", "small"):
        name = name.replace(i, "")

    return name.replace(" ", "")


def smb_check():
    return bool(os.path.exists(cnf.coll_folder))


def on_exit(e=None):
    w, h = cnf.root.winfo_width(), cnf.root.winfo_height()
    x, y = cnf.root.winfo_x(), cnf.root.winfo_y()

    cnf.root_g["w"] = w
    cnf.root_g["h"] = h
    cnf.root_g["x"] = x
    cnf.root_g["y"] = y

    cnf.write_cfg()

    cnf.topbar_flag = False
    cnf.scan_flag = False
    quit()


def get_coll_name(src: str):
    coll = src.replace(cnf.coll_folder, "").strip(os.sep).split(os.sep)

    if len(coll) > 1:
        return coll[0]
    else:
        return cnf.coll_folder.strip(os.sep).split(os.sep)[-1]


def place_center(parrent: tkinter.Toplevel, win: tkinter.Toplevel, w, h):
    x, y = parrent.winfo_x(), parrent.winfo_y()
    xx = x + parrent.winfo_width()//2 - w//2
    yy = y + parrent.winfo_height()//2 - h//2
    win.geometry(f"+{xx}+{yy}")


def reveal_coll(coll_name):
    if coll_name != cnf.all_colls:
        coll_path = os.path.join(cnf.coll_folder, coll_name)
    else:
        coll_path = cnf.coll_folder

    try:
        subprocess.check_output(["/usr/bin/open", coll_path])
    except subprocess.CalledProcessError:
        subprocess.check_output(["/usr/bin/open", cnf.coll_folder])


def paste_search():
    try:
        pasted = cnf.root.clipboard_get().strip()
        cnf.search_var.set(pasted)
    except tkinter.TclError:
        print("no clipboard")


def focus_last_win():
    for k, v in cnf.root.children.items():
        if v.widgetName == "toplevel":
            v.focus_force()
            v.grab_set_global()
            return
    cnf.root.focus_force()




# ********************image utils********************

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
        image = replace_bg(image, cnf.bg_color)

    resized = resize_image(image, cnf.thumb_size-3, cnf.thumb_size-3, True)

    try:
        return cv2.imencode(".jpg", resized)[1].tobytes()
    except cv2.error:
        print("too big img")


def decode_image(image):
    try:
        nparr = numpy.frombuffer(image, numpy.byte)
        return cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
    except TypeError:
        print("utils.py decode_image NoneType instead bytes like img")
        return decode_image(encode_image(cnf.thumb_err))


def convert_to_rgb(image):
    # convert cv2 color to rgb
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # load numpy array image
    return Image.fromarray(image_rgb)


def crop_image(img):
    width, height = img.shape[1], img.shape[0]
    if height >= width:
        delta = (height-width)//2
        cropped = img[delta:height-delta, 0:width]
    else:
        delta = (width-height)//2
        cropped = img[0:height, delta:width-delta]
    return cropped[0:cnf.thumb_size-3, 0:cnf.thumb_size-3]


def black_borders(img: Image):
    try:
        bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()

        if bbox:
            img = img.crop(bbox)

        return img

    except Exception as e:
        print("utils > black_borders > can't crop PSD")
        print(e)
        return img



# ********************finder utils********************

def find_tiffs(src: str):
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
        return images
    else:
        return False


def reveal_files(list_paths: list):
    cnf.topbar_text(cnf.lng.please_wait)

    paths = (
        f"\"{i}\" as POSIX file"
        for i in list_paths
        )

    paths = ", ".join(paths)

    applescript = f"""
        tell application \"Finder\"
        reveal {{{paths}}}
        activate
        end tell
        """

    run_applescript(applescript)


def db_remove_img(src):
    q = (
        sqlalchemy.delete(Thumbs).filter(
            Thumbs.src==src
            ))
    Dbase.conn.execute(q)
    cnf.reload_thumbs()


def copy_text(text):
    cnf.root.clipboard_clear()
    cnf.root.clipboard_append(text)


def apply_filter(e: tkinter.Event, label, collname=None):
    if label == cnf.lng.product:
        cnf.product = True
        cnf.models = cnf.catalog = False
    elif label == cnf.lng.models:
        cnf.models = True
        cnf.product = cnf.catalog = False
    elif label == cnf.lng.catalog:
        cnf.catalog = True
        cnf.product = cnf.models = False
    else:
        cnf.product = cnf.models = cnf.catalog = True

    if collname:
        cnf.show_coll(e, collname)
    else:
        cnf.reload_scroll()


@dec_utils_task
def finder_actions(
    src, tiff=False, reveal=False, copy_path=False, download=False, 
    fullsize=False
    ):

    if not isinstance(src, list):
        src = [src]

    if not [i for i in src if os.path.exists(i)]:
        cnf.topbar_text(cnf.lng.no_jpg)
        delay()
        return

    if tiff:
        tiffs = []
        cnf.topbar_text(cnf.lng.please_wait)

        for i in src:
    
            if not cnf.topbar_flag:
                return
    
            found_tiffs = find_tiffs(i)

            if found_tiffs:
                tiffs = tiffs + found_tiffs
    
        src = tiffs.copy()
        if not tiffs:
            cnf.topbar_text(cnf.lng.no_tiff)
            delay()
            return

    if reveal:
        cnf.topbar_text(cnf.lng.please_wait)
        reveal_files(src)
        delay()
        return
    
    if copy_path:
        cnf.topbar_text(cnf.lng.please_wait)
        cnf.root.clipboard_clear()
        cnf.root.clipboard_append("\n".join(src))
        delay()
        return

    if download or fullsize:
        downloads = os.path.join(cnf.down_folder, cnf.app_name)
        os.makedirs(downloads, exist_ok=True)
        ln_src = len(src)

        for num, img_src in enumerate(src, 1):
            if not cnf.topbar_flag:
                return

            cnf.topbar_text(
                f"{cnf.lng.copying} {num} {cnf.lng.from_pretext} {ln_src}"
                )

            name, ext = os.path.splitext(img_src.split("/")[-1])

            if download:
                try:
                    shutil.copy(img_src, f"{downloads}/{name}.{ext}")
                except FileNotFoundError:
                    print(f"utils > download file not found {img_src}")
                    continue

            if fullsize:
                if img_src.endswith((".psd", ".PSD", ".psb", ".PSB")):

                    try:
                        img = psd_tools.PSDImage.open(img_src).composite()
                    except Exception as e:
                        try:
                            img = Image.open(img_src)
                        except Exception:
                            print(f"utils > fullsize psd open > {img_src}")
                            print(e)
                            continue

                    try:
                        img = img.convert("RGB", colors=8)
                        # img = black_borders(img)
                        img.save(f"{downloads}/psd {name}.jpg")

                    except Exception as e:
                        print(f"utils > fullsize psd save > {img_src}")
                        print(e)
                        continue

                else:
                    try:
                        img = tifffile.imread(img_src)[:,:,:3]

                        if str(img.dtype) != "uint8":
                            img = (img/256).astype("uint8")

                        img = Image.fromarray(img.astype("uint8"), "RGB")
                        # img = black_borders(img)
                        img.save(f"{downloads}/tiff {name}.jpg")

                    except Exception as e:
                        print(f"utils > fullsize tiff > {img_src}")
                        print(e)
                        continue

        subprocess.Popen(["open", downloads])
