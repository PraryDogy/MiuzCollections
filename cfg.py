import json
import os
import tkinter

APP_VER = '2.6.2'
DB_VER = '2.6.1'
DB_DIR = os.path.join(
    os.path.expanduser('~'), 
    'Library/Application Support/Miuz Gallery'
    )
DB_NAME = f'database{DB_VER}.db'

FONTCOLOR = "#E2E2E2"
BGCOLOR = "#222222"
BGBUTTON = "#434343"
BGPRESSED = '#395432'

ROOT = tkinter.Tk()
FLAG = True
LIVE_LBL = None


"""There is default values on 22.08.2022"""

data = {
    'YADISK_TOKEN': "AQAAAAARTU_6AAgMRGzO_kyAykpGqUubuGuraCg",
    'YADISK_DIR': '/miuzgall',
    
    'SMB_DIR': '/Volumes/Shares',
    'SMB_CONN': 'smb://192.168.10.105/Shares',
    
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
        json.dump(data, file, indent=4,)


YADISK_TOKEN = data['YADISK_TOKEN']
YADISK_DIR = data['YADISK_DIR']

# SMB_DIR = '/'
SMB_DIR = data['SMB_DIR']
SMB_CONN = data['SMB_CONN']

# PHOTO_DIR = '/Users/evlosh/Downloads/MiuzGallery/MiuzGallery/SamplePhotos'
PHOTO_DIR = data['PHOTO_DIR']

COLL_FOLDER = data['COLL_FOLDER']
RT_FOLDER = data['RT_FOLDER']
FILE_AGE = data['FILE_AGE']