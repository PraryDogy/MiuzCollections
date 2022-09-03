import os
import subprocess
import threading
import tkinter
import traceback

import cfg
import cv2
import yadisk
import database

from Utils.Styled import MyLabel, MyButton


def create_thumb(src):
    """Returns list with 4 square thumbnails: 150, 200, 250, 300"""

    img = cv2.imread(src)
    width, height = img.shape[1], img.shape[0]

    if height >= width:
        diff = int((height-width)/2)
        new_img = img[diff:height-diff, 0:width]

    else:
        diff = int((width-height)/2)
        new_img = img[0:height, diff:width-diff]

    resized = []

    for size in [(150, 150), (200, 200), (250, 250), (300, 300)]:
        newsize = cv2.resize(
            new_img, size, interpolation = cv2.INTER_AREA)
        encoded = cv2.imencode('.jpg', newsize)[1].tobytes()
        resized.append(encoded)

    return resized


def my_copy(output):
    """Custom copy to clipboard with subprocess"""

    process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'},
                                stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))
    print('copied')


def my_paste():
    """Custom paste from clipboard with subprocess"""

    print('pasted')
    return subprocess.check_output('pbpaste',
                                env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


class SmbChecker(tkinter.Toplevel):

    def __init__(self):
        """Methods: Check"""

        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR, padx=10, pady=10)
        self.withdraw()

    def check(self):
        """Checks smb availability with cfg.PHOTO_DIR os.exists method,
        e.g: /Volumes/Path/To/Photo/Dir
        If dir not exists, show gui with description and return False

        PHOTO_DIR and SMB_CONN can be changed in settings gui or in cfg.json
        Read cfg.py file."""

        if not os.path.exists(os.path.join(os.sep, *cfg.PHOTO_DIR.split('/'))):
            self.gui()
            return False
        self.destroy()
        return True

    def gui(self):
        """doc"""
        self.focus_force()
        self.title('Нет подключения')
        self.resizable(0,0)

        txt = 'Нет подключения к сетевому диску Miuz. '
        title_lbl = MyLabel(self, text=txt)
        title_lbl.pack(pady=(0, 20))

        txt2 =(
            'Программа работает в офлайн режиме. '
            '\n- Проверьте подключение к интернету. '
            '\n- Откройте любую папку на сетевом диске,'
            '\nвведите логин и пароль, если требуется'
            '\n- Откройте настройки > эксперт, введите'
            '\nправильный адрес и перезапустите приложение.'
            '\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        descr_lbl = MyLabel(self, text=txt2, justify=tkinter.LEFT)
        descr_lbl.pack(padx=15, pady=(0, 15))

        cls_btn = MyButton(self, text='Закрыть')
        cls_btn.Cmd(lambda e: self.destroy())
        cls_btn.pack()

        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.deiconify()
        self.grab_set()
