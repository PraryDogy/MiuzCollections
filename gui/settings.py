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
        self.title(cnf.lng.settings)
        self.minsize(500, 450)

        self.scan_again = False
        self.old_time = cnf.scan_time
        self.old_lng = cnf.lng

        path_name = CLabel(
            self,
            text=cnf.lng.colls_path,
            anchor="w",
            justify="left"
            )
        path_name.pack(anchor="w")

        self.path_widget = CLabel(
            self,
            text=f"{cnf.coll_folder}",
            anchor="w",
            justify="left",
            wraplength = 400,
            )
        self.path_widget.pack(anchor="w")

        select_path = CButton(self, text=cnf.lng.browse)
        select_path.cmd(self.select_path_cmd)
        select_path.pack(pady=(10, 0))

        sett_desc = CLabel(
            self, text=cnf.lng.sett_descr, anchor="w", justify="left"
            )
        sett_desc.pack(anchor="w", pady=(15, 0))



        CSep(self).pack(pady=15, padx=50, fill=tkinter.X)

        down_title = CLabel(
            self,
            text=cnf.lng.down_path,
            anchor="w",
            justify="left"
            )
        down_title.pack(anchor="w")

        self.down_widget = CLabel(
            self,
            text=f"{cnf.down_folder}",
            anchor="w",
            justify="left",
            wraplength = 400,
            )
        self.down_widget.pack(anchor="w")

        select_down = CButton(self, text=cnf.lng.browse)
        select_down.cmd(self.select_down_cmd)
        select_down.pack(pady=(10, 0))



        CSep(self).pack(pady=15, padx=50, fill=tkinter.X)

        self.scan_btn = CButton(
            self,
            text=f"{cnf.lng.update_every} {cnf.scan_time} {cnf.lng.mins}",
            )
        self.scan_btn.configure(width=28)
        self.scan_btn.cmd(self.scan_time_cmd)
        self.scan_btn.pack()



        CSep(self).pack(pady=15, padx=50, fill=tkinter.X)

        lang_lbl = CLabel(
            self,
            text=cnf.lng.lang_label,
            anchor="w",
            justify="left",
            )
        lang_lbl.pack(anchor="w")

        self.lang_btn = CButton(self, text=cnf.lng.language)
        self.lang_btn.pack(pady=(10, 0))
        self.lang_btn.cmd(self.lang_cmd)

        self.lang_descr = CLabel(
            self, text=cnf.lng.lang_descr, anchor="w", justify="left"
            )
        self.lang_descr.pack(anchor="w", pady=(15, 0))




        cancel_frame = CFrame(self)
        cancel_frame.pack(expand=True)

        CSep(cancel_frame).pack(pady=15, fill=tkinter.X)

        save_btn = CButton(cancel_frame, text=cnf.lng.ok)
        save_btn.cmd(self.save_cmd)
        save_btn.pack(padx=(0, 15), side="left")

        cancel_btn = CButton(cancel_frame, text=cnf.lng.cancel)
        cancel_btn.cmd(self.cancel_cmd)
        cancel_btn.pack(side="left")

        cnf.root.update_idletasks()

        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()


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
            text=f"{cnf.lng.update_every} {cnf.scan_time} {cnf.lng.mins}"
            )

    def lang_cmd(self, e=None):
        from lang import Eng, Rus

        if isinstance(cnf.lng, Rus):
            cnf.lng = Eng()
        else:
            cnf.lng = Rus()

        self.lang_btn.configure(text=cnf.lng.language)
        self.lang_descr.configure(text=cnf.lng.lang_descr)


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
        cnf.scan_time = self.old_time
        cnf.lng = self.old_lng

        self.destroy()
        cnf.root.focus_force()

    def save_cmd(self, e=None):
        cnf.coll_folder = self.path_widget['text']
        cnf.down_folder = self.down_widget["text"]

        cnf.write_cfg()
        self.destroy()
        cnf.root.focus_force()

        if self.scan_again:
            if smb_check():
                scaner.scaner_start()
            else:
                scaner.scaner_sheldue()
                SmbAlert()

        if self.old_lng != cnf.lng:
            Globals.reload_scroll()
            Globals.reload_menu()
            Globals.reload_stbar()
