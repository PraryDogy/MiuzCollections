import os
import subprocess
import tkinter
import traceback

try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal

import io
import traceback

from PIL import Image

from cfg import cnf
from database import *


class SysUtils:
    ww = 150

    def run_applescript(self, script: Literal["applescript"]):
        args = [
            arg for row in script.split("\n")
            for arg in ("-e", row.strip())
            if row.strip()
            ]
        subprocess.call(args=["osascript"] + args)

    def print_err(self, write=False):
        print(traceback.format_exc())

        if write:
            with open(os.path.join(cnf.cfg_dir, "err.txt"), "a") as f:
                f.write(traceback.format_exc())

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

    def decode_image(self, img: bytes) -> Image:
        return Image.open(fp=io.BytesIO(img))

    def crop_image(self, img: Image) -> Image:
        width, height = img.size   # Get dimensions
        left = (width - __class__.ww)/2
        top = (height - __class__.ww)/2
        right = (width + __class__.ww)/2
        bottom = (height + __class__.ww)/2
        return img.crop((left, top, right, bottom))
    