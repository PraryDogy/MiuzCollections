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

with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'r') as file:
    config = json.load(file)

widgets = {
    'settings_win': tkinter.Toplevel,
    'gen_frame': tkinter.Frame,
    'adv_frame': tkinter.Frame,
    'gen_btn': tkinter.Button,
    'adv_btn': tkinter.Button,
    'PHOTODIR_LBL': tkinter.Label,
    'COLLFOLDERS_LBL': tkinter.Label,
    'RTFOLDER_ENTRY': tkinter.Entry,
    'FILEAGE_ENTRY':tkinter.Entry,
    }


class Settings(tkinter.Toplevel):
    """
    Tkinter toplevel with settings gui.
    """

    def __init__(self):
        tkinter.Toplevel.__init__(self, cfg.ROOT, bg=cfg.BGCOLOR)
        widgets['settings_win'] = self
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind('<Command-w>', lambda e: self.destroy())
        self.bind('<Command-q>', lambda e: quit())

        self.withdraw()
        # self.resizable(0,0)
        self.title('Настройки')
        self.geometry('570x650')
        self.configure(padx=10, pady=10)

        frame_up = MyFrame(self)
        frame_up.pack(fill=tkinter.BOTH, expand=True)

        frame_bott = MyFrame(self)
        frame_bott.pack()

        LeftMenu(frame_up).pack(side=tkinter.LEFT, padx=(0, 10))

        General(frame_up).pack(fill=tkinter.BOTH, expand=True)
        Expert(frame_up)

        BelowMenu(frame_bott).pack(pady=(10,0))

        place_center(self)

        self.deiconify()
        self.grab_set()


class LeftMenu(MyFrame):
    """
    Menu with buttons "General settins" and "Advanced settings".
    param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        widgets['gen_btn'] = MyButton(self, text='Основные')
        widgets['gen_btn'].configure(bg=cfg.BGPRESSED)

        widgets['gen_btn'].cmd(lambda e: self.change(
            kill=widgets['adv_frame'], pack=widgets['gen_frame'],
            press=widgets['gen_btn'], clear=widgets['adv_btn']))
        widgets['gen_btn'].pack()

        widgets['adv_btn'] = MyButton(self, text = 'Дополнительно')

        widgets['adv_btn'].cmd(lambda e: self.change(
            kill=widgets['gen_frame'], pack=widgets['adv_frame'],
            press=widgets['adv_btn'], clear=widgets['gen_btn']))
        widgets['adv_btn'].pack()

    def change(self, **kw):
        """
        Destroys frame, creates new one.
        Press button with created frame and clear button with destroyed frame.

        * params: `kill`, `pack`, `press`, `clear`
        * param `kill`: tkinter frame for destroy
        * param `pack`: tkinter frame for pack: fill both, expand is True
        * param `press`: changes tkinter button bg to cfg.BGPRESSED
        * param `clear`: changes tkinter button bg to cfg.BGBUTTON
        """
        kw['kill'].pack_forget()
        kw['pack'].pack(fill=tkinter.BOTH, expand=True)

        kw['press'].configure(bg=cfg.BGPRESSED)
        kw['clear'].configure(bg=cfg.BGBUTTON)


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

        config['PHOTO_DIR'] = widgets['PHOTODIR_LBL']['text']
        config['COLL_FOLDERS'] = [widgets['COLLFOLDERS_LBL']['text']]
        config['RT_FOLDER'] = widgets['RTFOLDER_ENTRY'].get()
        config['FILE_AGE'] = widgets['FILEAGE_ENTRY'].get()

        with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
            json.dump(config, file, indent=4)

        self.winfo_toplevel().destroy()


class General(MyFrame):
    """
    Tkinter frame with general app settings.
    * param `master`: tkinter frame
    """
    def __init__(self, master):
        MyFrame.__init__(self, master, padx=15)
        widgets['gen_frame'] = self

        title = MyLabel(self, text='Основные', font=('Arial', 22, 'bold'))
        title.pack(pady=10)

        txt1 = (
            'При запуске программа сканирует и обновляет фото'
            f'\nвсех коллекций за последние {cfg.FILE_AGE} дней.'
            '\nНажмите "Обновить", чтобы повторно запустить сканирование.')

        descr_updater = MyLabel(self)
        descr_updater.configure(
            text=txt1, justify=tkinter.LEFT, wraplength=350)
        descr_updater.pack(pady=(0, 10), anchor=tkinter.W)

        img_path = os.path.join(os.path.dirname(__file__), 'upd.png')
        img_src = Image.open(img_path)
        img_copy= img_src.copy()
        img_tk = ImageTk.PhotoImage(img_copy)

        img_lbl = MyLabel(self)
        img_lbl.configure(image=img_tk)
        img_lbl.pack()
        img_lbl.image_names = img_tk

        sep = Separator(self, orient='horizontal')
        sep.pack(padx=40, pady=20, fill=tkinter.X)

        txt2 = (
            'Нажмите "Полное сканирование", чтобы обновить'
            '\nфотографии всех коллекций за все время c 2018 года.')
        descr_scan = MyLabel(self)
        descr_scan.configure(
            text=txt2, justify=tkinter.LEFT, wraplength=350)
        descr_scan.pack(pady=(0, 10), anchor=tkinter.W)

        scan_btn = MyButton(self, text='Полное сканирование')
        scan_btn.cmd(lambda e: self.full_scan())
        scan_btn.pack(anchor='center')

        sep = Separator(self, orient='horizontal')
        sep.pack(padx=40, pady=(25, 20), fill=tkinter.X)

        author_txt = (
            f'{cfg.APP_NAME} {cfg.APP_VER}'
            '\nCreated by Evgeny Loshkarev'
            '\nCopyright © 2022 MIUZ Diamonds.'
            '\nAll rights reserved.')

        author_lbl = MyLabel(self)
        author_lbl.configure(
            text=author_txt, justify=tkinter.LEFT)
        author_lbl.pack(anchor=tkinter.W)

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
        tkmacosx.SFrame.__init__(self, master, padx=15)
        self.configure(bg=cfg.BGCOLOR, scrollbarwidth=7)
        self.configure(avoidmousewheel=(self))
        widgets['adv_frame'] = self

        title = MyLabel(self, text='Дополнительно', font=('Arial', 22, 'bold'))
        title.pack(pady=10)

        for descr, value, widget in zip(
            [descriptions['PHOTO_DIR'], descriptions['COLL_FOLDERS']],
            [config['PHOTO_DIR'], config['COLL_FOLDERS']],
            ['PHOTODIR_LBL', 'COLLFOLDERS_LBL']):

            gallery_descr = MyLabel(
                self, text=descr, justify=tkinter.LEFT, anchor=tkinter.W)
            gallery_descr.pack(anchor=tkinter.W)

            gallery_frame = MyFrame(self)
            gallery_frame.pack(fill=tkinter.X)

            gallery_btn = MyButton(gallery_frame, text='Обзор')
            gallery_btn.pack(side=tkinter.LEFT, anchor=tkinter.W, pady=(10, 0))
            gallery_btn.configure(height=1, width=9)


            widgets[widget] = MyLabel(
                gallery_frame, text=value, justify=tkinter.LEFT,
                anchor=tkinter.W)
            widgets[widget].pack(
                side=tkinter.LEFT, anchor=tkinter.W, 
                padx=(10, 0), pady=(10, 0))

            gallery_btn.cmd(
                lambda e, x=widgets[widget]: self.select_path(x))

            sep = Separator(self, orient='horizontal')
            sep.pack(padx=40, pady=20, fill=tkinter.X)


        for descr, value, widget in zip(
            [descriptions['RT_FOLDER'], descriptions['FILE_AGE']],
            [config['RT_FOLDER'], config['FILE_AGE']],
            ['RTFOLDER_ENTRY', 'FILEAGE_ENTRY']):

            lbl = MyLabel(
                self, justify=tkinter.LEFT, wraplength=340, text=descr)
            lbl.pack(anchor=tkinter.W, pady=(0, 10))

            widgets[widget] = tkinter.Entry(
                self, bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
                insertbackground=cfg.FONTCOLOR, selectbackground=cfg.BGPRESSED,
                highlightthickness=5, highlightbackground=cfg.BGBUTTON,
                highlightcolor=cfg.BGBUTTON, bd=0, justify='center', width=35)

            widgets[widget].insert(0, value)
            widgets[widget].pack(pady=(0, 10))

            frame_btns = MyFrame(self)
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

            sep = Separator(self, orient='horizontal')
            sep.pack(padx=40, pady=20, fill=tkinter.X)

        rest_frame = MyFrame(self)
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
            [cfg.defaults['PHOTO_DIR'], cfg.defaults['COLL_FOLDERS']],
            ['PHOTO_DIR', 'COLL_FOLDERS']):

            widget['text'] = default
            config[value] = default

        for widget, default, value in zip(
            [widgets['RTFOLDER_ENTRY'], widgets['FILEAGE_ENTRY']],
            [cfg.defaults['RT_FOLDER'], cfg.defaults['FILE_AGE']],
            ['RT_FOLDER', 'FILE_AGE']):

            widget.delete(0, 'end')
            widget.insert(0, default)
            config[value] = default

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
