import os
import threading
import traceback

import cfg
import yadisk

from .Gui import Create as DbGui


def DownloadDb():
    y = yadisk.YaDisk(token=cfg.YADISK_TOKEN)
    localDirDb = os.path.join(cfg.DB_DIR, cfg.DB_NAME)
    yadiskDirDb = os.path.join(cfg.YADISK_DIR, cfg.DB_NAME)

    try:
        y.download(yadiskDirDb, localDirDb)

    except Exception:
        print(traceback.format_exc())
        
        
def Check():
    '''
    \nCheck folder with db. Folder path in cfg.py
    \nCreate folder if not exists
    \nCheck database file in folder. Filename in cfg.py
    \nIf file not exists or size==0kb:
    \nRun with threading file downloader and run gui with download status
    '''
    if not os.path.exists(cfg.DB_DIR):
        os.makedirs(cfg.DB_DIR)

    db = os.path.join(cfg.DB_DIR, cfg.DB_NAME)
    
    if (not os.path.exists(db) or 
        os.path.getsize(db) < 0.9):
        
        dbGui = DbGui()

        checkDbTask = threading.Thread(
            target=lambda: DownloadDb())
        checkDbTask.start()
        
        while checkDbTask.is_alive():
            cfg.ROOT.update()

        dbGui.destroy()
