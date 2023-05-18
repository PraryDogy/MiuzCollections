import calendar
import os
import re
import shutil
import subprocess
import sys
import textwrap
import threading
import tkinter
import traceback
from datetime import datetime
from functools import partial
from tkinter import filedialog, ttk

import cv2
import sqlalchemy
import tkmacosx
from PIL import Image, ImageTk

import cfg
from database import *
from scaner import *
from utils import *

from .menu import *
from .st_bar import *
from .thumbnails import *
from .widgets import *


__all__ = (
    "app"
    )


class Application:
    def __init__(self):
        cfg.ROOT.title(cfg.APP_NAME)
        cfg.ROOT.configure(bg=cfg.BG)

        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', lambda: cfg.ROOT.deiconify())

        cfg.ROOT.bind('<Command-w>', lambda e: cfg.ROOT.iconify())

        if cfg.config["ASK_EXIT"] == 1:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", AskExit)
            cfg.ROOT.createcommand("tk::mac::Quit" , AskExit)
        else:
            cfg.ROOT.createcommand("tk::mac::Quit" , on_exit)
            cfg.ROOT.protocol("WM_DELETE_WINDOW", on_exit)
        

        CSep(cfg.ROOT).pack(fill=tkinter.X, pady=15, padx=(15, 5))

        self.menu = Menu(cfg.ROOT)
        self.menu.pack(side=tkinter.LEFT, fill=tkinter.Y, pady=(0, 15))

        right_frame = CFrame(cfg.ROOT)
        right_frame.pack(fill=tkinter.BOTH, expand=1)
    
        self.thumbnails = Thumbnails(right_frame)
        self.thumbnails.pack(fill=tkinter.BOTH, expand=1, padx=(15, 5))

        CSep(right_frame).pack(fill=tkinter.X, pady=10, padx=15)

        self.st_bar = StBar(right_frame)
        self.st_bar.pack(pady=(0, 10))

        MacMenu()

        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')

        if cfg.config['ROOT_W'] < 50 or cfg.config['ROOT_H'] < 50:
            cfg.config['ROOT_W'], cfg.config['ROOT_H'] = 700, 500

        cfg.ROOT.geometry(
            (f"{cfg.config['ROOT_W']}x{cfg.config['ROOT_H']}"
            f"+{cfg.config['ROOT_X']}+{cfg.config['ROOT_Y']}")
            )
        cfg.ROOT.minsize(800, 500)


app = Application()