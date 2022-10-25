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
APP_VER = '3.0.9'

KEY = 'QaovKbF1YpKCM9e-HE2wvn30lIqCbeYTUcONcdLpV18='

# database info
CFG_DIR = os.path.join(
    os.path.expanduser('~'), 'Library/Application Support/Miuz Gallery')

FONTCOLOR = "#E2E2E2"
BGCOLOR = "#222222"
BGBUTTON = "#434343"
BGPRESSED = '#395432'

# tkinter global variables for avaibility from any place
ROOT = tkinter.Tk()
ROOT.withdraw()
LIVE_LBL = tkinter.Label
FLAG = True
IMAGES_RESET = object


def defaults():
    return {
        'APP_VER': APP_VER,
        'PHOTO_DIR': '/Volumes/Shares/Marketing/Photo',
        'COLL_FOLDER': '/Volumes/Shares/Marketing/Photo/_Collections',
        'RT_FOLDER': 'Retouch',
        'FILE_AGE': 60,
        'ROOT_SIZE': '500x500',
        'ROOT_POS': '+0+0',
        'CURR_COLL': 'last',
        'TYPE_SCAN': '',
        }


def read_cfg(what_read):
    """
    Decrypts `cfg.json` from `cfg.CFG_DIR` and returns dict.
    """
    key = Fernet(KEY)
    with open(what_read, 'rb') as file:
        data = file.read()
    try:
        return json.loads(key.decrypt(data).decode("utf-8"))
    except InvalidToken:
        config = defaults()
        encrypt_cfg(config)

        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), 'database.db'),
            os.path.join(CFG_DIR, 'database.db'))

        return config


if not os.path.exists(CFG_DIR):
    os.mkdir(CFG_DIR)

if os.path.exists(os.path.join(CFG_DIR, 'cfg')):
    config = read_cfg(os.path.join(CFG_DIR, 'cfg'))
else:
    config = defaults()
    encrypt_cfg(config)

if not os.path.exists(os.path.join(CFG_DIR, 'database.db')):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), 'database.db'),
        os.path.join(CFG_DIR, 'database.db'))