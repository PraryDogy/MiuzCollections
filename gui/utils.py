import shutil
import os
import string
import subprocess
import threading
import tkinter

import cv2
import numpy
from PIL import Image, ImageDraw

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
    "on_exit",
    "replace_bg",
    "Reveal",
    "smb_ip",
    "run_applescript",
    "download_files",
    "download_onefile",
    "download_tiffs",
    "focus_last_win",
    )


class Reveal:
    def normalize_name(self, name: str):
        name, ext = os.path.splitext(name)
        name = name.translate(str.maketrans("", "", string.punctuation))

        for i in conf.stopwords:
            name = name.replace(i, "")

        return name.replace(" ", "")

    def reveal_jpg(self, src: str):
        def task():
            subprocess.call(["open", "-R", src])
        threading.Thread(target = task).start()

    def reveal_tiffs(self, list_paths: list):
        def task():
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

        if list_paths:
            threading.Thread(target=task).start()

    def find_tiffs(self, src: str):
        path, filename = os.path.split(src)
        src_file_no_ext = self.normalize_name(filename)
        exts = (".tiff", ".TIFF", ".psd", ".PSD", ".psb", ".PSB", ".tif", ".TIF")
        images = []

        for root, dirs, files in os.walk(path):
            for file in files:

                if file.endswith(exts):

                    file_no_ext = self.normalize_name(file)

                    if src_file_no_ext in file_no_ext:
                        images.append(os.path.join(root, file))

                    elif file_no_ext in src_file_no_ext and len(file_no_ext) > 5:
                        images.append(os.path.join(root, file))
        if images:
            return images
        else:
            return False


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


def smb_check():
    def task():
        if not os.path.exists(conf.coll_folder):
            try:
                cmd = f"mount volume \"{conf.smb_ip}\""
                subprocess.call(["osascript", "-e", cmd], timeout=3)
            except subprocess.TimeoutExpired:
                print("timeout 3 sec, utils.py, smb_check")

    t = threading.Thread(target=task, daemon=True)
    t.start()
    while t.is_alive():
        conf.root.update()

    return bool(os.path.exists(conf.coll_folder))


def smb_ip():
    df = subprocess.Popen(['df', conf.coll_folder], stdout=subprocess.PIPE)
    outputLine = df.stdout.readlines()[1]
    unc_path = str(outputLine.split()[0])
    return "smb://" + unc_path.split("@")[-1][:-1]


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


def run_applescript(applescript: str):
    args = [
        item
        for x in [("-e",l.strip())
        for l in applescript.split('\n')
        if l.strip() != ''] for item in x]
    subprocess.call(["osascript"] + args)


def download_files(title, paths_list: list):
    coll = conf.curr_coll
    if coll == "all":
        coll = "All collections"

    dest = os.path.join(
        os.path.expanduser('~'), "Downloads", conf.app_name, coll, title
        )

    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)

    for i in paths_list:
        filename = i.split("/")[-1]
        shutil.copy(i, os.path.join(dest, filename))
        # subprocess.call(['cp', i, os.path.join(dest, filename)])

    subprocess.Popen(["open", dest])


def download_onefile(src):
    title = src.split("/")[-1]
    parrent_path = os.path.join(
        os.path.expanduser('~'), "Downloads", conf.app_name
        )
    dest_path = os.path.join(parrent_path, title)

    if not os.path.exists(parrent_path):
        os.mkdir(parrent_path)

    shutil.copy(src, dest_path)

    subprocess.Popen(["open", "-R", dest_path])


def download_tiffs(src):
    tiffs = Reveal().find_tiffs(src)
    if tiffs:
        parrent_path = os.path.join(os.path.expanduser('~'), "Downloads", conf.app_name)
        if not os.path.exists(parrent_path):
            os.mkdir(parrent_path)

        for i in tiffs:
            filename = i.split("/")[-1]
            dest = os.path.join(parrent_path, filename)
            shutil.copy(i, dest)

        subprocess.Popen(["open", parrent_path])


def focus_last_win():
    for k, v in conf.root.children.items():
        if v.widgetName == "toplevel":
            v.focus_force()
            v.grab_set_global()
            return
    conf.root.focus_force()