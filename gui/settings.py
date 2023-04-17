import os
import shutil
import sys
import tkinter
from functools import partial
from tkinter import filedialog

import tkmacosx

import cfg
from utils import write_cfg, my_copy, my_paste, place_center, close_windows

from .widgets import AskExit, CButton, CFrame, CLabel, CloseBtn, CSep, CWindow


class Settings(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title('Настройки')
        self.resizable(1, 1)

        self.minimize = tkinter.IntVar(value=cfg.config['MINIMIZE'])

        self.main_wid = self.main_widget(self)
        self.main_wid.pack()

        cfg.ROOT.update_idletasks()

        self.geometry(
            f'{cfg.ROOT.winfo_width()//2}x'
            f'{self.winfo_height()}')

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.grab_set()

    def main_widget(self, master: tkinter):
        frame = CFrame(master)
        title_lbl = CLabel(
                frame,
                text = "Коллекции",
                justify = tkinter.LEFT,
                font = ('Arial', 22, 'bold'),
                )
        title_lbl.pack()

        path_lbl = CLabel(
            frame,
            text = cfg.config['COLL_FOLDER'],
            justify = tkinter.LEFT,
            wraplength = 400
            )
        path_lbl.pack(padx=(10, 0), pady=(5, 0))

        select_path = CButton(frame, text='Обзор')
        select_path.pack(pady=(15, 0), padx=(5, 0))
        select_path.configure(width=9)
        select_path.cmd(lambda e, x=path_lbl: self.select_path(x))

        CSep(frame).pack(padx=40, pady=20, fill=tkinter.X)


        checkbox_frame = CFrame(frame)
        checkbox_frame.pack(pady = (0, 15))

        check_box = tkinter.Checkbutton(checkbox_frame, bg=cfg.BGCOLOR)
        check_box['command'] = lambda: self.checkbox_cmd(check_box)
        [check_box.select() if self.minimize.get() == 1 else check_box.deselect()]

        check_lbl = CLabel(checkbox_frame, text='Свернуть вместо закрыть')

        [i.pack(side=tkinter.LEFT) for i in (check_box, check_lbl)]

        rest_frame = CFrame(frame)
        rest_frame.pack()

        restore_btn = CButton(rest_frame, text='По умолчанию')
        restore_btn.configure(width=12)
        restore_btn.cmd(lambda e, x=restore_btn: self.restore(x))
        restore_btn.pack(side=tkinter.LEFT, padx=(0, 10))

        reset_button = CButton(rest_frame, text='Очистить кэш')
        reset_button.configure(width=12)
        reset_button.cmd(lambda e: self.full_reset())
        reset_button.pack(side=tkinter.LEFT)

        CSep(frame).pack(padx=40, pady=20, fill=tkinter.X)

        cancel_frame = CFrame(frame)
        cancel_frame.pack()

        save_btn = CButton(cancel_frame, text='Сохранить')
        save_btn.cmd(lambda e: self.save_settings())
        save_btn.configure(width=12)
        save_btn.pack(side=tkinter.LEFT, padx=(0, 10))

        cancel_btn = CloseBtn(cancel_frame, text='Отмена')
        cancel_btn.configure(width=12)
        cancel_btn.pack(side=tkinter.LEFT)

        return frame

    def checkbox_cmd(self, master: tkinter.Checkbutton):
        if self.minimize.get() == 1:
            self.minimize.set(0)
            master.deselect()
        elif self.minimize.get() == 0:
            self.minimize.set(1)
            master.select()

    def full_reset(self):
        shutil.rmtree(cfg.CFG_DIR)
        os.execv(sys.executable, ['python'] + sys.argv)

    def select_path(self, master: tkinter.Label):
        path = filedialog.askdirectory()

        if len(path) == 0:
            return

        master['text'] = path

    def get_widgets(self):
        children = self.main_wid.winfo_children()

        checkbox = children[4].winfo_children()[0]

        return (children[1], checkbox)

    def restore(self, btn: CButton):
        """
        Gets advanced settings values from cfg and write to cfg.json
        Sets default text in all text input fields in advanced settings.
        * param `btn`: current tkinter button
        """
        btn.press()

        path2, checkbox = self.get_widgets()
        checkbox: tkinter.Checkbutton

        path2['text'] = cfg.default_vars['COLL_FOLDER']

        checkbox.select()

    def copy_input(self, master: tkinter.Entry, btn: CButton):
        """
        Gets text from current text input field and copy to clipboard.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.press()
        my_copy(master.get())

    def paste_input(self, master: tkinter.Entry, btn: CButton, e):
        """
        Gets text from clipboard and paste in text input field.
        * param `ins`: tkinter entry current text input
        * param `btn`: current button
        """
        btn.press()
        master.delete(0, 'end')
        master.insert(0, my_paste())

    def save_settings(self):
        """
        Get text from all text fields in advanced settings and save to
        cfg.json
        """
        coll_path, checkbox = self.get_widgets()

        cfg.config['COLL_FOLDER'] = coll_path['text']
        cfg.config['MINIMIZE'] = self.minimize.get()

        write_cfg(cfg.config)

        if cfg.config['MINIMIZE'] == 1:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", lambda: cfg.ROOT.iconify())

        else:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", AskExit)

        close_windows()
