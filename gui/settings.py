import tkinter
from tkinter import filedialog

from cfg import cnf
from .scaner import scaner
from .utils import *

from .globals import Globals
from .widgets import *

__all__ = (
    "Settings",
    )


class Settings(CWindow):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.cancel_cmd)
        self.bind('<Escape>', self.cancel_cmd)
        self.bind("<Return>", self.save_cmd)
        self.title(cnf.lang.settings)
        self.minsize(400, 300)

        self.changed_lang = False
        self.scan_again = False
        self.old_curr_coll = cnf.curr_coll
        self.old_time = cnf.scan_time

        self.main_wid = self.main_widget()
        self.main_wid.pack(expand=True, fill="both")

        cnf.root.update_idletasks()

        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def main_widget(self):
        frame = CFrame(self)



        path_name = CLabel(
            frame,
            text=cnf.lang.colls_path,
            anchor="w",
            justify="left"
            )
        path_name.pack(anchor="w")
        cnf.lang_sett.append(path_name)

        self.path_widget = CLabel(
            frame,
            text=f"{cnf.coll_folder}",
            anchor="w",
            justify="left",
            wraplength = 350,
            )
        self.path_widget.pack(anchor="w")

        select_path = CButton(frame, text=cnf.lang.browse)
        select_path.cmd(self.select_path_cmd)
        select_path.pack(pady=(10, 0))
        cnf.lang_sett.append(select_path)

        self.sett_desc = CLabel(
            frame, text=cnf.lang.sett_descr, anchor="w", justify="left"
            )
        self.sett_desc.pack(anchor="w", pady=(15, 0))
        cnf.lang_sett.append(self.sett_desc)



        CSep(frame).pack(pady=15, padx=50, fill=tkinter.X)

        down_title = CLabel(
            frame,
            text=cnf.lang.down_path,
            anchor="w",
            justify="left"
            )
        down_title.pack(anchor="w")
        cnf.lang_sett.append(down_title)

        self.down_widget = CLabel(
            frame,
            text=f"{cnf.down_folder}",
            anchor="w",
            justify="left",
            wraplength = 350,
            )
        self.down_widget.pack(anchor="w")

        select_down = CButton(frame, text=cnf.lang.browse)
        select_down.cmd(self.select_down_cmd)
        select_down.pack(pady=(10, 0))
        cnf.lang_sett.append(select_down)



        CSep(frame).pack(pady=15, padx=50, fill=tkinter.X)

        self.scan_btn = CButton(
            frame,
            text=f"{cnf.lang.update_every} {cnf.scan_time} {cnf.lang.mins}",
            )
        self.scan_btn.configure(width=28)
        self.scan_btn.cmd(self.scan_time_cmd)
        cnf.lang_sett.append(self.scan_btn)
        self.scan_btn.pack()



        CSep(frame).pack(pady=15, padx=50, fill=tkinter.X)

        lang_lbl = CLabel(
            frame,
            text=cnf.lang.lang_label,
            anchor="w",
            justify="left",
            wraplength = 350,
            )
        lang_lbl.pack(anchor="w")
        cnf.lang_sett.append(lang_lbl)

        self.lang_btn = CButton(frame, text=cnf.lang.language)
        self.lang_btn.pack(pady=(10, 0))
        self.lang_btn.cmd(self.lang_cmd)

        cancel_frame = CFrame(frame)
        cancel_frame.pack(expand=True)



        CSep(cancel_frame).pack(pady=15, fill=tkinter.X)

        save_btn = CButton(cancel_frame, text=cnf.lang.ok)
        save_btn.cmd(self.save_cmd)
        save_btn.pack(padx=(0, 15), side="left")
        cnf.lang_sett.append(save_btn)

        cancel_btn = CButton(cancel_frame, text=cnf.lang.cancel)
        cancel_btn.cmd(self.cancel_cmd)
        cancel_btn.pack(side="left")
        cnf.lang_sett.append(cancel_btn)

        return frame

    def scan_time_cmd(self, e=None):
        times = [5, 10, 30, 60]
        try:
            ind = times.index(cnf.scan_time)
        except ValueError:
            ind = -1

        try:
            cnf.scan_time = times[ind+1]
        except IndexError:
            cnf.scan_time = times[0]

        self.scan_btn.configure(
            text=f"{cnf.lang.update_every} {cnf.scan_time} {cnf.lang.mins}"
            )

    def change_lang(self):
        self.scan_btn.configure(
            text=f"{cnf.lang.update_every} {cnf.scan_time} {cnf.lang.mins}"
            )

        wids = cnf.lang_menu + cnf.lang_sett
        wids = wids + cnf.lang_stbar + cnf.lang_thumbs

        for wid in (wids):
            for k, v in self.old_lang.__dict__.items():
                try:
                    if wid["text"] == v:
                        wid["text"] = cnf.lang.__dict__[k]
                except tkinter.TclError:
                    print("change lang widget err", wid.widgetName)
                    print(wid.__dict__)

    def lang_cmd(self, e=None):
        from lang import Eng, Rus

        self.changed_lang = True

        if self.lang_btn["text"] == "English":
            self.lang_btn["text"] = "Русский"
            self.title("Настройки")

            self.old_lang = cnf.lang
            cnf.lang = Rus()

            self.change_lang()

        else:
            self.lang_btn["text"] = "English"
            self.title("Settings")

            self.old_lang = cnf.lang
            cnf.lang = Eng()

            self.change_lang()

    def select_path_cmd(self, e=None):
        path = filedialog.askdirectory(initialdir=cnf.coll_folder)

        if len(path) == 0:
            return

        if self.path_widget["text"] != path:
            self.path_widget['text'] = path
            self.scan_again = True

    def select_down_cmd(self, e=None):
        path = filedialog.askdirectory(initialdir=cnf.down_folder)

        if len(path) == 0:
            return

        if self.down_widget["text"] != path:
            self.down_widget['text'] = path

    def cancel_cmd(self, e=None):
        if self.changed_lang:
            self.lang_cmd()

        cnf.lang_sett.clear()
        cnf.scan_time = self.old_time

        self.destroy()
        cnf.root.focus_force()

    def save_cmd(self, e=None):
        cnf.lang_sett.clear()
        cnf.coll_folder = self.path_widget['text']
        cnf.down_folder = self.down_widget["text"]

        if self.lang_btn["text"] == "English":
            cnf.json_lang = "English"
        else:
            cnf.json_lang = "Russian"

        cnf.write_cfg()
        self.destroy()
        cnf.root.focus_force()

        if self.scan_again:
            cnf.curr_coll = cnf.all_colls
            self.scan_again = False
            if smb_check():
                scaner.scaner_start()
            else:
                scaner.scaner_sheldue()
                SmbAlert()

        if self.changed_lang:
            Globals.reload_scroll()
