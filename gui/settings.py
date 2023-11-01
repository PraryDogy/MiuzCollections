import tkinter
from tkinter import filedialog

from cfg import cnf
from .scaner import scaner
from .utils import *

from .widgets import *

__all__ = (
    "Settings",
    )


class Settings(CWindow):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.close_sett)
        self.bind("<Escape>", self.close_sett)
        self.bind("<Return>", self.save_sett)
        self.title(cnf.lng.settings)
        self.minsize(450, 500)
        place_center(cnf.root, self, 450, 500)

        self.scan_again = False
        self.old_time = cnf.scan_time
        self.old_lng = cnf.lng

        path_name = CLabel(
            self, text=cnf.lng.colls_path, anchor="w", justify="left"
            )
        path_name.pack(anchor="w")

        self.path_widget = CLabel(
            self, text=f"{cnf.coll_folder}", anchor="w", justify="left",
            wraplength = 400,
            )
        self.path_widget.pack(anchor="w")

        select_path = CButton(self, text=cnf.lng.browse, pady=5)
        select_path.cmd(self.select_path_cmd)
        select_path.pack(pady=(10, 0))

        sett_desc = CLabel(
            self, text=cnf.lng.sett_descr, anchor="w", justify="left"
            )
        sett_desc.pack(anchor="w", pady=(15, 0))



        CSep(self).pack(pady=15, padx=50, fill="x")

        down_title = CLabel(
            self, text=cnf.lng.down_path, anchor="w", justify="left"
            )
        down_title.pack(anchor="w")

        self.down_widget = CLabel(
            self, text=f"{cnf.down_folder}", anchor="w", justify="left",
            wraplength = 400,
            )
        self.down_widget.pack(anchor="w")

        select_down = CButton(self, text=cnf.lng.browse, pady=5)
        select_down.cmd(self.select_down_cmd)
        select_down.pack(pady=(10, 0))



        CSep(self).pack(pady=15, padx=50, fill="x")

        self.scan_btn = CButton(
            self, width=28, pady=5,
            text=f"{cnf.lng.update_every} {cnf.scan_time} {cnf.lng.mins}",
            )
        self.scan_btn.cmd(self.scan_time_cmd)
        self.scan_btn.pack()



        CSep(self).pack(pady=15, padx=50, fill="x")

        lang_lbl = CLabel(
            self,
            text=cnf.lng.lang_label,
            anchor="w",
            justify="left",
            )
        lang_lbl.pack(anchor="w")

        self.lang_btn = CButton(self, text=cnf.lng.language, pady=5)
        self.lang_btn.pack(pady=(10, 0))
        self.lang_btn.cmd(self.lang_cmd)

        self.lang_descr = CLabel(
            self, text=cnf.lng.lang_descr, anchor="w", justify="left"
            )
        self.lang_descr.pack(anchor="w", pady=(15, 0))




        cancel_frame = CFrame(self)
        cancel_frame.pack(expand=1)

        CSep(cancel_frame).pack(pady=15, fill="x")

        save_btn = CButton(cancel_frame, text=cnf.lng.ok, pady=5)
        save_btn.cmd(self.save_sett)
        save_btn.pack(padx=(0, 15), side="left")

        cancel_btn = CButton(cancel_frame, text=cnf.lng.cancel, pady=5)
        cancel_btn.cmd(self.close_sett)
        cancel_btn.pack(side="left")

        self.update_idletasks()
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
        path = filedialog.askdirectory(initialdir=cnf.coll_folder, parent=self)
        self.focus_force()

        if len(path) == 0:
            return

        if self.path_widget.cget("text") != path:
            self.path_widget.configure(text=path)
            self.scan_again = True

    def select_down_cmd(self, e=None):
        path = filedialog.askdirectory(initialdir=cnf.down_folder, parent=self)
        self.focus_force()

        if len(path) == 0:
            return

        if self.down_widget.cget("text") != path:
            self.down_widget.configure(text=path)

    def close_sett(self, e=None):
        cnf.scan_time = self.old_time
        cnf.lng = self.old_lng
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()

    def save_sett(self, e=None):
        cnf.coll_folder = self.path_widget.cget("text")
        cnf.down_folder = self.down_widget.cget("text")

        self.grab_release()
        self.destroy()
        cnf.root.focus_force()
        cnf.write_cfg()

        if self.scan_again:
            if smb_check():
                scaner.scaner_start()
            else:
                scaner.scaner_sheldue()
                SmbAlert()

        if self.old_lng != cnf.lng:
            cnf.reload_scroll()
            cnf.reload_menu()
            cnf.reload_strbar()