import os
import subprocess
import threading
import tkinter
from datetime import datetime
from functools import partial

import cfg
from utils import MyButton, MyFrame, MyLabel, get_coll_name, my_copy, smb_check

from .ask_exit import AskExit
from .smb_checker import SmbChecker


def on_closing():
    if cfg.COMPARE:
        cfg.COMPARE = False
        cfg.STATUSBAR_NORMAL()
        [i.configure(bg=cfg.BGCOLOR) for i in cfg.THUMBS]


    all = tuple(i for i in cfg.ROOT.winfo_children())
    windows = tuple(i for i in all if isinstance(i, tkinter.Toplevel))
    [i.destroy() for i in windows]

    cfg.ROOT.focus_force()


class BaseWindow(tkinter.Toplevel):
    def __init__(self):
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        if not smb_check():
            on_closing()
            SmbChecker()
            return

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing())
        self.bind('<Command-w>', lambda e: on_closing())
        self.bind('<Escape>', lambda e: on_closing())
        self.bind('<Command-q>', lambda e: AskExit(cfg.ROOT))
        self.title('Просмотр')
        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')


class CloseButton(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=1, width=13)
        self.cmd(lambda e: on_closing())


class BaseImgButtons(MyFrame):
    def __init__(self, master, img_src):
        MyFrame.__init__(self, master)
        self.img_src = img_src

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=13)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        open_btn = MyButton(self, text='Открыть папку')
        open_btn.configure(height=1, width=13)
        open_btn.cmd(partial(self.open_folder, open_btn))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def copy_name(self, btn: MyButton):
        btn.press()
        my_copy(self.img_src.split(os.sep)[-1].split('.')[0])

    def open_folder(self, btn: MyButton, e: tkinter.Event):
        btn.press()
        path = os.sep.join(self.img_src.split(os.sep)[:-1])

        def open():
            subprocess.check_output(["/usr/bin/open", path])

        threading.Thread(target=open).start()







 