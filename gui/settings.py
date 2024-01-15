import tkinter
from tkinter import filedialog

from cfg import cnf

from .smb_alert import SmbAlert
from .widgets import *

try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal

from utils import Scaner, SysUtils, Watcher

__all__ = ("Settings",)


class Win:
    win: CWindow = False


class BrowsePathFrame(CFrame, SysUtils):
    def __init__(self, master: tkinter, title: str,
                 path: Literal["str pathlike object"]):

        super().__init__(master=master)

        title_lbl = CLabel(master=self, text=title, anchor="w", justify="left")
        title_lbl.pack(anchor="w", pady=(0, 5))

        first_row = CFrame(master=self)
        first_row.pack(anchor="w")

        path_selector = CButton(master=first_row, text=cnf.lng.browse)
        path_selector.cmd(lambda e: self.__selector_cmd(path=path))
        path_selector.pack(anchor="w", side="left")

        self.__path_lbl = CLabel(first_row, text=path, anchor="w",
                               justify="left", wraplength = 300)
        self.__path_lbl.pack(anchor="w", side="left", padx=10)

    def get_path(self) -> Literal["str path like"]:
        return self.__path_lbl.cget(key="text")

    def __selector_cmd(self, path: Literal["str pathlike object"],
                     e: tkinter.Event = None):
        dialog = filedialog.askdirectory(initialdir=path, parent=self)
        self.focus_force()

        if len(dialog) == 0:
            return

        if self.get_path() != dialog:
            self.__path_lbl.configure(text=dialog)


class ScanerWid(CFrame, SysUtils):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        scan_btn = CButton(master=self, text=f"{cnf.scan_time_sec} {cnf.lng.mins}")
        scan_btn.cmd(lambda e: self.__scan_time_cmd(btn=scan_btn, e=e))
        scan_btn.pack(side="left")

        scan_title = CLabel(master=self, text=cnf.lng.update_every)
        scan_title.pack(side="left", padx=10)

    def __scan_time_cmd(self, btn: CButton, e: tkinter.Event = None):
        times = [1, 5, 10, 30, 60]

        if hasattr(self, "new_scan_time"):
            ind = times.index(self.new_scan_time)
        else:
            try:
                ind = times.index(cnf.scan_time_sec)
            except ValueError:
                # self.print_err()
                ind = 0

        try:
            self.new_scan_time = times[ind+1]
        except IndexError:
            self.print_err()
            self.new_scan_time = times[0]

        btn.configure(text=f"{self.new_scan_time} {cnf.lng.mins}")


class FiltersWid(CFrame):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)
        self.bind(sequence="<ButtonRelease-1>",
                  func=lambda e: self.focus_force())

        title = CLabel(master=self, text=cnf.lng.filters)
        title.pack(anchor="w")

        self.__filter_entries = {}

        for k, v in cnf.filter_true_names.items():
            row = CFrame(master=self)
            row.pack(pady=(10, 0), anchor="w")

            lbl = CLabel(master=row, text=cnf.lng.filter_names[k], width=9,
                anchor="w", justify="left")
            lbl.pack(side="left")

            ent = CEntry(master=row, textvariable=tkinter.StringVar(self, v))
            ent.pack(side="left")
            self.__filter_entries[k] = ent

    def filter_entries_values(self) -> dict[str, str]:
        """
        dict keys: cnf > filter_true names > keys
        dict values: text from entry
        """
        return {k: v.get()
                for k, v in self.__filter_entries.items()}


class LangWid(CFrame):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        lang_btn = CButton(master=self, text=cnf.lng.language)
        lang_btn.pack(side="left")
        lang_btn.cmd(lambda e: self.__lang_cmd(btn=lang_btn, e=e))

        title = CLabel(master=self, text=cnf.lng.lang_label, anchor="w",
                       justify="left")
        title.pack(side="left", padx=10)

    def __lang_cmd(self, btn: CButton, e: tkinter.Event = None):
        from lang import Eng, Rus

        for i in (Rus(), Eng()):
            if cnf.user_lng != i.name:
                self.new_lang = i.name
                btn.configure(text=i.language)
                return


class SettingsVar:
    def set(self, value: int):
        cnf.settings_var.set(value=value)
        cnf.settings_var.get()


class Settings(CWindow, SysUtils):
    def __init__(self):
        w, h = 440, 440

        if Win.win:
            Win.win.destroy()
            Win.win = False
            SettingsVar().set(value=0)

        SettingsVar().set(value=1)
        CWindow.__init__(self)
        Win.win = self

        self.protocol(name="WM_DELETE_WINDOW", func=self.__close_sett)
        self.bind(sequence="<Escape>", func=self.__close_sett)
        self.bind(sequence="<Return>", func=self.__save_sett)
        self.title(string=cnf.lng.settings)
        self.minsize(width=w, height=h)
        self.place_center(w=w, h=h)

        pader = 15

        self.__browse_colls = BrowsePathFrame(
            master=self, title=cnf.lng.colls_path, path=cnf.coll_folder)
        self.__browse_colls.pack(anchor="w", pady=(0, pader))

        self.__browse_down = BrowsePathFrame(
            master=self, title=cnf.lng.down_path, path=cnf.down_folder)
        self.__browse_down.pack(anchor="w")

        CSep(master=self).pack(fill="x", pady=pader)

        # self.__scaner_wid = ScanerWid(master=self)
        # self.__scaner_wid.pack(anchor="w", pady=(0, pader))

        self.__lang_wid = LangWid(master=self)
        self.__lang_wid.pack(anchor="w")

        CSep(master=self).pack(fill="x", pady=pader)

        self.__filters = FiltersWid(master=self)
        self.__filters.pack(anchor="w")

        CSep(master=self).pack(fill="x", pady=pader)

        cancel_frame = CFrame(master=self)
        cancel_frame.pack()

        save_btn = CButton(master=cancel_frame, text=cnf.lng.ok)
        save_btn.cmd(self.__save_sett)
        save_btn.pack(padx=(0, 15), side="left")

        cancel_btn = CButton(master=cancel_frame, text=cnf.lng.cancel)
        cancel_btn.cmd(self.__close_sett)
        cancel_btn.pack(side="left")

    def __close_sett(self, e: tkinter.Event = None):
        Win.win = False
        self.destroy()
        cnf.root.focus_force()
        SettingsVar().set(value=0)

    def __save_sett(self, e: tkinter.Event = None):
        if hasattr(self.__lang_wid, "new_lang"):
            cnf.set_language(lang_name=self.__lang_wid.new_lang)

        cnf.down_folder = self.__browse_down.get_path()

        entries = self.__filters.filter_entries_values()
        for k, v in entries.items():
            cnf.filter_true_names[k] = v

        if cnf.coll_folder != self.__browse_colls.get_path():
            cnf.coll_folder = self.__browse_colls.get_path()
            cnf.curr_coll = cnf.all_colls

            if not self.smb_check():
                SmbAlert()

            Watcher.observer.stop()
            cnf.root.after(ms=500, func=Scaner)
            cnf.root.after(ms=500, func=Watcher)

        cnf.write_cfg()

        self.destroy()
        cnf.root.focus_force()

        cnf.set_topbar_title()
        cnf.reload_filters()
        cnf.reload_menu()
        cnf.reload_strbar()
        cnf.reload_scroll()

        Win.win = False
        SettingsVar().set(value=0)