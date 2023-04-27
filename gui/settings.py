from . import (cfg, close_windows, filedialog, os, place_center, shutil, sys,
               tkinter, write_cfg)
from .widgets import AskExit, CButton, CFrame, CLabel, CloseBtn, CSep, CWindow

path_widget = tkinter.Label
checkbox_widget = tkinter.Checkbutton
live_widget = tkinter.Label
save_btn = tkinter.Label

__all__ = (
    "Settings"
    )


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
        global path_widget, checkbox_widget, live_widget, save_btn

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
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            wraplength = 370,
            width = 30,
            )
        path_widget.pack(padx = 15, pady = (5, 0), fill=tkinter.X)

        select_path = CButton(frame, text = 'Обзор')
        select_path.pack(pady = (15, 0), padx = (5, 0))
        select_path.configure(width = 9)
        select_path.cmd(lambda e, x = path_widget: self.select_path_cmd(x))

        checkbox_frame = CFrame(frame)
        checkbox_frame.pack(pady = (15, 0))

        checkbox_widget = tkinter.Checkbutton(
            checkbox_frame,
            bg = cfg.BG
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
        restore_btn.cmd(lambda e, x = restore_btn: self.default_cmd(x))
        restore_btn.pack()

        live_widget = CLabel(
            frame,
            text = cfg.LIVE_TEXT,
            anchor = tkinter.W,
            justify = tkinter.LEFT,
            width = 30,
            )
        live_widget.pack(padx = 15, pady = (15, 0), fill=tkinter.X)

        cancel_frame = CFrame(frame)
        cancel_frame.pack()

        CSep(cancel_frame).pack(pady = 15, fill = tkinter.X)

        save_btn = CButton(cancel_frame, text = 'Сохранить')
        save_btn.cmd(lambda e: self.save_cmd())
        save_btn.configure(width = 12)
        save_btn.pack(side = tkinter.LEFT, padx = (0, 10))

        cancel_btn = CloseBtn(cancel_frame, text = 'Отмена')
        cancel_btn.configure(width = 12)
        cancel_btn.pack(side = tkinter.LEFT)

        return frame

    def update_live_lbl(self):
        global live_widget

        try:
            live_widget["text"] = (
                cfg.LIVE_TEXT.replace(cfg.config["COLL_FOLDER"], "")
                )
        except Exception:
            print("no live label settings")

        if self.winfo_exists():
            cfg.ROOT.after(100, self.update_live_lbl)

    def checkbox_cmd(self, master: tkinter.Checkbutton):
        if self.minimize.get() == 1:
            self.minimize.set(0)
            master.deselect()
        elif self.minimize.get() == 0:
            self.minimize.set(1)
            master.select()

    def select_path_cmd(self, master: tkinter.Label):
        path = filedialog.askdirectory()

        if len(path) == 0:
            return

        if master["text"] != path:
            master['text'] = path
            save_btn["text"] = "Перезапуск"
            save_btn.cmd(lambda e: self.save_reload())

    def save_reload(self):
        self.save_cmd()
        os.execv(sys.executable, ['python'] + sys.argv)

    def default_cmd(self, btn: CButton):
        """
        Gets advanced settings values from cfg and write to cfg.json
        Sets default text in all text input fields in advanced settings.
        * param `btn`: current tkinter button
        """
        btn.press()
        path_widget['text'] = cfg.default_vars['COLL_FOLDER']
        checkbox_widget.select()

    def save_cmd(self):
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
