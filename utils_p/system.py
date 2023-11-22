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