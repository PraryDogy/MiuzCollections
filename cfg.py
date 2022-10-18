"""
Global variables & settings.
"""

import json
import os
import tkinter


# app info
APP_NAME = 'MiuzGallery'
APP_VER = '2.9.9'

# database info
DB_VER = '2.6.2'
DB_DIR = os.path.join(
    os.path.expanduser('~'), 'Library', 'Application Support', 'Miuz Gallery')
DB_NAME = f'database{DB_VER}.db'

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

IMAGES_COMPARE = set()
IMAGES_INFO = []
IMAGES_SRC = []


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


def create_json():
    with open(os.path.join(DB_DIR, 'cfg.json'), 'w') as file:
        defaul = defaults()
        json.dump(defaul, file, indent=4,)
        return defaul


if not os.path.exists(DB_DIR):
    os.mkdir(DB_DIR)

if os.path.exists(os.path.join(DB_DIR, 'cfg.json')):
    with open(os.path.join(DB_DIR, 'cfg.json'), 'r') as file:
        config = json.load(file)
else:
    config = create_json()

for i in defaults().keys():
    try:
        config[i]
    except KeyError:
        config = create_json()


