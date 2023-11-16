import tkinter
from tkinter import filedialog

from cfg import cnf
from .scaner import scaner
from .utils import *
from .smb_alert import SmbAlert
from .widgets import *

__all__ = (
    "Settings",
    )


class BrowsePathFrame(CFrame):
    def __init__(self, master, title, path, **kw):
        super().__init__(master, **kw)

        title_lbl = CLabel(
            self, text=title, anchor="w", justify="left", 
            )
        title_lbl.pack(anchor="w", pady=(0, 5))

        first_row = CFrame(self)
        first_row.pack(anchor="w")

        path_selector = CButton(first_row, text=cnf.lng.browse)
        path_selector.cmd(lambda e: self.selector_cmd(path))
        path_selector.pack(anchor="w", side="left")

        self.path_lbl = CLabel(
            first_row, text=f"{path}", anchor="w", justify="left",
            wraplength = 300,
            )
        self.path_lbl.pack(anchor="w", side="left", padx=10)

    def get_path(self):
        return self.path_lbl.cget("text")

    def selector_cmd(self, path, e=None):
        dialog = filedialog.askdirectory(initialdir=path, parent=self)
        self.focus_force()

        if len(dialog) == 0:
            return

        if self.get_path() != dialog:
            self.path_lbl.configure(text=dialog)


class ScanerWid(CFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        scan_btn = CButton(
            self,  text=f"{cnf.scan_time} {cnf.lng.mins}", width=75,
            )
        scan_btn.cmd(lambda e: self.scan_time_cmd(scan_btn, e))
        scan_btn.pack(side="left")

        scan_title = CLabel(self, text=cnf.lng.update_every)
        scan_title.pack(side="left", padx=10)

    def scan_time_cmd(self, btn: CButton, e=None):
        times = [5, 10, 30, 60]

        if hasattr(self, "new_scan_time"):
            ind = times.index(self.new_scan_time)
        else:
            try:
                ind = times.index(cnf.scan_time)
            except ValueError:
                ind = 0

        try:
            self.new_scan_time = times[ind+1]
        except IndexError:
            self.new_scan_time = times[0]

        btn.configure(
            text=f"{self.new_scan_time} {cnf.lng.mins}"
            )


class FiltersWid(CFrame):
    def __init__(self, master, **kw):
        super().__init__(master)
        self.bind("<ButtonRelease-1>", lambda e: self.focus_force())

        title = CLabel(self, text=cnf.lng.filters)
        title.pack(anchor="w")

        self.entries = {}

        for k, v in cnf.filter_true_names.items():
            row = CFrame(self)
            row.pack(pady=(10, 0), anchor="w")

            lbl = CLabel(
                row, text=cnf.lng.filter_names[k], width=9,
                anchor="w", justify="left"
                )
            lbl.pack(side="left")

            ent = CEntry(row, textvariable=tkinter.StringVar(self, v))
            ent.pack(side="left")
            self.entries[k] = ent

    def get_entries_values(self):
        return {
            k: v.get()
            for k, v in self.entries.items()
            }


class LangWid(CFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)

        lang_btn = CButton(self, text=cnf.lng.language)
        lang_btn.pack(side="left")
        lang_btn.cmd(lambda e: self.lang_cmd(lang_btn, e))

        title = CLabel(
            self, text=cnf.lng.lang_label, anchor="w", justify="left")
        title.pack(side="left", padx=10)

    def lang_cmd(self, btn: CButton, e=None):
        from lang import Eng, Rus

        for i in (Rus(), Eng()):
            if cnf.user_lng != i.name:
                self.new_lang = i.name
                btn.configure(text=i.language)
                return


class Settings(CWindow):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.close_sett)
        self.bind("<Escape>", self.close_sett)
        self.bind("<Return>", self.save_sett)
        self.title(cnf.lng.settings)
        w, h = 440, 490
        self.minsize(w, h)
        place_center(cnf.root, self, w, h)

        pader = 15

        self.browse_colls = BrowsePathFrame(
            self, title=cnf.lng.colls_path, path=cnf.coll_folder
            )
        self.browse_colls.pack(anchor="w", pady=(0, pader))

        self.browse_down = BrowsePathFrame(
            self, title=cnf.lng.down_path, path=cnf.down_folder
            )
        self.browse_down.pack(anchor="w")

        CSep(self).pack(fill="x", pady=pader)

        self.scaner_wid = ScanerWid(self)
        self.scaner_wid.pack(anchor="w", pady=(0, pader))

        self.lang_wid = LangWid(self)
        self.lang_wid.pack(anchor="w")

        CSep(self).pack(fill="x", pady=pader)

        self.filters = FiltersWid(self)
        self.filters.pack(anchor="w")

        CSep(self).pack(fill="x", pady=pader)

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

    def close_sett(self, e=None):
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()

    def save_sett(self, e=None):
        if hasattr(self.scaner_wid, "new_scan_time"):
            cnf.scan_time = self.scaner_wid.new_scan_time

        if hasattr(self.lang_wid, "new_lang"):
            cnf.set_language(lang_name=self.lang_wid.new_lang)

        cnf.down_folder = self.browse_down.get_path()

        entries = self.filters.get_entries_values()
        for k, v in entries.items():
            cnf.filter_true_names[k] = v

        if cnf.coll_folder != self.browse_colls.get_path():
            cnf.coll_folder = self.browse_colls.get_path()
            cnf.curr_coll = cnf.all_colls
            if smb_check():
                scaner.scaner_sheldue(1500)
            else:
                scaner.scaner_sheldue()
                SmbAlert()

        cnf.write_cfg()

        self.grab_release()
        self.destroy()
        cnf.root.focus_force()

        cnf.set_topbar_title()
        cnf.reload_filters()
        cnf.reload_menu()
        cnf.reload_strbar()
        cnf.reload_scroll()
