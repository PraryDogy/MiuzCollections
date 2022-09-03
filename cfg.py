import json
import os
import tkinter

# app info
APP_NAME = 'MiuzGallery'
APP_VER = '2.8.0'

# database info
DB_VER = '2.6.1'
DB_DIR = os.path.join(
    os.path.expanduser('~'), 
    'Library', 'Application Support', 'Miuz Gallery'
    )
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

# for downloading database from Yandex Disk
YADISK_TOKEN = "AQAAAAARTU_6AAgMRGzO_kyAykpGqUubuGuraCg"
YADISK_DIR = '/miuzgall'

# There is default values on 22.08.2022
defaults = {    
    'PHOTO_DIR': '/Volumes/Shares/Marketing/Photo',
    'COLL_FOLDER': '_Collections',
    'RT_FOLDER': 'Retouch',
    'FILE_AGE':60
    }
        
if os.path.exists(os.path.join(DB_DIR, 'cfg.json')):
    with open(os.path.join(DB_DIR, 'cfg.json'), 'r') as file:
        data = json.load(file)
else:
    with open(os.path.join(DB_DIR, 'cfg.json'), 'w') as file:
        json.dump(defaults, file, indent=4,)
        data = defaults

PHOTO_DIR = data['PHOTO_DIR']
COLL_FOLDER = data['COLL_FOLDER']
RT_FOLDER = data['RT_FOLDER']
FILE_AGE = data['FILE_AGE']