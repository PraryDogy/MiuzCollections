import os
import shutil
import tkinter

from utils import read_cfg, write_cfg

# app info
APP_NAME = 'MiuzCollections'
DB = "db.db"
APP_VER = '3.5.3'

CFG_DIR = os.path.join(
    os.path.expanduser("~"),
    f"Library/Application Support/{APP_NAME}"
    )

# gui settings
FONT = "#E2E2E2"
BG = "#19191B"
BUTTON = "#2A2A2D"
# SELECTED = '#0056D9'
SELECTED = "#4B4B4B"
HOVERED = '#3A3A3E'

THUMB_SIZE = 150
LIMIT = 150

# flags
FLAG = False
SCANER_TASK = None

LIVE_TEXT = ""

# gui objects for global access
ROOT = tkinter.Tk()
ROOT.withdraw()
THUMBNAILS: tkinter.Frame = None
MENU: tkinter.Frame = None
ST_BAR: tkinter.Frame = None

default_vars = {
        'COLL_FOLDER': '/Volumes/Shares/Marketing/Photo/_Collections',

        'CURR_COLL': 'last',
        'ASK_EXIT': 1,

        "ROOT_W": 700,
        "ROOT_H": 500,
        "ROOT_X": 100,
        "ROOT_Y": 100,

        "PREVIEW_W": 700,
        "PREVIEW_H": 500,

        "STOPWORDS": ["preview", "1x1", "1х1", "crop", "копия", "copy"],

        "//READ_ME1": "Вы можете изменить только параметр STOPWORDS",
        "//READ_ME2": "Это список слов, которые исключаются при поиске .tiff файлов",
        "//READ_ME3": "Например .jpeg называется 'котик_preview.jpeg'",
        "//READ_ME4": "и если в списке STOPWORDS есть слово 'preview'",
        "//READ_ME5": "то программа будет искать все .tiff файлы с именем 'котик'",
        "//READ_ME6": "исключая слово 'preview'"
        }

if not os.path.exists(CFG_DIR):
    os.mkdir(CFG_DIR)

if not os.path.exists(os.path.join(CFG_DIR, "cfg.json")):
    config = default_vars
    write_cfg(default_vars)

if not os.path.exists(os.path.join(CFG_DIR, DB)):
    shutil.copyfile(DB, os.path.join(CFG_DIR, DB))


config = read_cfg()

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
