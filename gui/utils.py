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
from PIL import Image, UnidentifiedImageError

from cfg import cnf
from database import *

from .globals import Globals

__all__ = (
    "apply_filter",
    "convert_to_rgb",
    "copy_jpg_path",
    "copy_tiffs_paths",
    "copy_text",
    "crop_image",
    "db_remove_img",
    "decode_image",
    "download_fullsize",
    "download_group_fullsize",
    "download_group_jpg",
    "download_group_tiff",
    "download_one_jpg",
    "download_tiffs",
    "encode_image",
    "find_tiffs",
    "focus_last_win",
    "get_coll_name",
    "normalize_name",
    "on_exit",
    "paste_search",
    "place_center",
    "topbar_default",
    "replace_bg",
    "resize_image",
    "reveal_coll",
    "reveal_jpg",
    "reveal_tiffs",
    "run_applescript",
    "run_thread",
    "smb_check",
    "smb_ip",
    )




# ********************system utils********************

utils_task: threading.Thread = None
smb_task: threading.Thread = None


def run_thread(fn, args=[]):
    global utils_task
    utils_task = threading.Thread(target=fn, args=args, daemon=True)
    utils_task.start()


def wait_thread():
    if smb_task:
        while smb_task.is_alive():
            cnf.root.update()

    if utils_task:
        while utils_task.is_alive():
            cnf.root.update()


def topbar_default():
    def task():
        sleep(2)
        Globals.topbar_default()
    try:
        run_thread(task)
    except RuntimeError:
        print("utils > topbar_default_thread runtime err")
        topbar_default()


def default_thread(task):
    def wrapper(*args):
        wait_thread()
        run_thread(task, args)
        wait_thread()
        topbar_default()
        wait_thread()
        cnf.topbar_flag = True
    return wrapper


def run_applescript(applescript: str):
    args = [
        item
        for x in [("-e",l.strip())
        for l in applescript.split('\n')
        if l.strip() != ''] for item in x]
    subprocess.call(["osascript"] + args)


def write_err():
    if not os.path.exists(cnf.cfg_dir):
        os.mkdir(cnf.cfg_dir)

    file = os.path.join(cnf.cfg_dir, 'err.txt')

    if not os.path.exists(file):
        with open(file, 'w') as err_file:
            pass

    with open(file, 'r') as err_file:
        data = err_file.read()

    data = f'{data}\n\n{traceback.format_exc()}'

    with open(file, 'w') as err_file:
        print(data, file=err_file)


def normalize_name(name: str):
    name, ext = os.path.splitext(name)
    name = name.translate(str.maketrans("", "", string.punctuation))

    for i in ("preview", "1x1", "1х1", "crop", "копия", "copy", "small"):
        name = name.replace(i, "")

    return name.replace(" ", "")


def smb_check():
    global smb_task


    def task():
        if not os.path.exists(cnf.coll_folder):
            try:
                cmd = f"mount volume \"{cnf.smb_ip}\""
                subprocess.call(["osascript", "-e", cmd], timeout=3)
            except subprocess.TimeoutExpired:
                print("timeout 3 sec, utils.py, smb_check")


    smb_task = threading.Thread(target=task, daemon=True)
    smb_task.start()
    while smb_task.is_alive():
        cnf.root.update()

    return bool(os.path.exists(cnf.coll_folder))


def smb_ip():
    df = subprocess.Popen(['df', cnf.coll_folder], stdout=subprocess.PIPE)
    try:
        outputLine = df.stdout.readlines()[1]
        unc_path = str(outputLine.split()[0])
        return "smb://" + unc_path.split("@")[-1][:-1]
    except IndexError:
        return None


def on_exit(e=None):
    w, h = cnf.root.winfo_width(), cnf.root.winfo_height()
    x, y = cnf.root.winfo_x(), cnf.root.winfo_y()

    cnf.root_w = w
    cnf.root_h = h
    cnf.root_x = x
    cnf.root_y = y

    cnf.write_cfg()

    cnf.topbar_flag = False
    cnf.scan_flag = False
    quit()


def create_dir(title=None):
    coll = cnf.curr_coll
    if coll == cnf.all_colls:
        coll = cnf.lang.all_colls

    dest = os.path.join(cnf.down_folder, cnf.app_name, coll)

    if title:
        dest = os.path.join(dest, title)

    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)

    return dest


def get_coll_name(src: str):
    coll = src.replace(cnf.coll_folder, "").strip(os.sep).split(os.sep)

    if len(coll) > 1:
        return coll[0]
    else:
        return cnf.coll_folder.strip(os.sep).split(os.sep)[-1]


def place_center():
    win: tkinter.Toplevel = [
        i for i in cnf.root.winfo_children()
        if isinstance(i, tkinter.Toplevel)][-1]

    x, y = cnf.root.winfo_x(), cnf.root.winfo_y()
    xx = x + cnf.root.winfo_width()//2 - win.winfo_width()//2
    yy = y + cnf.root.winfo_height()//2 - win.winfo_height()//2

    win.geometry(f'+{xx}+{yy}')


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
        Globals.search_var.set(pasted)
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

    resized = resize_image(image, cnf.thumb_size, cnf.thumb_size, True)

    try:
        return cv2.imencode('.jpg', resized)[1].tobytes()
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
    return cropped[0:cnf.thumb_size, 0:cnf.thumb_size]




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


@default_thread
def reveal_tiffs(list_paths: list):
    if not list_paths:
        Globals.topbar_text(cnf.lang.no_tiff)
        return

    Globals.topbar_text(cnf.lang.please_wait)

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


@default_thread
def download_tiffs(src):
    Globals.topbar_text(cnf.lang.please_wait)
    tiffs = find_tiffs(src)

    if not tiffs:
        Globals.topbar_text(cnf.lang.no_tiff)
        return

    ln_tiffs = len(tiffs)
    parrent = create_dir()
    

    for num, tiff in enumerate(tiffs, 1):

        if not cnf.topbar_flag:
            return

        t = (
            f"{cnf.lang.copying} "
            f"{num} {cnf.lang.from_pretext} {ln_tiffs}"
            )
        Globals.topbar_text(t)
        try:
            shutil.copy(tiff, os.path.join(parrent, tiff.split("/")[-1]))
        except FileNotFoundError:
            print(f"utils > download tiffs > not found {tiff}")
            write_err()
            continue

    subprocess.Popen(["open", parrent])


# @default_thread
def copy_tiffs_paths(path):
    wait_thread()

    Globals.topbar_text(cnf.lang.please_wait)
    tiffs = find_tiffs(path)

    if tiffs:
        cnf.root.clipboard_clear()
        cnf.root.clipboard_append("\n".join(tiffs))
    else:
        Globals.topbar_text(cnf.lang.no_tiff)

    topbar_default()


def copy_jpg_path(path):
    if os.path.exists(path):
        cnf.root.clipboard_clear()
        cnf.root.clipboard_append(path)
    else:
        Globals.topbar_text(cnf.lang.no_jpg)

    topbar_default()


@default_thread
def reveal_jpg(src: str):
    if not os.path.exists(src):
        Globals.topbar_text(cnf.lang.no_jpg)
        return

    Globals.topbar_text(cnf.lang.please_wait)
    subprocess.call(["open", "-R", src])


@default_thread
def download_group_jpg(title, paths_list: list):
    check = [i for i in paths_list if os.path.exists(i)]
    if not check:
        Globals.topbar_text(cnf.lang.no_jpg)
        return

    dest = create_dir(title)
    ln_paths = len(paths_list)

    for num, imgpath in enumerate(paths_list, 1):

        if not cnf.topbar_flag:
            return

        t = (
            f"{cnf.lang.copying} {num} "
            f"{cnf.lang.from_pretext} {ln_paths}"
            )

        Globals.topbar_text(t)
        filename = imgpath.split("/")[-1]

        try:
            shutil.copy(imgpath, os.path.join(dest, filename))
        except FileNotFoundError:
            print(f"utils > copy group jpg > not found {imgpath}")
            write_err()
            continue

    subprocess.Popen(["open", dest])


@default_thread
def download_group_tiff(title, paths_list):
    check = [i for i in paths_list if os.path.exists(i)]
    if not check:
        Globals.topbar_text(cnf.lang.no_tiff)
        return

    tiffs = []

    for i in paths_list:

        if not cnf.topbar_flag:
            print(1)
            return

        found_tiffs = find_tiffs(i)

        if found_tiffs:
            tiffs = tiffs + found_tiffs

    if not tiffs:
        Globals.topbar_text(cnf.lang.no_tiff)
        return

    ln_tiffs = len(tiffs)
    dest = create_dir(title)

    for num, imgpath in enumerate(tiffs, 1):

        if not cnf.topbar_flag:
            return

        t = (
            f"{cnf.lang.copying} {num} "
            f"{cnf.lang.from_pretext} {ln_tiffs}"
            )

        Globals.topbar_text(t)

        filename = imgpath.split("/")[-1]

        try:
            shutil.copy(imgpath, os.path.join(dest, filename))
        except FileNotFoundError:
            print(f"utils > copy group tiff > not found {imgpath}")
            write_err()
            continue

    subprocess.Popen(["open", dest])


@default_thread
def download_one_jpg(src):
    if not os.path.exists(src):
        Globals.topbar_text(cnf.lang.no_jpg)
        return

    Globals.topbar_text(cnf.lang.copying)
    dest = create_dir()
    dest = os.path.join(dest, src.split("/")[-1])

    try:
        shutil.copy(src, dest)
        subprocess.Popen(["open", "-R", dest])
    except FileNotFoundError:
        print(f"utils > download one jpg > not found {src}")
        write_err()


def db_remove_img(src):
    q = (
        sqlalchemy.delete(Thumbs).filter(
            Thumbs.src==src
            ))
    Dbase.conn.execute(q)
    Globals.reload_thumbs()


def copy_text(text):
    cnf.root.clipboard_clear()
    cnf.root.clipboard_append(text)


@default_thread
def download_fullsize(src):
    Globals.topbar_text(cnf.lang.please_wait)
    tiffs = find_tiffs(src)

    if not tiffs:
        Globals.topbar_text(cnf.lang.no_tiff)
        return
    
    ln_tiffs = len(tiffs)
    parrent = create_dir()
    

    for num, img_path in enumerate(tiffs, 1):
        if not cnf.topbar_flag:
            return

        t = (
            f"{cnf.lang.copying} "
            f"{num} {cnf.lang.from_pretext} {ln_tiffs}"
            )
        Globals.topbar_text(t)

        filename = img_path.split(os.sep)[-1].split(".")[0]
        dest = os.path.join(parrent, filename + ".jpg")

        if os.path.exists(dest):
            dest = os.path.join(parrent, filename + " 2" + ".jpg")

        if img_path.endswith((".psd", ".PSD", ".psb", ".PSB")):
            try:
                img = psd_tools.PSDImage.open(img_path).composite()

            except (
                UnidentifiedImageError, OSError, OverflowError, ValueError
                ):
                img = Image.open(img_path)

            try:
                img = img.convert("RGB", colors=8).save(dest)
            except Exception:
                print(f"utils > download fsize > save {img_path}")
                write_err()
                continue

        else:
            try:
                img = tifffile.imread(img_path)[:,:,:3]

                if str(img.dtype) == "uint16":
                    img = (img/256).astype('uint8')

                img = Image.fromarray(img.astype('uint8'), 'RGB')
                img.save(dest)

            except Exception:
                print(f"utils > download group fsize > tiff save {img_path}")
                write_err()
                continue

    subprocess.Popen(["open", parrent])


@default_thread
def download_group_fullsize(title, paths_list):
    check = [i for i in paths_list if os.path.exists(i)]
    if not check:
        Globals.topbar_text(cnf.lang.no_tiff)
        return

    tiffs = []

    for i in paths_list:

        if not cnf.topbar_flag:
            return

        found_tiffs = find_tiffs(i)

        if found_tiffs:
            tiffs = tiffs + found_tiffs

    if not tiffs:
        Globals.topbar_text(cnf.lang.no_tiff)
        return

    ln_tiffs = len(tiffs)
    parrent = create_dir(title)

    for num, img_path in enumerate(tiffs, 1):
        if not cnf.topbar_flag:
            return

        t = (
            f"{cnf.lang.copying} "
            f"{num} {cnf.lang.from_pretext} {ln_tiffs}"
            )
        Globals.topbar_text(t)

        filename = img_path.split(os.sep)[-1].split(".")[0]
        dest = os.path.join(parrent, filename + ".jpg")

        if os.path.exists(dest):
            dest = os.path.join(parrent, filename + " 2" + ".jpg")

        if img_path.endswith((".psd", ".PSD", ".psb", ".PSB")):
            try:
                img = psd_tools.PSDImage.open(img_path)
                img = img.composite()

            except (
                UnidentifiedImageError, OSError, OverflowError, ValueError
                ):
                img = Image.open(img_path)

            try:
                img = img.convert("RGB", colors=8).save(dest)
            except Exception:
                print(f"utils > download group fsize > save {img_path}")
                write_err()
                continue

        else:
            try:
                img = tifffile.imread(img_path)[:,:,:3]

                if str(img.dtype) == "uint16":
                    img = (img/256).astype('uint8')

                img = Image.fromarray(img.astype('uint8'), 'RGB')
                img.save(dest)

            except Exception:
                print(f"utils > download group fsize > tiff save {img_path}")
                write_err()
                continue

    subprocess.Popen(["open", parrent])


def apply_filter(str, e=None):
    if str == "product":
        cnf.product = True
        cnf.models = False
        cnf.catalog = False
    elif str == "models":
        cnf.product = False
        cnf.models = True
        cnf.catalog = False
    elif str == "catalog":
        cnf.product = False
        cnf.models = False
        cnf.catalog = True
    else:
        cnf.product = True
        cnf.models = True
        cnf.catalog = True

    if e:
        Globals.show_coll(e)
    else:
        Globals.reload_scroll()
