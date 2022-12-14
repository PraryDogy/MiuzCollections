"""
Global variables & settings.
"""

import json
import os
import shutil
import tkinter

from cryptography.fernet import Fernet, InvalidToken

from utils import encrypt_cfg

# app info
APP_NAME = 'MiuzGallery'
APP_VER = '3.2.3'

DB_VER = '1.1'
DB_NAME = f'db {DB_VER}.db'

KEY = 'QaovKbF1YpKCM9e-HE2wvn30lIqCbeYTUcONcdLpV18='

# database info
CFG_DIR = os.path.join(
    os.path.expanduser('~'), 'Library/Application Support/Miuz Gallery')

BGFONT = "#E2E2E2"
BGCOLOR = "#1A1A1A"
BGBUTTON = "#2C2C2C"
BGPRESSED = '#395432'
BGSELECTED = '#4E4769'
THUMB_SIZE = 150

# tkinter global variables for avaibility from any place
ROOT = tkinter.Tk()
ROOT.withdraw()

MENU_W = 0
LIVE_LBL = tkinter.Label
THUMBS = []
FLAG = False
COMPARE = False
IMG_SRC = str

# gui functions 
THUMBNAILS_RELOAD = object
STBAR_NORM = object
STBAR_COMPARE = object
STBAR_WAIT = object


def defaults():
    return {
        'APP_VER': APP_VER,
        'PHOTO_DIR': '/Volumes/Shares/Marketing/Photo',
        'COLL_FOLDER': '/Volumes/Shares/Marketing/Photo/_Collections',
        'RT_FOLDER': 'Retouch',
        'FILE_AGE': 60,
        'GEOMETRY': [700, 500, 0, 0],
        'CURR_COLL': 'last',
        'TYPE_SCAN': '',
        'MINIMIZE': 1
        }


def read_cfg(what_read: str):
    """
    Decrypts `cfg.json` from `cfg.CFG_DIR` and returns dict.
    """
    key = Fernet(KEY)
    with open(what_read, 'rb') as file:
        data = file.read()
    try:
        return json.loads(key.decrypt(data).decode("utf-8"))
    except InvalidToken:
        # if config file is older than 3.0.8 version
        # that means indeed replace database file & config file
        config = defaults()
        encrypt_cfg(config)
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), 'db.db'),
            os.path.join(CFG_DIR, DB_NAME))
        return config


if not os.path.exists(CFG_DIR):
    os.mkdir(CFG_DIR)

if not os.path.exists(os.path.join(CFG_DIR, DB_NAME)):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), 'db.db'),
        os.path.join(CFG_DIR, DB_NAME))

for file in os.listdir(CFG_DIR):
    if file.endswith('.db') and file != DB_NAME:
        os.remove(os.path.join(CFG_DIR, file))

if os.path.exists(os.path.join(CFG_DIR, 'cfg')):
    config = read_cfg(os.path.join(CFG_DIR, 'cfg'))
else:
    config = defaults()
    encrypt_cfg(config)

defs = defaults()
part1 = {k:v for k, v in config.items() if k in defs.keys()}
part2 = {k:v for k, v in defs.items() if k not in config.keys()}
new_config = {**part1, **part2}
encrypt_cfg(new_config) if new_config.keys() != config.keys() else False
config = new_config if new_config.keys() != config.keys() else config
