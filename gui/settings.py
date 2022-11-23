"""
Tkinter toplevel gui with app settings.
"""

import os
import shutil
import sys
import tkinter
from tkinter import filedialog

import cfg
import tkmacosx
from utils import (MyButton, MyFrame, MyLabel, MySep, encrypt_cfg, my_copy,
                   my_paste, place_center)

vars = {
    'PHOTODIR_LBL': 'tkinter label',
    'COLLFOLDERS_LBL': 'tkinter label',
    'RTFOLDER_ENTRY': 'tkinter entry',
    'FILEAGE_ENTRY':'tkinter entry',
    'text_length': 1,
    }


class Settings(tkinter.Toplevel):
    """
    Tkinter toplevel with settings gui.
    """

    def __init__(self):
        tkinter.Toplevel.__init__(self, cfg.ROOT, bg=cfg.BGCOLOR)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.bind('<Command-w>', lambda e: self.on_exit())
        self.bind('<Escape>', lambda e: self.on_exit())

        self.withdraw()
        self.title('Настройки')
        self.configure(padx=20, pady=10)
        self.geometry(
            f'{int(cfg.ROOT.winfo_width()*0.4)}x'
            f'{int(cfg.ROOT.winfo_height()*0.7)}')

        cfg.ROOT.update_idletasks()
        vars['text_length'] = int(self.winfo_width()*0.9)

        scrollable = tkmacosx.SFrame(
            self, bg=cfg.BGCOLOR, scrollbarwidth=7)
        scrollable.pack(fill=tkinter.BOTH, expand=True)

        bottom_frame = MyFrame(self)
        bottom_frame.pack(padx=(0, 7))

        Widgets(scrollable, bottom_frame)

        place_center(self)
        self.deiconify()
        self.grab_set()

    def on_exit(self):
        self.destroy()
        cfg.ROOT.focus_force()


class Widgets(MyFrame):
    """
    Tkinter frame with general app settings.
    * param `master`: tkinter frame
    """
    def __init__(self, master: tkmacosx.SFrame, bottom_frame: tkinter.Frame):
        title = MyLabel(master, text='Настройки', font=('Arial', 22, 'bold'))
        title.pack(pady=10)

        txt2 = (
            'При запуске программа сканирует и обновляет фото всех коллекций '
            f'за последние {cfg.config["FILE_AGE"]} дней'
            'Нажмите "Полное сканирование", чтобы обновить фотографии всех '
            'коллекций за все время c 2018 года.'
            )
        descr_scan = MyLabel(master)
        descr_scan.configure(
            text=txt2, justify=tkinter.LEFT,
            wraplength=vars['text_length'])
        descr_scan.pack(pady=(0, 5), anchor=tkinter.W)

        scan_btn = MyButton(master, text='Полное сканирование')
        scan_btn.configure(height=1, width=17)
        scan_btn.cmd(lambda e: self.full_scan())
        scan_btn.pack()

        sep = MySep(master)
        sep.pack(padx=40, pady=(40, 20), fill=tkinter.X)

        for title, value, widget in zip(
            ['Все фото.', 'Коллекции.'],
            [cfg.config['PHOTO_DIR'], cfg.config['COLL_FOLDER']],
            ['PHOTODIR_LBL', 'COLLFOLDERS_LBL']):

            gallery_descr = MyLabel(
                master, text=title, justify=tkinter.LEFT,
                wraplength=vars['text_length'],
                font=('Arial', 22, 'bold'))
            gallery_descr.pack()

            vars[widget] = MyLabel(
                master, text=value, justify=tkinter.LEFT,
                wraplength=vars['text_length'])
            vars[widget].pack(
                padx=(10, 0), pady=(5, 0))

            gallery_btn = MyButton(master, text='Обзор')
            gallery_btn.pack(
                pady=(5, 0), padx=(5, 0))
            gallery_btn.configure(height=1, width=9)

            gallery_btn.cmd(
                lambda e, x=vars[widget]: self.select_path(x))

            sep = MySep(master)
            sep.pack(padx=40, pady=20, fill=tkinter.X)

        txt3 = (
            'Имя папки с ретушью. Подразумевается, что внутри папки с этим '
            'именем будут отретушированные фото.'
            )

        txt4 = (
            'По умолчанию программа ищет отретушированные фотографии за '
            f'последние {cfg.config["FILE_AGE"]} дней. Можно указать другое '
            'количество дней. Чем больше цифра, тем дольше сканирование.'
            )

        for descr, value, widget in zip(
            [txt3, txt4],
            [cfg.config['RT_FOLDER'], cfg.config['FILE_AGE']],
            ['RTFOLDER_ENTRY', 'FILEAGE_ENTRY']):

            lbl = MyLabel(
                master, justify=tkinter.LEFT,
                wraplength=vars['text_length'], text=descr)
            lbl.pack(anchor=tkinter.W, pady=(0, 10))

            vars[widget] = tkinter.Entry(
                master, bg=cfg.BGBUTTON, fg=cfg.BGFONT,
                insertbackground=cfg.BGFONT, selectbackground=cfg.BGPRESSED,
                highlightthickness=5, highlightbackground=cfg.BGBUTTON,
                highlightcolor=cfg.BGBUTTON, bd=0, justify='center', width=35)

            vars[widget].insert(0, value)
            vars[widget].pack(pady=(0, 10))

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
            btn_paste.pack(side=tkinter.RIGHT)

            sep = MySep(master)
            sep.pack(padx=40, pady=20, fill=tkinter.X)

        rest_frame = MyFrame(master)
        rest_frame.pack(pady=(0, 15))

        restore_btn = MyButton(rest_frame, text='По умолчанию')
        restore_btn.configure(height=1, width=12)
        restore_btn.cmd(lambda e, x=restore_btn: self.restore(x))
        restore_btn.pack(side=tkinter.LEFT, padx=(0, 10))

        reset_button = MyButton(rest_frame, text='Полный сброс')
        reset_button.configure(height=1, width=12)
        reset_button.cmd(lambda e: self.full_reset())
        reset_button.pack(side=tkinter.RIGHT)

        below_frame = MyFrame(bottom_frame)
        below_frame.pack(pady=(15, 15))

        save_btn = MyButton(below_frame, text='Сохранить')
        save_btn.cmd(lambda e: self.save_settings(master))
        save_btn.configure(height=1, width=12)
        save_btn.pack(side=tkinter.LEFT, padx=(0, 10))

        cancel_btn = MyButton(below_frame, text='Отмена')
        cancel_btn.cmd(lambda e: self.cancel(master))
        cancel_btn.configure(height=1, width=12)
        cancel_btn.pack(side=tkinter.RIGHT)

    def full_scan(self):
        """
        Reload app and run Utils Scaner with full scan method.
        """
        cfg.config['TYPE_SCAN'] = 'full'
        encrypt_cfg(cfg.config)
        os.execv(sys.executable, ['python'] + sys.argv)

    def full_reset(self):
        shutil.rmtree(cfg.CFG_DIR)
        os.execv(sys.executable, ['python'] + sys.argv)

    def select_path(self, widget):
        path = filedialog.askdirectory()

        if len(path) == 0:
            return

        widget['text'] = path

    def restore(self, btn: MyButton):
        """
        Gets advanced settings values from cfg and write to cfg.json
        Sets default text in all text input fields in advanced settings.
        * param `btn`: current tkinter button
        """
        btn.press()

        for widget, default, value in zip(
            [vars['PHOTODIR_LBL'], vars['COLLFOLDERS_LBL']],
            [cfg.defaults['PHOTO_DIR'], cfg.defaults['COLL_FOLDER']],
            ['PHOTO_DIR', 'COLL_FOLDER']):

            widget['text'] = default
            cfg.config[value] = default

        for widget, default, value in zip(
            [vars['RTFOLDER_ENTRY'], vars['FILEAGE_ENTRY']],
            [cfg.defaults['RT_FOLDER'], cfg.defaults['FILE_AGE']],
            ['RT_FOLDER', 'FILE_AGE']):

            widget.delete(0, 'end')
            widget.insert(0, default)
            cfg.config[value] = default

    def copy_input(self, ins: tkinter.Entry, btn: MyButton):
        """
        Gets text from current text input field and copy to clipboard.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.press()
        my_copy(ins.get())

    def paste_input(self, ins: tkinter.Entry, btn: MyButton):
        """
        Gets text from clipboard and paste in text input field.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.press()
        ins.delete(0, 'end')
        ins.insert(0, my_paste())

    def cancel(self, master: tkinter.Frame):
        """
        Cancel button command.
        """
        master.winfo_toplevel().destroy()

    def save_settings(self, master: tkinter.Frame):
        """
        Get text from all text fields in advanced settings and save to
        cfg.json
        """

        cfg.config['PHOTO_DIR'] = vars['PHOTODIR_LBL']['text']
        cfg.config['COLL_FOLDER'] = vars['COLLFOLDERS_LBL']['text']
        cfg.config['RT_FOLDER'] = vars['RTFOLDER_ENTRY'].get()
        cfg.config['FILE_AGE'] = vars['FILEAGE_ENTRY'].get()

        encrypt_cfg(cfg.config)

        master.winfo_toplevel().destroy()
