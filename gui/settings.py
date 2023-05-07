from database import *

from . import (cfg, filedialog, on_exit, place_center, scaner, smb_check,
               sqlalchemy, tkinter, write_cfg, os, subprocess)
from .widgets import *

path_widget = tkinter.Label
checkbox_wid = tkinter.Checkbutton
SCAN_AGAIN = False

__all__ = (
    "Settings",
    )


class Settings(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title('Настройки')

        self.geometry("400x250")
        self.minsize(400, 250)
        self.maxsize(800, 300)
        self.resizable(1, 1)

        self.ask_exit = tkinter.IntVar(value = cfg.config['ASK_EXIT'])

        self.main_wid = self.main_widget()
        self.main_wid.pack(expand=True, fill="both")

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def main_widget(self):
        global path_widget, checkbox_wid

        frame = CFrame(self)

        title_lbl = CLabel(frame, text="Коллекции")
        title_lbl.configure(font=('San Francisco Pro', 22, 'bold'))
        title_lbl.pack(expand=True, fill="both")

        path_widget = CLabel(
            frame,
            text=cfg.config['COLL_FOLDER'],
            anchor="w",
            justify="left"
            )
        path_widget.pack(pady=(5, 0), expand=True, fill="both")

        select_path = CButton(frame, text='Обзор')
        select_path.cmd(lambda e: self.select_path_cmd())
        select_path.pack(pady=(5, 0), padx=(5, 0))

        restore_frame = CFrame(frame)
        restore_frame.pack(pady=(15, 0))

        restore_btn = CButton(restore_frame, text='Сброс')
        restore_btn.cmd(lambda e, x=restore_btn: self.default_cmd(x))
        restore_btn.pack(padx=(0, 10), side="left")

        open_cfg = CButton(restore_frame, text="Файл настроек")
        open_cfg.cmd(lambda e: self.open_cfg_cmd())
        open_cfg.pack(side="right")

        checkbox_frame = CFrame(frame)
        checkbox_frame.pack(pady=(15, 0))

        checkbox_wid = tkinter.Checkbutton(checkbox_frame, bg=cfg.BG)
        checkbox_wid['command'] = lambda: self.checkbox_cmd(checkbox_wid)

        if self.ask_exit.get() == 1:
            checkbox_wid.select()
        else:
            checkbox_wid.deselect()

        checkbox_wid.pack(side="left")

        checkbox_lbl = CLabel(checkbox_frame, text='Спрашивать при выходе')
        checkbox_lbl.pack(side="left")

        checkbox_lbl.bind("<Button-1>", lambda e: self.checkbox_cmd(checkbox_wid))

        cancel_frame = CFrame(frame)
        cancel_frame.pack(expand=True)

        CSep(cancel_frame).pack(pady=15, fill=tkinter.X)

        save_btn = CButton(cancel_frame, text='Сохранить')
        save_btn.cmd(lambda e: self.save_cmd())
        save_btn.pack(padx=(0, 10), side="left")

        cancel_btn = CButton(cancel_frame, text='Отмена')
        cancel_btn.cmd(lambda e: self.destroy())
        cancel_btn.pack(side="left")

        return frame
    
    def open_cfg_cmd(self):
        subprocess.check_output(
            ["/usr/bin/open", os.path.join(cfg.CFG_DIR, 'cfg.json')]
            )
        self.destroy()
        cfg.ROOT.focus_force()

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
        checkbox_wid.select()

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
        self.destroy()
        cfg.ROOT.focus_force()

        if SCAN_AGAIN:
            SCAN_AGAIN = False
            cfg.FLAG = False

            try:
                while cfg.SCANER_TASK.is_alive():
                    cfg.ROOT.update()
            except AttributeError:
                print("no task scaner")
            if smb_check():
                scaner()
            else:
                SmbAlert()