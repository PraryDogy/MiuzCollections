import os
import subprocess
import threading
import tkinter
import traceback

import cfg
import cv2
import yadisk
from DataBase import Database

from Utils.Styled import *


def CreateThumb(imgPath):
    """Returns list with 4 square thumbnails: 150, 200, 250, 300"""
    
    img = cv2.imread(imgPath)
    width, height = img.shape[1], img.shape[0]
    
    if height >= width:
        diff = int((height-width)/2)
        new_img = img[diff:height-diff, 0:width]

    else:
        diff = int((width-height)/2)
        new_img = img[0:height, diff:width-diff]       

    resized = list()
    
    for size in [(150, 150), (200, 200), (250, 250), (300, 300)]:
        newsize = cv2.resize(
            new_img, size, interpolation = cv2.INTER_AREA)
        encoded = cv2.imencode('.jpg', newsize)[1].tobytes()
        resized.append(encoded)    
        
    return resized


def MyCopy(output):
    """Custom copy to clipboard with subprocess"""
    
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))
    print('copied')


def MyPaste():
    """Custom paste from clipboard with subprocess"""
    
    print('pasted')
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


def ReloadGallery():
    """Destroy cfg.IMG_GRID frame with thumbmails,
    create new tkinter frame cfg.IMG_GRID and put in it new thumbnails"""
    
    cfg.IMG_GRID.destroy()
    imgFrame = tkinter.Frame(cfg.UP_FRAME, bg=cfg.BGCOLOR)
    imgFrame.pack(side='left', fill='both', expand=True)
    cfg.IMG_GRID = imgFrame
    
    cfg.GRID_GUI()
    

class SmbChecker(tkinter.Toplevel):
    """Methods: Check"""
    
    def __init__(self):
        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR, padx=10, pady=10)
        self.withdraw()

    def Check(self):
        if not os.path.exists(cfg.PHOTO_DIR):
            if not self.Connect():
                self.Gui()
                return False
        self.destroy()
        return True

    def Connect(self):
        os.system(f"osascript -e 'mount volume \"{cfg.SMB_CONN}\"'")
        if not os.path.exists(cfg.PHOTO_DIR):
            return False
        return True

    def Gui(self):
        self.focus_force()
        self.title('Нет подключения')
        self.resizable(0,0)
        self.attributes('-topmost', 'true')
        
        txt = 'Нет подключения к сетевому диску Miuz. '
        titleLbl = MyLabel(
            self, text=txt, wraplength=350, font=('Arial', 10, 'bold'))
        titleLbl.pack(pady=(0, 20))

        txt2 =(
            'Программа работает в офлайн режиме. '
            '\n- Проверьте подключение к интернету. '
            '\n- Откройте любую папку на сетевом диске,'
            '\nвведите логин и пароль, если требуется'
            '\n- Откройте настройки > эксперт, введите правильный адрес '
            '\nи перезапустите приложение.'  
            '\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        descrLbl = MyLabel(self, text=txt2, justify='left')
        descrLbl.pack(padx=15, pady=(0, 15))

        clsBtn = MyButton(self, text='Закрыть')
        clsBtn.Cmd(lambda event: self.destroy())
        clsBtn.pack()

        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.deiconify()
        
        
class DbCkecker(tkinter.Toplevel):
    def __init__(self):        
        """Methods: Check."""

        tkinter.Toplevel.__init__(
            self, bg=cfg.BGCOLOR, padx=15, pady=10)
        self.withdraw()
   
    def Check(self):
        """Check db & folder db is exists. 
        If not exists, run gui and wait for download db with threading, 
        than destroy gui.
        If can't download, create empty Database with tables and values."""
        
        if not os.path.exists(cfg.DB_DIR):
            os.makedirs(cfg.DB_DIR)

        db = os.path.join(cfg.DB_DIR, cfg.DB_NAME)
        
        if (not os.path.exists(db) or 
            os.path.getsize(db) < 0.9):
            
            self.Gui()
            checkDbTask = threading.Thread(target=lambda: self.DownloadDb())
            checkDbTask.start()
            
            while checkDbTask.is_alive():
                cfg.ROOT.update()
        self.destroy()

    def DownloadDb(self):
        """Download database file  with thumbnails from Yandex Disk or
        create new one with tables and values if download fails."""
        
        y = yadisk.YaDisk(token=cfg.YADISK_TOKEN)
        localDirDb = os.path.join(cfg.DB_DIR, cfg.DB_NAME)
        yadiskDirDb = os.path.join(cfg.YADISK_DIR, cfg.DB_NAME)

        try:
            y.download(yadiskDirDb, localDirDb)

        except Exception:
            adm = Database.Utils()
            adm.Create()
            adm.FillConfig()
            print(traceback.format_exc())

    def Gui(self):
        """Create gui with text: Wait, downloading"""
        self.focus_force()
        self.title('Подождите')
        self.resizable(0,0)

        txt = 'Пожалуйста, подождите.'
        titleLbl = MyLabel(
            self, text=txt, wraplength=350, font=('Arial', 18, 'bold'))
        titleLbl.pack(pady=(0, 10))

        descr = MyLabel(self, text='Скачиваю дополнения.')
        descr.pack()
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.deiconify()