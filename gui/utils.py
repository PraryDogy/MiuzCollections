import os
import shutil
import string
import subprocess
import threading
import tkinter
from time import sleep

import cv2
import numpy
from PIL import Image

from cfg import conf

from .globals import Globals

__all__ = (
    "convert_to_rgb",
    "copy_jpeg_path",
    "copy_tiffs_paths",
    "crop_image",
    "decode_image",
    "download_group_jpeg",
    "download_one_jpeg",
    "download_tiffs",
    "encode_image",
    "find_tiffs",
    "focus_last_win",
    "get_coll_name",
    "normalize_name",
    "on_exit",
    "paste_search",
    "place_center",
    "topbar_default_thread",
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

utils_task = threading.Thread


def run_thread(fn, args=[]):
    global utils_task
    utils_task = threading.Thread(target=fn, args=args, daemon=True)
    utils_task.start()


def wait_thread():
    while utils_task.is_alive():
        conf.root.update()


def topbar_default_thread():
    global utils_task

    def task():
        sleep(2)
        Globals.topbar_default()

    try:
        run_thread(task)
    except RuntimeError:
        print("utils > topbar_default_thread runtime err")
        conf.root.after(2000, topbar_default_thread)


def run_applescript(applescript: str):
    args = [
        item
        for x in [("-e",l.strip())
        for l in applescript.split('\n')
        if l.strip() != ''] for item in x]
    subprocess.call(["osascript"] + args)



def normalize_name(name: str):
    name, ext = os.path.splitext(name)
    name = name.translate(str.maketrans("", "", string.punctuation))

    for i in conf.stopwords:
        name = name.replace(i, "")

    return name.replace(" ", "")


def smb_check():
    def task():
        if not os.path.exists(conf.coll_folder):
            try:
                cmd = f"mount volume \"{conf.smb_ip}\""
                subprocess.call(["osascript", "-e", cmd], timeout=3)
            except subprocess.TimeoutExpired:
                print("timeout 3 sec, utils.py, smb_check")

    run_thread(task)
    return bool(os.path.exists(conf.coll_folder))


def smb_ip():
    df = subprocess.Popen(['df', conf.coll_folder], stdout=subprocess.PIPE)
    try:
        outputLine = df.stdout.readlines()[1]
        unc_path = str(outputLine.split()[0])
        return "smb://" + unc_path.split("@")[-1][:-1]
    except IndexError:
        return None


def on_exit(e=None):
    w, h = conf.root.winfo_width(), conf.root.winfo_height()
    x, y = conf.root.winfo_x(), conf.root.winfo_y()

    conf.root_w = w
    conf.root_h = h
    conf.root_x = x
    conf.root_y = y

    conf.write_cfg()

    conf.flag = False
    quit()


def create_dir(title=None):
    coll = conf.curr_coll
    if coll == "all":
        coll = conf.lang.all_colls

    dest = os.path.join(
        os.path.expanduser('~'), "Downloads", conf.app_name, coll
        )

    if title:
        dest = os.path.join(dest, title)

    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)

    return dest


def get_coll_name(src: str):
    coll = src.replace(conf.coll_folder, "").strip(os.sep).split(os.sep)

    if len(coll) > 1:
        return coll[0]
    else:
        return conf.coll_folder.strip(os.sep).split(os.sep)[-1]


def place_center():
    win: tkinter.Toplevel = [
        i for i in conf.root.winfo_children()
        if isinstance(i, tkinter.Toplevel)][-1]

    x, y = conf.root.winfo_x(), conf.root.winfo_y()
    xx = x + conf.root.winfo_width()//2 - win.winfo_width()//2
    yy = y + conf.root.winfo_height()//2 - win.winfo_height()//2

    win.geometry(f'+{xx}+{yy}')


def reveal_coll(coll_name):
    if coll_name != conf.all_colls:
        coll_path = os.path.join(conf.coll_folder, coll_name)
    else:
        coll_path = conf.coll_folder

    try:
        subprocess.check_output(["/usr/bin/open", coll_path])
    except subprocess.CalledProcessError:
        subprocess.check_output(["/usr/bin/open", conf.coll_folder])


def paste_search():
    try:
        pasted = conf.root.clipboard_get().strip()
        Globals.search_var.set(pasted)
    except tkinter.TclError:
        print("no clipboard")


def focus_last_win():
    for k, v in conf.root.children.items():
        if v.widgetName == "toplevel":
            v.focus_force()
            v.grab_set_global()
            return
    conf.root.focus_force()




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
        image = replace_bg(image, conf.bg_color)

    resized = resize_image(image, conf.thumb_size, conf.thumb_size, True)

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
        return decode_image(encode_image(conf.thumb_err))


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
    return cropped[0:conf.thumb_size, 0:conf.thumb_size]




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


def reveal_tiffs(list_paths: list):
    wait_thread()

    def task():
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

    if list_paths:
        Globals.topbar_text(conf.lang.live_wait)
        wait_thread()
        run_thread(task)
        wait_thread()
        topbar_default_thread()
    else:
        Globals.topbar_text(conf.lang.live_notiff)
        wait_thread()
        topbar_default_thread()


def download_tiffs(src):
    wait_thread()


    def task(parrent, tiffs, ln_tiffs):
        for num, tiff in enumerate(tiffs, 1):

            if not conf.flag:
                return

            t = (
                f"{conf.lang.live_copying} "
                f"{num} {conf.lang.live_from} {ln_tiffs}"
                )
            Globals.topbar_text(t)
            shutil.copy(tiff, os.path.join(parrent, tiff.split("/")[-1]))

        subprocess.Popen(["open", parrent])


    Globals.topbar_text(conf.lang.live_wait)
    tiffs = find_tiffs(src)

    if tiffs:
        conf.flag = True
        ln_tiffs = len(tiffs)
        parrent = create_dir()

        run_thread(task, [parrent, tiffs, ln_tiffs])
        wait_thread()
        topbar_default_thread()

    else:
        Globals.topbar_text(conf.lang.live_notiff)
        topbar_default_thread()


def copy_tiffs_paths(path):
    wait_thread()

    Globals.topbar_text(conf.lang.live_wait)
    tiffs = find_tiffs(path)

    if tiffs:
        conf.root.clipboard_clear()
        conf.root.clipboard_append("\n".join(tiffs))
        topbar_default_thread()
    else:
        Globals.topbar_text(conf.lang.live_notiff)
        topbar_default_thread()


def copy_jpeg_path(path):
    if os.path.exists(path):
        conf.root.clipboard_clear()
        conf.root.clipboard_append(path)
    else:
        Globals.topbar_text(conf.lang.live_nojpeg)
        topbar_default_thread()


def reveal_jpg(src: str):
    wait_thread()

    def task():
        subprocess.call(["open", "-R", src])

    if os.path.exists(src):
        Globals.topbar_text(conf.lang.live_wait)
        run_thread(task)
    else:
        Globals.topbar_text(conf.lang.live_nojpeg)

    wait_thread()
    topbar_default_thread()


def download_group_jpeg(title, paths_list: list):
    wait_thread()


    def task(dest, ln_paths):
        for num, imgpath in enumerate(paths_list, 1):

            if not conf.flag:
                return

            t = (
                f"{conf.lang.live_copying} {num} "
                f"{conf.lang.live_from} {ln_paths}"
                )

            Globals.topbar_text(t)

            filename = imgpath.split("/")[-1]
            shutil.copy(imgpath, os.path.join(dest, filename))

        subprocess.Popen(["open", dest])

    for i in paths_list:
        if not os.path.exists(i):
            Globals.topbar_text(conf.lang.live_nojpeg)
            topbar_default_thread()
            return

    conf.flag = True
    dest = create_dir(title)
    ln_paths = len(paths_list)
    run_thread(task, [dest, ln_paths])
    wait_thread()
    topbar_default_thread()
    conf.flag = False


def download_one_jpeg(src):
    wait_thread()


    def task(dest):
        shutil.copy(src, dest)
        subprocess.Popen(["open", "-R", dest])

    if os.path.exists(src):
        Globals.topbar_text(conf.lang.live_copying)
        dest = create_dir()
        dest = os.path.join(dest, src.split("/")[-1])
        run_thread(task, [dest])
    else:
        Globals.topbar_text(conf.lang.live_nojpeg)

    wait_thread()
    topbar_default_thread()
