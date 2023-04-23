import os
import shutil
import tkinter

from utils import read_cfg, write_cfg

# app info
APP_NAME = 'MiuzPhoto'
APP_VER = '3.3.6'

CFG_DIR = os.path.join(
    os.path.expanduser('~'), f'Library/Application Support/{APP_NAME}')

# database info
DB_VER = '1.1'
DB_NAME = f'db {DB_VER}.db'

# gui settings
FONT = "#E2E2E2"
BG = "#1A1A1A"
BUTTON = "#2C2C2C"
PRESSED = '#395432'
SELECTED = '#4E4769'

THUMB_SIZE = 150
LIMIT = 150

# flags
FLAG = False
COMPARE = False
LIVE_TEXT = (
    "Created by Evgeny Loshkarev"
    "\nCopyright © 2023 MIUZ Diamonds."
    )

# gui objects for global access
ROOT = tkinter.Tk()
ROOT.withdraw()
GALLERY: tkinter.Frame = None
MENU: tkinter.Frame = None
ST_BAR: tkinter.Frame = None

default_vars = {
        'COLL_FOLDER': '/Volumes/Shares/Marketing/Photo/_Collections',

        'CURR_COLL': 'last',
        'MINIMIZE': 1,

        "ROOT_W": 700,
        "ROOT_H": 500,
        "ROOT_X": 0,
        "ROOT_Y": 0,

        "PREVIEW_W": 700,
        "PREVIEW_H": 500
        }

if not os.path.exists(CFG_DIR):
    os.mkdir(CFG_DIR)

if not os.path.exists(os.path.join(CFG_DIR, DB_NAME)):
    shutil.copyfile(
        os.path.join(os.path.dirname(__file__), 'db.db'),
        os.path.join(CFG_DIR, DB_NAME))

for file in os.listdir(CFG_DIR):
    if file.endswith('.db') and file != DB_NAME:
        os.remove(os.path.join(CFG_DIR, file))

if os.path.exists(os.path.join(CFG_DIR, 'cfg.json')):
    config = read_cfg()
else:
    config = default_vars
    write_cfg(config)

old_keys = {
    k:v 
    for k, v in config.items()
    if k in default_vars.keys()
    }

new_keys = {
    k:v for
    k, v in default_vars.items()
    if k not in config.keys()
    }

new_config = {**old_keys, **new_keys}

if new_config.keys() != config.keys():
    write_cfg(new_config)
    config = new_config
