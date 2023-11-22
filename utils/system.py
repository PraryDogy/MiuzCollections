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



    

def run_applescript(applescript: Literal["applescript"]):
    args = [
        arg for row in applescript.split("\n")
        for arg in ("-e", row.strip())
        if row.strip()
        ]
    subprocess.call(args=["osascript"] + args)


def reveal_files(paths: tuple[Literal["file path"], ...]):
    cnf.notibar_text(cnf.lng.please_wait)

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

    run_applescript(applescript)