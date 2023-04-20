import os
import shutil
import sys
import tkinter
from tkinter import filedialog

import tkmacosx

import cfg
from utils import close_windows, my_copy, my_paste, place_center, write_cfg

from .widgets import AskExit, CButton, CFrame, CLabel, CloseBtn, CSep, CWindow

path_widget = tkinter.Label
checkbox_widget = tkinter.Checkbutton
live_widget = tkinter.Label


class Settings(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title('Настройки')
        self.resizable(1, 1)

        self.minimize = tkinter.IntVar(value = cfg.config['MINIMIZE'])

        self.main_wid = self.main_widget()
        self.main_wid.pack()

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.grab_set()

        self.update_live_lbl()

    def main_widget(self):
        global path_widget, checkbox_widget, live_widget

        frame = CFrame(self)

        title_lbl = CLabel(
                frame,
                text = "Коллекции",
                justify = tkinter.LEFT,
                font = ('Arial', 22, 'bold'),
                width = 30,
                )
        title_lbl.pack()

        path_widget = CLabel(
            frame,
            text = cfg.config['COLL_FOLDER'],
            justify = tkinter.LEFT,
            wraplength = 400
            )
        path_widget.pack(padx = 15, pady = (5, 0))

        select_path = CButton(frame, text = 'Обзор')
        select_path.pack(pady = (15, 0), padx = (5, 0))
        select_path.configure(width = 9)
        select_path.cmd(lambda e, x = path_widget: self.select_path(x))

        checkbox_frame = CFrame(frame)
        checkbox_frame.pack(pady = (15, 0))

        checkbox_widget = tkinter.Checkbutton(
            checkbox_frame,
            bg = cfg.BGCOLOR
            )
        checkbox_widget['command'] = lambda: self.checkbox_cmd(checkbox_widget)
        [
            checkbox_widget.select()
            if self.minimize.get() == 1
            else checkbox_widget.deselect()
            ]
        checkbox_widget.pack(side = tkinter.LEFT)

        checkbox_lbl = CLabel(checkbox_frame, text = 'Свернуть вместо закрыть')
        checkbox_lbl.pack(side = tkinter.LEFT)

        rest_frame = CFrame(frame)
        rest_frame.pack(pady = (15, 0))

        restore_btn = CButton(rest_frame, text = 'По умолчанию')
        restore_btn.configure(width = 12)
        restore_btn.cmd(lambda e, x = restore_btn: self.restore(x))
        restore_btn.pack(side = tkinter.LEFT, padx = (0, 10))

        reset_button = CButton(rest_frame, text = 'Очистить кэш')
        reset_button.configure(width = 12)
        reset_button.cmd(lambda e: self.full_reset())
        reset_button.pack(side = tkinter.LEFT)

        live_widget = CLabel(
            frame,
            text = cfg.LIVE_TEXT,
            justify = tkinter.LEFT,
            wraplength = 400,
            )
        live_widget.pack(padx = 15, pady = (15, 0))

        cancel_frame = CFrame(frame)
        cancel_frame.pack()

        CSep(cancel_frame).pack(pady = 15, fill = tkinter.X)

        save_btn = CButton(cancel_frame, text = 'Сохранить')
        save_btn.cmd(lambda e: self.save_settings())
        save_btn.configure(width = 12)
        save_btn.pack(side = tkinter.LEFT, padx = (0, 10))

        cancel_btn = CloseBtn(cancel_frame, text = 'Отмена')
        cancel_btn.configure(width = 12)
        cancel_btn.pack(side = tkinter.LEFT)

        return frame

    def update_live_lbl(self):
        global live_widget
        live_widget["text"] = cfg.LIVE_TEXT

        if self.winfo_exists():
            cfg.ROOT.after(1000, self.update_live_lbl)

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

    def restore(self, btn: CButton):
        """
        Gets advanced settings values from cfg and write to cfg.json
        Sets default text in all text input fields in advanced settings.
        * param `btn`: current tkinter button
        """
        btn.press()
        path_widget['text'] = cfg.default_vars['COLL_FOLDER']
        checkbox_widget.select()

    def save_settings(self):
        """
        Get text from all text fields in advanced settings and save to
        cfg.json
        """
        cfg.config['COLL_FOLDER'] = path_widget['text']
        cfg.config['MINIMIZE'] = self.minimize.get()

        write_cfg(cfg.config)

        if cfg.config['MINIMIZE'] == 1:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", lambda: cfg.ROOT.iconify())

        else:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", AskExit)

        close_windows()
