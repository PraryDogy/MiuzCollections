import json
import os
import shutil
import tkinter

# app info
APP_NAME = 'MiuzCollections'
DB = "db.db"
APP_VER = '3.6.0'

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

default_vars = {
        'COLL_FOLDER': '/Volumes/Shares/Marketing/Photo/_Collections',

        'CURR_COLL': 'last',
        'SORT_MODIFIED': True,
        'ASK_EXIT': 0,

        "ROOT_W": 700,
        "ROOT_H": 500,
        "ROOT_X": 100,
        "ROOT_Y": 100,

        "PREVIEW_W": 700,
        "PREVIEW_H": 500,

        "STOPWORDS": [
            "preview", "1x1", "1х1", "crop", "копия", "copy"
            ],
        "EXCEPTIONS": ""
        }


def read_cfg():
    with open(os.path.join(CFG_DIR, 'cfg.json'), "r", encoding="utf8") as file:
        return json.loads(file.read())


def write_cfg(data: dict):
    try:
        json_data = read_cfg()
        config["STOPWORDS"] = json_data["STOPWORDS"]
    except Exception:
        print("cfg.py write_cfg no cfg file in application support")

    with open(os.path.join(CFG_DIR, 'cfg.json'), "w", encoding='utf8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


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
