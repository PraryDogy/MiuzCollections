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

        if descr:
            path_label = path_label + "\n" + descr

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

    def select_path_cmd(self, path, e=None):
        dialog = filedialog.askdirectory(initialdir=path, parent=self)
        self.focus_force()

        if len(dialog) == 0:
            return

        if self.path_widget.cget("text") != dialog:
            self.path_widget.configure(text=dialog)

    def get_path(self):
        return self.path_widget.cget("text")


class FiltersWid(CFrame):
    def __init__(self, master, **kw):
        super().__init__(master)
        self.bind("<ButtonRelease-1>", lambda e: self.focus_force())

        title = CLabel(self, text=cnf.lng.filters)
        title.pack(anchor="w")

        for k, v in cnf.filter_true_name.items():
            row = CFrame(self)
            row.pack(pady=(10, 0), anchor="w")

            lbl = CLabel(
                row, text=cnf.lng.filter_names[k], width=7,
                anchor="w", justify="left"
                )
            lbl.pack(side="left", padx=(0, 10))

            ent = CEntry(row, textvariable=tkinter.StringVar(self, v))
            ent.pack(side="left")
            setattr(__class__, k, ent)

        self.get_entries_values()

    def get_entries_values(self):
        return {
            k: getattr(__class__, k).get()
            for k, v in cnf.filter_true_name.items()
            }


class Settings(CWindow):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.close_sett)
        self.bind("<Escape>", self.close_sett)
        self.bind("<Return>", self.save_sett)
        self.title(cnf.lng.settings)
        w, h = 500, 610
        self.minsize(w, h)
        place_center(cnf.root, self, w, h)

        self.browse_colls = BrowsePathFrame(
            self, path_label=cnf.lng.colls_path, path=cnf.coll_folder, 
            descr=cnf.lng.sett_descr
            )
        self.browse_colls.pack(fill="both", expand=1)

        CSep(self).pack(pady=15, padx=50, fill="x")

        self.filters = FiltersWid(self)
        self.filters.pack(fill="both", expand=1)

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
            text=cnf.lng.lang_label + "\n" + cnf.lng.lang_descr,
            anchor="w",
            justify="left",
            )
        lang_lbl.pack(anchor="w")

        self.lang_btn = CButton(self, text=cnf.lng.language)
        self.lang_btn.pack(pady=(10, 0))
        self.lang_btn.cmd(self.lang_cmd)

        CSep(self).pack(fill="x", pady=15, padx=50)

        cancel_frame = CFrame(self)
        cancel_frame.pack()

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
        new_scan_time = "new_scan_time"

        if hasattr(__class__, new_scan_time):
            ind = times.index(getattr(__class__, new_scan_time))
        else:
            try:
                ind = times.index(cnf.scan_time)
            except ValueError:
                ind = -1

        try:
            setattr(__class__, new_scan_time, times[ind+1])
        except IndexError:
            setattr(__class__, new_scan_time, times[0])

        t = getattr(__class__, new_scan_time)
        self.scan_btn.configure(
            text=f"{cnf.lng.update_every} {t} {cnf.lng.mins}"
            )

    def lang_cmd(self, e=None):
        from lang import Eng, Rus

        for i in (Rus(), Eng()):
            if cnf.lang != i.name:
                setattr(__class__, "new_lang", i.name)
                self.lang_btn.configure(text=i.language)
                return

    def close_sett(self, e=None):
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()

    def save_sett(self, e=None):
        if hasattr(__class__, "new_scan_time"):
            cnf.scan_time = getattr(__class__, "new_scan_time")

        if hasattr(__class__, "new_lang"):
            cnf.lang = getattr(__class__, "new_lang")
            cnf.set_lng()

        cnf.down_folder = self.browse_down.get_path()

        entries = self.filters.get_entries_values()
        for k, v in entries.items():
            cnf.filter_true_name[k] = v

        if cnf.coll_folder != self.browse_colls.get_path():
            cnf.coll_folder = self.browse_colls.get_path()
            if smb_check():
                scaner.scaner_sheldue(3000)
            else:
                scaner.scaner_sheldue()
                SmbAlert()

        cnf.write_cfg()

        self.grab_release()
        self.destroy()
        cnf.root.focus_force()

        cnf.reload_scroll()
        cnf.reload_menu()
        cnf.reload_strbar()