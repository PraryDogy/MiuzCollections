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
from tkinter import filedialog

import cv2
import sqlalchemy
import tkmacosx
from PIL import Image, ImageTk

import cfg
from database import Dbase, Thumbs
from scaner import *
from utils import *

from .mac_menu import MacMenu
from .menu import Menu
from .st_bar import StBar
from .thumbnails import Thumbnails
from .widgets import AskExit, CFrame, CSep

__all__ = (
    "Gui"
    )


class Gui:
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

        menu_widget = Menu(cfg.ROOT)
        menu_widget.pack(side=tkinter.LEFT, fill=tkinter.Y, pady=(0, 15))

        right_frame = CFrame(cfg.ROOT)
        right_frame.pack(fill=tkinter.BOTH, expand=1)
    
        gallery_widget = Thumbnails(right_frame)
        gallery_widget.pack(fill=tkinter.BOTH, expand=1, padx=(15, 5))

        CSep(right_frame).pack(fill=tkinter.X, pady=10, padx=15)

        stbar_widget = StBar(right_frame)
        stbar_widget.pack(pady=(0, 10))

        MacMenu()

        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')

        if cfg.config['ROOT_W'] < 50 or cfg.config['ROOT_H'] < 50:
            cfg.config['ROOT_W'], cfg.config['ROOT_H'] = 700, 500

        cfg.ROOT.geometry(
            (f"{cfg.config['ROOT_W']}x{cfg.config['ROOT_H']}"
            f"+{cfg.config['ROOT_X']}+{cfg.config['ROOT_Y']}")
            )