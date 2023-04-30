from database import *

from . import (cfg, close_windows, filedialog, place_center, scaner,
               sqlalchemy, tkinter, write_cfg, on_exit)
from .widgets import *

path_widget = tkinter.Label
checkbox_widget = tkinter.Checkbutton
SCAN_AGAIN = False

__all__ = (
    "Settings"
    )


class Settings(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title('Настройки')
        self.resizable(1, 1)

        self.ask_exit = tkinter.IntVar(value = cfg.config['ASK_EXIT'])

        self.main_wid = self.main_widget()
        self.main_wid.pack()

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.grab_set()

    def main_widget(self):
        global path_widget, checkbox_widget

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
        select_path.cmd(lambda e: self.select_path_cmd())

        checkbox_frame = CFrame(frame)
        checkbox_frame.pack(pady = (15, 0))

        checkbox_widget = tkinter.Checkbutton(
            checkbox_frame,
            bg = cfg.BG
            )
        checkbox_widget['command'] = lambda: self.checkbox_cmd(checkbox_widget)
        [
            checkbox_widget.select()
            if self.ask_exit.get() == 1
            else checkbox_widget.deselect()
            ]
        checkbox_widget.pack(side = tkinter.LEFT)

        checkbox_lbl = CLabel(checkbox_frame, text = 'Спрашивать при выходе')
        checkbox_lbl.pack(side = tkinter.LEFT)

        restore_btn = CButton(frame, text = 'Сброс')
        restore_btn.configure(width = 12)
        restore_btn.cmd(lambda e, x = restore_btn: self.default_cmd(x))
        restore_btn.pack(pady = (15, 0))

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

    def checkbox_cmd(self, master: tkinter.Checkbutton):
        if self.ask_exit.get() == 1:
            self.ask_exit.set(0)
            master.deselect()
        elif self.ask_exit.get() == 0:
            self.ask_exit.set(1)
            master.select()

    def select_path_cmd(self):
        global path_widget, SCAN_AGAIN
        path = filedialog.askdirectory(initialdir = cfg.config["COLL_FOLDER"])

        if len(path) == 0:
            return

        if path_widget["text"] != path:
            path_widget['text'] = path
            SCAN_AGAIN = True

    def default_cmd(self, btn: CButton):
        global SCAN_AGAIN

        btn.press()
        path_widget['text'] = cfg.default_vars['COLL_FOLDER']
        checkbox_widget.select()

        Dbase.conn.execute(sqlalchemy.delete(Thumbs))
        Dbase.conn.execute("VACUUM")

        SCAN_AGAIN = True

    def save_cmd(self):
        global SCAN_AGAIN, SCANER_PERMISSION

        cfg.config['COLL_FOLDER'] = path_widget['text']
        cfg.config['ASK_EXIT'] = self.ask_exit.get()

        if cfg.config["ASK_EXIT"] == 1:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", AskExit)
            cfg.ROOT.createcommand("tk::mac::Quit" , AskExit)
        else:
            cfg.ROOT.createcommand("tk::mac::Quit" , on_exit)
            cfg.ROOT.protocol("WM_DELETE_WINDOW", on_exit)

        write_cfg(cfg.config)
        close_windows()




        if SCAN_AGAIN:
            SCAN_AGAIN = False
            cfg.FLAG = False

            try:
                while cfg.SCANER_TASK.is_alive():
                    cfg.ROOT.update()
            except AttributeError:
                print("no task scaner")

            scaner()