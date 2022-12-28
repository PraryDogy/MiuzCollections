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

        self.geometry(
            f'{int(cfg.ROOT.winfo_width()*0.5)}x'
            f'{int(cfg.ROOT.winfo_height()*0.8)}')

        cfg.ROOT.update_idletasks()

        self.ln = int(self.winfo_width()*0.9)
        self.minimize = tkinter.IntVar(value=cfg.config['MINIMIZE'])

        scrolllable = tkmacosx.SFrame(
            self, bg=cfg.BGCOLOR, scrollbarwidth=7)
        scrolllable.pack(fill=tkinter.BOTH, expand=1)

        self.scan_widget(scrolllable).pack()

        self.dirs_wid = self.dirs_widget(scrolllable)
        self.dirs_wid.pack()

        self.entries_wid = self.entries_widget(scrolllable)
        self.entries_wid.pack()

        self.options_wid = self.options_widget(scrolllable)
        self.options_wid.pack()

        bottom_frame = CFrame(self)
        bottom_frame.pack(padx=(0, 7))

        self.cancel_widget(bottom_frame).pack()

        place_center(self)
        self.deiconify()
        self.grab_set()

    def scan_widget(self, master: tkinter):
        frame = CFrame(master)

        title = CLabel(frame, text='Настройки', font=('Arial', 22, 'bold'))
        title.pack(pady=10)

        txt2 = (
            'При запуске программа сканирует и обновляет фото всех коллекций '
            f'за последние {cfg.config["FILE_AGE"]} дней. '
            'Нажмите "Полное сканирование", чтобы обновить фотографии всех '
            'коллекций за все время c 2018 года.'
            )
        descr_scan = CLabel(frame)
        descr_scan.configure(
            text=txt2, justify=tkinter.LEFT,
            wraplength=self.ln)
        descr_scan.pack(pady=(0, 5), anchor=tkinter.W)

        scan_btn = CButton(frame, text='Полное сканирование')
        scan_btn.configure(width=17)
        scan_btn.cmd(lambda e: self.full_scan())
        scan_btn.pack()

        sep = CSep(frame)
        sep.pack(padx=40, pady=(40, 20), fill=tkinter.X)

        return frame

    def dirs_widget(self, master: tkinter):
        frame = CFrame(master)

        for title, value in zip(
            ('Все фото', 'Коллекции'),
            (cfg.config['PHOTO_DIR'], cfg.config['COLL_FOLDER'])
            ):

            title_lbl = CLabel(
                frame, text=title, justify=tkinter.LEFT,
                wraplength=self.ln,
                font=('Arial', 22, 'bold'))
            title_lbl.pack()

            path_lbl = CLabel(
                frame, text=value, justify=tkinter.LEFT, wraplength=self.ln)
            path_lbl.pack(padx=(10, 0), pady=(5, 0))

            select_path = CButton(frame, text='Обзор')
            select_path.pack(
                pady=(5, 0), padx=(5, 0))
            select_path.configure(width=9)
            select_path.cmd(
                lambda e, x=path_lbl: self.select_path(x))

            CSep(frame).pack(padx=40, pady=20, fill=tkinter.X)
        
        return frame

    def entries_widget(self, master: tkinter):
        frame = CFrame(master)
        
        t1 = (
            'Программа ищет отретушированные фото в папках с данным именем.'
            )

        t2 = (
            'По умолчанию программа ищет отретушированные фотографии за '
            f'последние {cfg.config["FILE_AGE"]} дней. Можно указать другое '
            'количество дней. Чем больше число, тем дольше сканирование.'
            )

        for descr, value in zip(
            (t1, t2),
            (cfg.config['RT_FOLDER'], cfg.config['FILE_AGE'])
            ):

            description_lbl = CLabel(
                frame, justify=tkinter.LEFT,
                wraplength=self.ln, text=descr)
            description_lbl.pack(anchor=tkinter.W, pady=(0, 10))

            entry = tkinter.Entry(
                frame, bg=cfg.BGBUTTON, fg=cfg.BGFONT,
                insertbackground=cfg.BGFONT, selectbackground=cfg.BGPRESSED,
                highlightthickness=5, highlightbackground=cfg.BGBUTTON,
                highlightcolor=cfg.BGBUTTON, bd=0, justify='center', width=35)

            entry.insert(0, value)
            entry.pack(pady=(0, 10))

            frame_btns = CFrame(frame)
            frame_btns.pack()

            btn_c = CButton(frame_btns, text='Копировать')
            btn_c.cmd(partial(self.copy_input, entry, btn_c))

            btn_v = CButton(frame_btns, text='Вставить')
            btn_v.cmd(partial(self.paste_input, entry, btn_v))

            [i.configure(width=9) for i in (btn_c, btn_v)]
            [i.pack(side=tkinter.LEFT, padx=(5)) for i in (btn_c, btn_v)]

            sep = CSep(frame)
            sep.pack(padx=40, pady=20, fill=tkinter.X)

        return frame

    def options_widget(self, master: tkinter):
        frame = CFrame(master)

        min_frame = CFrame(frame)
        min_frame.pack(pady = (0, 15))

        check_box = tkinter.Checkbutton(min_frame, bg=cfg.BGCOLOR)
        check_box['command'] = lambda: self.checkbox_cmd(check_box)
        [check_box.select() if self.minimize.get() == 1 else check_box.deselect()]

        check_lbl = CLabel(min_frame, text='Свернуть вместо закрыть')

        [i.pack(side=tkinter.LEFT) for i in (check_box, check_lbl)]

        rest_frame = CFrame(frame)
        rest_frame.pack(pady=(0, 15))

        restore_btn = CButton(rest_frame, text='По умолчанию')
        restore_btn.configure(width=12)
        restore_btn.cmd(lambda e, x=restore_btn: self.restore(x))
        restore_btn.pack(side=tkinter.LEFT, padx=(0, 10))

        reset_button = CButton(rest_frame, text='Полный сброс')
        reset_button.configure(width=12)
        reset_button.cmd(lambda e: self.full_reset())
        reset_button.pack(side=tkinter.RIGHT)

        return frame

    def cancel_widget(self, master: tkinter):
        frame = CFrame(master)

        save_btn = CButton(frame, text='Сохранить')
        save_btn.cmd(lambda e: self.save_settings())
        save_btn.configure(width=12)
        save_btn.pack(side=tkinter.LEFT, padx=(0, 10))

        cancel_btn = CloseBtn(frame, text='Отмена')
        cancel_btn.pack(side=tkinter.RIGHT)

        return frame

    def checkbox_cmd(self, master: tkinter.Checkbutton):
        if self.minimize.get() == 1:
            self.minimize.set(0)
            master.deselect()
        elif self.minimize.get() == 0:
            self.minimize.set(1)
            master.select()

    def full_scan(self):
        """
        Reload app and run Utils Scaner with full scan method.
        """
        cfg.config['TYPE_SCAN'] = 'full'
        write_cfg(cfg.config)
        os.execv(sys.executable, ['python'] + sys.argv)

    def full_reset(self):
        shutil.rmtree(cfg.CFG_DIR)
        os.execv(sys.executable, ['python'] + sys.argv)

    def select_path(self, master: tkinter.Label):
        path = filedialog.askdirectory()

        if len(path) == 0:
            return

        master['text'] = path

    def get_widgets(self):
        paths = self.dirs_wid.winfo_children()
        path1, path2 = paths[1], paths[5]

        entries = self.entries_wid.winfo_children()
        entry1, entry2 = entries[1], entries[5]

        options = self.options_wid.winfo_children()[0]
        checkbox = options.winfo_children()[0]

        return (path1, path2, entry1, entry2, checkbox)

    def restore(self, btn: CButton):
        """
        Gets advanced settings values from cfg and write to cfg.json
        Sets default text in all text input fields in advanced settings.
        * param `btn`: current tkinter button
        """
        btn.press()

        path1, path2, entry1, entry2, checkbox = self.get_widgets()
        defaults = cfg.defaults()
        entry1: tkinter.Entry
        entry2: tkinter.Entry
        checkbox: tkinter.Checkbutton

        path1['text'] = defaults['PHOTO_DIR']
        path2['text'] = defaults['COLL_FOLDER']

        [i.delete(0, 'end') for i in (entry1, entry2)]
        entry1.insert(0, defaults['RT_FOLDER'])
        entry2.insert(0, defaults['FILE_AGE'])

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
        path1, path2, entry1, entry2, checkbox = self.get_widgets()
        entry1: tkinter.Entry
        entry2: tkinter.Entry

        cfg.config['PHOTO_DIR'] = path1['text']
        cfg.config['COLL_FOLDER'] = path2['text']
        cfg.config['RT_FOLDER'] = entry1.get()
        
        file_age = entry2.get()
        if type(file_age) == int and file_age < 1000:
            cfg.config['FILE_AGE'] = entry2.get()

        cfg.config['MINIMIZE'] = self.minimize.get()

        write_cfg(cfg.config)

        if cfg.config['MINIMIZE'] == 1:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", lambda: cfg.ROOT.withdraw())
        else:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", AskExit)

        close_windows()
