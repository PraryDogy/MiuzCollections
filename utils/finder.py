import os
import shutil
import string
import subprocess
from time import sleep

try:
    from typing_extensions import Callable, Literal
except ImportError:
    from typing import Literal, Callable

import threading
from difflib import SequenceMatcher

from cfg import cnf
from database import *

from .system import SysUtils


class Tsk:
    task = threading.Thread(target=None)


class FinderBase(SysUtils):
    def _delay(self):
        sleep(2)

    def _similarity(self, aa: str, bb: str):
        return SequenceMatcher(None, aa, bb).ratio()

    def _normalize_name(self, name: str) -> Literal["file name no extention"]:
        name, ext = os.path.splitext(p=name)
        return name.translate(str.maketrans("", "", string.punctuation + " "))

    def _find_tiff(self, src: Literal["file path"]) -> (tuple[Literal["file path tiff"], ...] | list):
        src_path, src_filename = os.path.split(src)
        src_filename = self._normalize_name(src_filename)
        exts = (".tiff", ".TIFF", ".psd", ".PSD", ".psb", ".PSB", ".tif", ".TIF")
        images = []

        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith(exts):
                    filename = self._normalize_name(file)
                    if self._similarity(aa=src_filename, bb=filename) > 0.8:
                        images.append(os.path.join(root, file))
        return images

    def _reveal_files(self, paths: tuple[Literal["file path"], ...]):
        paths = (
            f"\"{i}\" as POSIX file"
            for i in paths
            )

        paths = ", ".join(paths)

        applescript = f"""
            tell application \"Finder\"
            activate
            reveal {{{paths}}}
            end tell
            """

        self.run_applescript(script=applescript)

    def _copy_img(self, src: str, dest: str, name: str, ext: str):
        try:
            shutil.copy(src=src, dst=f"{dest}/{name}{ext}")
            return True
        except FileNotFoundError:
            self.print_err()
            return False

    def _jpg_check(self, path_list: tuple[str, ...]) -> bool:
        if not [i for i in path_list if os.path.exists(path=i)]:
            return False
        return True

    def _get_tiff(self, path_list: tuple[str, ...]) -> tuple[str, ...]:
        return [tiff
                for src in path_list
                for tiff in self._find_tiff(src=src)
                if cnf.notibar_status]

    def _create_downloads(self):
        downloads = os.path.join(cnf.down_folder, cnf.app_name)
        os.makedirs(name=downloads, exist_ok=True)
        return downloads

    # def _fullsize_img(self, src: str, dest: str, name: str):
    #     if src.endswith((".psd", ".PSD", ".psb", ".PSB")):

    #         try:
    #             img = psd_tools.PSDImage.open(fp=src).composite()
    #         except Exception:
    #             try:
    #                 img = Image.open(fp=src)
    #             except Exception:
    #                 self.print_err()
    #                 return False

    #         try:
    #             img = img.convert(mode="RGB", colors=8)
    #             # img = black_borders(img)
    #             img.save(fp=f"{dest}/psd {name}.jpg")
    #         except Exception:
    #             self.print_err()
    #             return False

    #     else:
    #         try:
    #             img = tifffile.imread(files=src)[:,:,:3]
    #             if str(object=img.dtype) != "uint8":
    #                 img = (img/256).astype(dtype="uint8")
    #             img = Image.fromarray(obj=img.astype("uint8"), mode="RGB")
    #             # img = black_borders(img)
    #             img.save(fp=f"{dest}/tiff {name}.jpg")
    #         except Exception as e:
    #             self.print_err()
    #             return False

    def wait_utils_task(self):
        while Tsk.task.is_alive():
            cnf.root.update()

    def cancel_utils_task(self):
        cnf.notibar_status = False
        self.wait_utils_task()
        cnf.notibar_default()


class FinderThread(FinderBase):
    def __init__(self, fn: Callable):
        self.fn = fn

    def __call__(self, **kwargs):
        self.wait_utils_task()

        Tsk.task = threading.Thread(target=self.fn, kwargs=kwargs, daemon=True)
        Tsk.task.start()

        self.wait_utils_task()
        cnf.notibar_default()
        self.wait_utils_task()
        cnf.notibar_status = True


@FinderThread
class FinderActions(FinderBase):
    def __init__(self, src: Literal["path"] | tuple[Literal["path"], ...],
                 clipboard: bool = False, download: bool = False,
                 reveal: bool = False, tiff: bool = False):

        if not isinstance(src, list):
            src = [src]

        if not self._jpg_check(path_list=src):
            cnf.notibar_text(cnf.lng.no_jpg)
            self._delay()
            return

        if tiff:
            cnf.notibar_text(cnf.lng.please_wait)
            src = self._get_tiff(path_list=src)
            if not src:
                cnf.notibar_text(text=cnf.lng.no_tiff)
                self._delay()
                return

        if reveal:
            cnf.notibar_text(text=cnf.lng.please_wait)
            self._reveal_files(paths=src)
            self._delay()
            return
        
        if clipboard:
            cnf.notibar_text(text=cnf.lng.done)
            cnf.root.clipboard_clear()
            cnf.root.clipboard_append("\n".join(src))
            self._delay()
            return
        
        if download:
            downloads = self._create_downloads()
            ln_src = len(src)

            for num, img_src in enumerate(iterable=src, start=1):

                if not cnf.notibar_status:
                    return

                t = f"{cnf.lng.copying} {num} {cnf.lng.from_pretext} {ln_src}"
                cnf.notibar_text(text=t)
                name, ext = os.path.splitext(p=img_src.split("/")[-1])

                if not self._copy_img(src=img_src, dest=downloads, name=name, ext=ext):
                    continue
                
            subprocess.Popen(args=["open", downloads])
