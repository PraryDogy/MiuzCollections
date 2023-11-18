import os
import shutil
import string
import subprocess
import threading
import tkinter
import traceback
from time import sleep

try:
    from typing_extensions import Literal, Callable
except ImportError:
    from typing import Literal, Callable

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


def run_utils_task(fn: Callable, args: list = [], kwargs: dict = {}):
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
    cnf.notibar_default()


def delay():
    sleep(2)


def dec_utils_task(task: Callable):
    def wrapper(*args, **kwargs):
        wait_utils_task()
        run_utils_task(fn=task, args=args, kwargs=kwargs)
        wait_utils_task()
        cnf.notibar_default()
        wait_utils_task()
        cnf.topbar_flag = True
    return wrapper


def run_applescript(applescript: Literal["applescript"]):
    args = [
        arg for row in applescript.split("\n")
        for arg in ("-e", row.strip())
        if row.strip()
        ]
    subprocess.call(args=["osascript"] + args)


def write_err():
    if not os.path.exists(path=cnf.cfg_dir):
        os.mkdir(path=cnf.cfg_dir)

    file = os.path.join(cnf.cfg_dir, "err.txt")

    if not os.path.exists(path=file):
        with open(file=file, mode="w") as err_file:
            pass

    with open(file=file, mode="r") as err_file:
        data = err_file.read()

    data = f"{data}\n\n{traceback.format_exc()}"

    with open(file=file, mode="w") as err_file:
        print(values=data, file=err_file)


def normalize_name(name: str) -> Literal["file name"]:
    name, ext = os.path.splitext(p=name)
    name = name.translate(str.maketrans("", "", string.punctuation))

    for i in ("preview", "1x1", "1х1", "crop", "копия", "copy", "small"):
        name = name.replace(i, "")

    return name.replace(" ", "")


def smb_check() -> bool:
    return bool(os.path.exists(path=cnf.coll_folder))


def on_exit(e: tkinter.Event = None):
    new_g = {"w": cnf.root.winfo_width(),
             "h": cnf.root.winfo_height(),
             "x": cnf.root.winfo_x(),
             "y": cnf.root.winfo_y()}

    for k, v in new_g.items():
        cnf.root_g[k] = v

    cnf.write_cfg()

    cnf.topbar_flag = False
    cnf.scan_status = False
    quit()


def get_coll_name(src: Literal["file path"]) -> Literal["collection name"]:
    coll = src.replace(cnf.coll_folder, "").strip(os.sep).split(os.sep)

    if len(coll) > 1:
        return coll[0]
    else:
        return cnf.coll_folder.strip(os.sep).split(os.sep)[-1]


def place_center(win: tkinter.Toplevel, width: int, height: int,
                 parrent_win: tkinter.Toplevel = cnf.root):
    x, y = parrent_win.winfo_x(), parrent_win.winfo_y()
    xx = x + parrent_win.winfo_width() // 2 - width // 2
    yy = y + parrent_win.winfo_height() // 2 - height // 2
    win.geometry(f"+{xx}+{yy}")


def reveal_coll(collname: str):
    if collname != cnf.all_colls:
        coll_path = os.path.join(cnf.coll_folder, collname)
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


# ********************image utils********************

def resize_image(img: Literal["cv2 image"], wid_w: int, wid_h: int,
                 is_thumb: bool) -> Literal["cv2 image"]:
    h, w = img.shape[:2]
    aspect = w/h
    if is_thumb:
        if aspect > 1:
            new_h, new_w = wid_h, round(wid_h*aspect)
        elif aspect < 1:
            new_h, new_w = round(wid_w/aspect), wid_w
        elif aspect == 1:
            new_h, new_w = wid_h, wid_h
    else:
        f1 = wid_w / w
        f2 = wid_h / h
        f = f2
        new_w, new_h = (int(w * f), int(h * f))

    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def replace_bg(img: Literal["cv2 image"], color: str) -> Literal["cv2 image"]:
    try:
        trans_mask = img[:,:,3 ] == 0
        color = color.replace("#", "")
        bg_color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        img[trans_mask] = [*bg_color, 255]
    except IndexError:
        return img
    return img


def encode_image(src: Literal["file path"]) -> Literal["cv2 image"]:
    image = cv2.imread(src, cv2.IMREAD_UNCHANGED)

    if src.endswith((".png", ".PNG")):
        image = replace_bg(image, cnf.bg_color)

    resized = resize_image(image, cnf.thumbsize, cnf.thumbsize, True)

    try:
        return cv2.imencode(".jpg", resized)[1].tobytes()
    except cv2.error:
        print("too big img")


def decode_image(img: bytes) -> Literal["cv2 image"]:
    try:
        nparr = numpy.frombuffer(img, numpy.byte)
        return cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
    except TypeError:
        print("utils.py decode_image NoneType instead bytes like img")
        return decode_image(encode_image(cnf.thumb_err))


def convert_to_rgb(img: Literal["cv2 image"]) -> Image:
    # convert cv2 color to rgb
    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # load numpy array image
    return Image.fromarray(image_rgb)


def crop_image(img: Literal["cv2 image"]) -> Literal["cv2 image"]:
    width, height = img.shape[1], img.shape[0]
    if height >= width:
        delta = (height-width)//2
        cropped = img[delta:height-delta, 0:width]
    else:
        delta = (width-height)//2
        cropped = img[0:height, delta:width-delta]
    return cropped[0:cnf.thumbsize, 0:cnf.thumbsize]


def black_borders(img: Image) -> Image:
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

def find_tiffs(src: Literal["file path"]) -> (tuple[Literal["file path tiff"], ...] | bool):
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


def reveal_files(paths: tuple[Literal["file path"], ...]):
    cnf.notibar_text(cnf.lng.please_wait)

    paths = (
        f"\"{i}\" as POSIX file"
        for i in paths
        )

    paths = ", ".join(paths)

    applescript = f"""
        tell application \"Finder\"
        reveal {{{paths}}}
        activate
        end tell
        """

    run_applescript(applescript)


def db_remove_img(img_src: Literal["file path"]):
    q = (
        sqlalchemy.delete(ThumbsMd).filter(
            ThumbsMd.src==img_src
            ))
    Dbase.conn.execute(q)
    cnf.reload_thumbs()


def copy_text(text: str):
    cnf.root.clipboard_clear()
    cnf.root.clipboard_append(string=text)


def apply_filter(filter: Literal["all"] | Literal["cnf > filter values key"],
                 btn: tkinter = None, collname: str = None):
    if filter == "all":
        for k, v in cnf.filter_values.items():
            cnf.filter_values[k] = False
    else:
        for k, v in cnf.filter_values.items():
            cnf.filter_values[k] = False
        cnf.filter_values[filter] = True

    if collname and btn:
        cnf.reload_filters()
        cnf.show_coll(btn=btn, collname=collname)
    else:
        cnf.reload_filters()
        cnf.reload_scroll()


@dec_utils_task
def finder_actions(
    img_src: Literal["file path"] | tuple[Literal["filepath"], ...],
    tiff: bool = False,
    reveal: bool = False,
    copy_path: bool = False,
    download: bool = False,
    fullsize: bool = False):

    if not isinstance(img_src, list):
        img_src = [img_src]

    if not [i for i in img_src if os.path.exists(path=i)]:
        cnf.notibar_text(cnf.lng.no_jpg)
        delay()
        return

    if tiff:
        tiffs = []
        cnf.notibar_text(cnf.lng.please_wait)

        for i in img_src:
    
            if not cnf.topbar_flag:
                return
    
            found_tiffs = find_tiffs(src=i)

            if found_tiffs:
                tiffs = tiffs + found_tiffs
    
        img_src = tiffs.copy()
        if not tiffs:
            cnf.notibar_text(text=cnf.lng.no_tiff)
            delay()
            return

    if reveal:
        cnf.notibar_text(text=cnf.lng.please_wait)
        reveal_files(paths=img_src)
        delay()
        return
    
    if copy_path:
        cnf.notibar_text(text=cnf.lng.please_wait)
        cnf.root.clipboard_clear()
        cnf.root.clipboard_append("\n".join(img_src))
        delay()
        return

    if download or fullsize:
        downloads = os.path.join(cnf.down_folder, cnf.app_name)
        os.makedirs(name=downloads, exist_ok=True)
        ln_src = len(img_src)

        for num, img_src in enumerate(iterable=img_src, start=1):
            if not cnf.topbar_flag:
                return

            cnf.notibar_text(text=f"{cnf.lng.copying} {num} "
                             f"{cnf.lng.from_pretext} {ln_src}")

            name, ext = os.path.splitext(p=img_src.split("/")[-1])

            if download:
                try:
                    shutil.copy(src=img_src, dst=f"{downloads}/{name}.{ext}")
                except FileNotFoundError:
                    print(f"utils > download file not found {img_src}")
                    continue

            if fullsize:
                if img_src.endswith((".psd", ".PSD", ".psb", ".PSB")):

                    try:
                        img = psd_tools.PSDImage.open(fp=img_src).composite()
                    except Exception as e:
                        try:
                            img = Image.open(fp=img_src)
                        except Exception:
                            print(f"utils > fullsize psd open > {img_src}")
                            print(e)
                            continue

                    try:
                        img = img.convert(mode="RGB", colors=8)
                        # img = black_borders(img)
                        img.save(fp=f"{downloads}/psd {name}.jpg")

                    except Exception as e:
                        print(f"utils > fullsize psd save > {img_src}")
                        print(e)
                        continue

                else:
                    try:
                        img = tifffile.imread(files=img_src)[:,:,:3]

                        if str(object=img.dtype) != "uint8":
                            img = (img/256).astype(dtype="uint8")

                        img = Image.fromarray(obj=img.astype("uint8"), mode="RGB")
                        # img = black_borders(img)
                        img.save(fp=f"{downloads}/tiff {name}.jpg")

                    except Exception as e:
                        print(f"utils > fullsize tiff > {img_src}")
                        print(e)
                        continue

        subprocess.Popen(args=["open", downloads])
