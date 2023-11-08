import tkinter
from tkinter import filedialog

from cfg import cnf
from .scaner import scaner
from .utils import *

from .widgets import *

__all__ = (
    "Settings",
    )


class BrowsePathFrame(CFrame):
    def __init__(self, master, path_label, path, descr, **kw):
        super().__init__(master, **kw)

        path_title = CLabel(
            self, text=path_label, anchor="w", justify="left"
            )
        path_title.pack(anchor="w")

        self.path_widget = CLabel(
            self, text=f"{path}", anchor="w", justify="left",
            wraplength = 400,
            )
        self.path_widget.pack(anchor="w")

        select_path = CButton(self, text=cnf.lng.browse)
        select_path.cmd(lambda e: self.select_path_cmd(path))
        select_path.pack(pady=(10, 0))

        sett_desc = CLabel(
            self, text=descr, anchor="w", justify="left"
            )
        if descr:
            sett_desc.pack(anchor="w", pady=(15, 0))

    def select_path_cmd(self, path, e=None):
        dialog = filedialog.askdirectory(initialdir=path, parent=self)
        self.focus_force()

        if len(path) == 0:
            return

        if self.path_widget.cget("text") != dialog:
            self.path_widget.configure(text=dialog)

    def get_path(self):
        return self.path_widget.cget("text")


class Settings(CWindow):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.close_sett)
        self.bind("<Escape>", self.close_sett)
        self.bind("<Return>", self.save_sett)
        self.title(cnf.lng.settings)
        self.minsize(450, 500)
        place_center(cnf.root, self, 450, 500)

        self.old_time = cnf.scan_time
        self.old_lng = cnf.lng

        self.browse_colls = BrowsePathFrame(
            self, path_label=cnf.lng.colls_path, path=cnf.coll_folder, 
            descr=cnf.lng.sett_descr
            )
        self.browse_colls.pack(fill="both", expand=1)

        CSep(self).pack(pady=15, padx=50, fill="x")

        self.browse_down = BrowsePathFrame(
            self, path_label=cnf.lng.down_path, path=cnf.down_folder, 
            descr=None
            )
        self.browse_down.pack(fill="both", expand=1)

        CSep(self).pack(pady=15, padx=50, fill="x")

        self.scan_btn = CButton(
            self, width=28,
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

        self.lang_btn = CButton(self, text=cnf.lng.language)
        self.lang_btn.pack(pady=(10, 0))
        self.lang_btn.cmd(self.lang_cmd)

        self.lang_descr = CLabel(
            self, text=cnf.lng.lang_descr, anchor="w", justify="left"
            )
        self.lang_descr.pack(anchor="w", pady=(15, 0))

        cancel_frame = CFrame(self)
        cancel_frame.pack(expand=1)

        CSep(cancel_frame).pack(pady=15, fill="x")

        save_btn = CButton(cancel_frame, text=cnf.lng.ok)
        save_btn.cmd(self.save_sett)
        save_btn.pack(padx=(0, 15), side="left")

        cancel_btn = CButton(cancel_frame, text=cnf.lng.cancel)
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

    def close_sett(self, e=None):
        cnf.scan_time = self.old_time
        cnf.lng = self.old_lng
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()

    def save_sett(self, e=None):
        new_down_path = self.browse_down.get_path()
        new_colls_path = self.browse_colls.get_path()

        self.grab_release()
        self.destroy()
        cnf.root.focus_force()

        if new_down_path:
            cnf.down_folder = new_down_path
            cnf.write_cfg()

        if cnf.coll_folder != new_colls_path:
            cnf.coll_folder = new_colls_path
            cnf.write_cfg()

            if smb_check():
                scaner.scaner_start()
            else:
                scaner.scaner_sheldue()
                SmbAlert()

        if self.old_lng != cnf.lng:
            cnf.reload_scroll()
            cnf.reload_menu()
            cnf.reload_strbar()

