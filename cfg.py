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
APP_VER = '3.0.8'

KEY = 'QaovKbF1YpKCM9e-HE2wvn30lIqCbeYTUcONcdLpV18='

# database info
CFG_DIR = os.path.join(
    os.path.expanduser('~'), 'Library', 'Application Support', 'Miuz Gallery')

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


def default_size():
    ROOT.update_idletasks()
    if ROOT.winfo_screenwidth() > 150*8:
        return f'{150*8}x{int(ROOT.winfo_screenheight()*0.8)}'
    else:
        w = int(ROOT.winfo_screenwidth()*0.7)
        h = int(ROOT.winfo_screenheight()*0.8)
        return f'{w}x{h}'


def defaults():
    return {
        'PHOTO_DIR': os.path.join(
            os.sep, 'Volumes', 'Shares', 'Marketing', 'Photo'),
        'COLL_FOLDER': os.path.join(
            os.sep, 'Volumes', 'Shares', 'Marketing', 'Photo', '_Collections'),
        'RT_FOLDER': 'Retouch',
        'FILE_AGE': 60,
        'ROOT_SIZE': default_size(),
        'ROOT_POS': '+0+0'
        }


def read_cfg():
    """
    Decrypts `cfg.json` from `cfg.CFG_DIR` and returns dict.
    """
    key = Fernet(KEY)

    with open(os.path.join(CFG_DIR, 'cfg.json'), 'rb') as file:
        data = file.read()

    try:
        return json.loads(key.decrypt(data).decode("utf-8"))
    except InvalidToken:
        data = defaults()
        encrypt_cfg(data)
        return data


if not os.path.exists(CFG_DIR):
    os.mkdir(CFG_DIR)

if not os.path.exists(os.path.join(CFG_DIR, 'database.db')):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), 'database.db'),
        os.path.join(CFG_DIR, 'database.db'),
        )

if os.path.exists(os.path.join(CFG_DIR, 'cfg.json')):
    config = read_cfg()
else:
    encrypt_cfg(defaults())
    config = defaults()

for i in defaults().keys():
    try:
        config[i]
    except KeyError or TypeError:
        config = encrypt_cfg(defaults())
