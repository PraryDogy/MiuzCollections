import os
import tkinter

APP_VER = '2.6.2'
DB_VER = '2.6.1'
DB_DIR = os.path.join(
    os.path.expanduser('~'), 
    'Library/Application Support/Miuz Gallery'
    )
DB_NAME = f'database{DB_VER}.db'


YADISK_TOKEN = "AQAAAAARTU_6AAgMRGzO_kyAykpGqUubuGuraCg"
YADISK_DIR = '/miuzgall'

FONTCOLOR = "#E2E2E2"
BGCOLOR = "#222222"
BGBUTTON = "#434343"
BGPRESSED = '#3A453B'

ROOT = tkinter.Tk()
FLAG = True
LIVE_LBL = None

# changeable
SMB_DIR = '/Volumes/Shares'
SMB_CONN = 'smb://192.168.10.105/Shares'

PHOTO_DIR = '/Volumes/Shares/Marketing/Photo'
COLL_FOLDER = '_Collections'
RT_FOLDER = 'Retouch'
FILE_AGE = 60
