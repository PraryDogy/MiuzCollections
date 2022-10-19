"""
Tkinter toplevel gui with app settings.
"""

import json
import os
import shutil
import sys
import tkinter
from tkinter import filedialog
from tkinter.ttk import Separator

import cfg
import sqlalchemy
import tkmacosx
from database import Config, Dbase
from PIL import Image, ImageTk
from utils.utils import (MyButton, MyFrame, MyLabel, my_copy, my_paste,
                         place_center)

from .descriptions import descriptions


widgets = {
    'PHOTODIR_LBL': tkinter.Label,
    'COLLFOLDERS_LBL': tkinter.Label,
    'RTFOLDER_ENTRY': tkinter.Entry,
    'FILEAGE_ENTRY':tkinter.Entry,
    'text_length': 1,
    }


class Settings(tkinter.Toplevel):
    """
    Tkinter toplevel with settings gui.
    """

    def __init__(self):
        tkinter.Toplevel.__init__(self, cfg.ROOT, bg=cfg.BGCOLOR)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind('<Command-w>', lambda e: self.destroy())
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<Command-q>', lambda e: quit())

        self.withdraw()
        self.resizable(0,0)
        self.title('Настройки')
        self.configure(padx=20, pady=10)
        self.geometry(
            f'{int(cfg.ROOT.winfo_width()*0.5)}x'
            f'{int(cfg.ROOT.winfo_height()*0.8)}')

        cfg.ROOT.update_idletasks()
        widgets['text_length'] = int(self.winfo_width()*0.9)

        scrollable = tkmacosx.SFrame(
            self, bg=cfg.BGCOLOR, scrollbarwidth=7)
        scrollable.pack(fill=tkinter.BOTH, expand=True)

        General(scrollable)
        Expert(scrollable)
        BelowMenu(self).pack(pady=(10,0), padx=(0, 19))

        place_center(self)
        self.deiconify()
        self.grab_set()


class General(MyFrame):
    """
    Tkinter frame with general app settings.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        title = MyLabel(master, text='Основные', font=('Arial', 22, 'bold'))
        title.pack(pady=10)

        txt1 = (
            'При запуске программа сканирует и обновляет фото всех коллекций '
            f'за последние {cfg.config["FILE_AGE"]} дней. Нажмите "Обновить" '
            'в правом нижнем углу, чтобы повторно запустить сканирование.'
            )

        descr_updater = MyLabel(master)
        descr_updater.configure(
            text=txt1, justify=tkinter.LEFT,
            wraplength=widgets['text_length'])
        descr_updater.pack(pady=(0, 10), anchor=tkinter.W)

        txt2 = (
            'Нажмите "Полное сканирование", чтобы обновить фотографии всех '
            'коллекций за все время c 2018 года.'
            )
        descr_scan = MyLabel(master)
        descr_scan.configure(
            text=txt2, justify=tkinter.LEFT,
            wraplength=widgets['text_length'])
        descr_scan.pack(pady=(0, 5), anchor=tkinter.W)

        scan_btn = MyButton(master, text='Полное сканирование')
        scan_btn.configure(height=1, width=17)
        scan_btn.cmd(lambda e: self.full_scan())
        scan_btn.pack()

        sep = Separator(master, orient='horizontal')
        sep.pack(padx=40, pady=(25, 20), fill=tkinter.X)

    def full_scan(self):
        """
        Reload app and run Utils Scaner with full scan method.
        """
        Dbase.conn.execute(sqlalchemy.update(Config).where(
            Config.name=='typeScan').values(value='full'))
        os.execv(sys.executable, ['python'] + sys.argv)


class Expert(tkmacosx.SFrame):
    """
    Tkinter frame with advanced app settings.
    """
    def __init__(self, master):

        for descr, value, widget in zip(
            [descriptions['PHOTO_DIR'], descriptions['COLL_FOLDER']],
            [cfg.config['PHOTO_DIR'], cfg.config['COLL_FOLDER']],
            ['PHOTODIR_LBL', 'COLLFOLDERS_LBL']):

            gallery_descr = MyLabel(
                master, text=descr, justify=tkinter.LEFT,
                wraplength=widgets['text_length'])
            gallery_descr.pack(anchor=tkinter.W)

            widgets[widget] = MyLabel(
                master, text=value, justify=tkinter.LEFT,
                wraplength=widgets['text_length'])
            widgets[widget].pack(
                padx=(10, 0), pady=(5, 0))

            gallery_btn = MyButton(master, text='Обзор')
            gallery_btn.pack(
                pady=(5, 0), padx=(5, 0))
            gallery_btn.configure(height=1, width=9)

            gallery_btn.cmd(
                lambda e, x=widgets[widget]: self.select_path(x))

            sep = Separator(master, orient='horizontal')
            sep.pack(padx=40, pady=20, fill=tkinter.X)


        for descr, value, widget in zip(
            [descriptions['RT_FOLDER'], descriptions['FILE_AGE']],
            [cfg.config['RT_FOLDER'], cfg.config['FILE_AGE']],
            ['RTFOLDER_ENTRY', 'FILEAGE_ENTRY']):

            lbl = MyLabel(
                master, justify=tkinter.LEFT,
                wraplength=widgets['text_length'], text=descr)
            lbl.pack(anchor=tkinter.W, pady=(0, 10))

            widgets[widget] = tkinter.Entry(
                master, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
                insertbackground=cfg.FONTCOLOR, selectbackground=cfg.BGPRESSED,
                highlightthickness=5, highlightbackground=cfg.BGBUTTON,
                highlightcolor=cfg.BGBUTTON, bd=0, justify='center', width=35)

            widgets[widget].insert(0, value)
            widgets[widget].pack(pady=(0, 10))

            frame_btns = MyFrame(master)
            frame_btns.pack()

            btn_copy = MyButton(frame_btns, text='Копировать')
            btn_copy.configure(height=1, width=9)
            btn_copy.cmd(
                lambda e, x=widget, y=btn_copy: self.copy_input(x, y))
            btn_copy.pack(side=tkinter.LEFT, padx=(0, 10))

            btn_paste = MyButton(frame_btns, text='Вставить')
            btn_paste.configure(height=1, width=9)
            btn_paste.cmd(
                lambda e, x=widget, y=btn_paste: self.paste_input(x))
            btn_paste.pack(side=tkinter.RIGHT, padx=(0, 10))

            sep = Separator(master, orient='horizontal')
            sep.pack(padx=40, pady=20, fill=tkinter.X)

        rest_frame = MyFrame(master)
        rest_frame.pack(pady=(0, 15))

        restore_btn = MyButton(rest_frame, text='По умолчанию')
        restore_btn.configure(height=1, width=12)
        restore_btn.cmd(lambda e, x=restore_btn: self.restore(x))
        restore_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        reset_button = MyButton(rest_frame, text='Полный сброс')
        reset_button.configure(height=1, width=12)
        reset_button.cmd(lambda e: self.full_reset())
        reset_button.pack(side=tkinter.LEFT)

    def full_reset(self):
        shutil.rmtree(cfg.DB_DIR)
        os.execv(sys.executable, ['python'] + sys.argv)

    def select_path(self, widget):
        path = filedialog.askdirectory()

        if len(path) == 0:
            return

        widget['text'] = path

    def restore(self, btn):
        """
        Gets advanced settings values from cfg and write to cfg.json
        Sets default text in all text input fields in advanced settings.
        * param `btn`: current tkinter button
        """
        btn.press()

        for widget, default, value in zip(
            [widgets['PHOTODIR_LBL'], widgets['COLLFOLDERS_LBL']],
            [cfg.defaults['PHOTO_DIR'], cfg.defaults['COLL_FOLDER']],
            ['PHOTO_DIR', 'COLL_FOLDER']):

            widget['text'] = default
            cfg.config[value] = default

        for widget, default, value in zip(
            [widgets['RTFOLDER_ENTRY'], widgets['FILEAGE_ENTRY']],
            [cfg.defaults['RT_FOLDER'], cfg.defaults['FILE_AGE']],
            ['RT_FOLDER', 'FILE_AGE']):

            widget.delete(0, 'end')
            widget.insert(0, default)
            cfg.config[value] = default

    def copy_input(self, ins, btn):
        """
        Gets text from current text input field and copy to clipboard.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.press()
        my_copy(ins.get())

    def paste_input(self, ins, btn):
        """
        Gets text from clipboard and paste in text input field.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.press()
        ins.delete(0, 'end')
        ins.insert(0, my_paste())


class BelowMenu(MyFrame):
    """
    Creates tkinter frame with save settings button and close button.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        save_btn = MyButton(self, text='Сохранить')
        save_btn.cmd(lambda e: self.save_settings())
        save_btn.pack(side=tkinter.LEFT, padx=10)

        cancel_btn = MyButton(self, text='Отмена')
        cancel_btn.cmd(lambda e: self.cancel())
        cancel_btn.pack(side=tkinter.LEFT)

    def cancel(self):
        """
        Cancel button command.
        """
        self.winfo_toplevel().destroy()

    def save_settings(self):
        """
        Get text from all text fields in advanced settings and save to
        cfg.json
        """

        cfg.config['PHOTO_DIR'] = widgets['PHOTODIR_LBL']['text']
        cfg.config['COLL_FOLDER'] = widgets['COLLFOLDERS_LBL']['text']
        cfg.config['RT_FOLDER'] = widgets['RTFOLDER_ENTRY'].get()
        cfg.config['FILE_AGE'] = widgets['FILEAGE_ENTRY'].get()

        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(cfg.config, file, indent=4)

        self.winfo_toplevel().destroy()
