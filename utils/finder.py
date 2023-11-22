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
from .system import delay, find_tiffs, reveal_files


class System:
    def delay(self):
        sleep(2)

    def normalize_name(self, name: str) -> Literal["file name"]:
        name, ext = os.path.splitext(p=name)
        name = name.translate(str.maketrans("", "", string.punctuation))

        for i in ("preview", "1x1", "1х1", "crop", "копия", "copy", "small"):
            name = name.replace(i, "")

        return name.replace(" ", "")

    def find_tiff(self, src: Literal["file path"]) -> (tuple[Literal["file path tiff"], ...] | list):
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
        return images


class FinderActions(System):
    def __init__(self, src: Literal["path"] | tuple[Literal["path"], ...],
                 copy_path: bool = False, download: bool = False,
                 fullsize: bool = False, reveal: bool = False,
                 tiff: bool = False):

        if not isinstance(src, list):
            src = [src]

        if not self.jpg_check(path_list=src):
            cnf.notibar_text(cnf.lng.no_jpg)
            self.delay()
            return

        if tiff:
            cnf.notibar_text(cnf.lng.please_wait)
            src = self.get_tiff(path_list=src)
            if not src:
                cnf.notibar_text(text=cnf.lng.no_tiff)
                delay()
                return

    def jpg_check(self, path_list: tuple[str, ...]) -> bool:
        if not [i for i in path_list if os.path.exists(path=i)]:
            return False
        return True

    def get_tiff(self, path_list: tuple[str, ...]) -> tuple[str, ...]:
        return [tiff
                for src in path_list
                for tiff in self.find_tiff(src=src)
                if cnf.notibar_status]








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
    
            if not cnf.notibar_status:
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
        cnf.notibar_text(text=cnf.lng.done)
        cnf.root.clipboard_clear()
        cnf.root.clipboard_append("\n".join(img_src))
        delay()
        return

    if download or fullsize:
        downloads = os.path.join(cnf.down_folder, cnf.app_name)
        os.makedirs(name=downloads, exist_ok=True)
        ln_src = len(img_src)

        for num, img_src in enumerate(iterable=img_src, start=1):
            if not cnf.notibar_status:
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
