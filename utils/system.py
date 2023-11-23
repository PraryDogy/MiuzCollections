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
import traceback



class SysUtils:
    def run_applescript(self, script: Literal["applescript"]):
        args = [
            arg for row in script.split("\n")
            for arg in ("-e", row.strip())
            if row.strip()
            ]
        subprocess.call(args=["osascript"] + args)

    def print_err(self):
        print(traceback.format_exc())

    def smb_check(self) -> bool:
        return bool(os.path.exists(path=cnf.coll_folder))

    def on_exit(self, e: tkinter.Event = None):
        cnf.root_g.update(
            {"w": cnf.root.winfo_width(),
             "h": cnf.root.winfo_height(),
             "x": cnf.root.winfo_x(),
             "y": cnf.root.winfo_y()}
             )

        cnf.write_cfg()

        cnf.notibar_status = False
        cnf.scan_status = False
        quit()

    def get_coll_name(self, src: Literal["file path"]) -> Literal["collection name"]:
        coll = src.replace(cnf.coll_folder, "").strip(os.sep).split(os.sep)

        if len(coll) > 1:
            return coll[0]
        else:
            return cnf.coll_folder.strip(os.sep).split(os.sep)[-1]

    def place_center(self, win: tkinter.Toplevel, width: int, height: int,
                     parrent_win: tkinter.Toplevel = cnf.root):
        x, y = parrent_win.winfo_x(), parrent_win.winfo_y()
        xx = x + parrent_win.winfo_width() // 2 - width // 2
        yy = y + parrent_win.winfo_height() // 2 - height // 2
        win.geometry(f"+{xx}+{yy}")
