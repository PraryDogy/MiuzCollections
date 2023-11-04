import tkinter

from cfg import cnf
from .scaner import scaner
from .utils import *

from .settings import Settings
from .widgets import *

__all__ = (
    "StBar",
    )


class ScanerGui(CWindow):
    def __init__(self):
        super().__init__()
        self.title(cnf.lng.updating)
        self.geometry("300x90")
        place_center(cnf.root, self, 300, 90)
        self.protocol("WM_DELETE_WINDOW", self.close_gui)
        self.bind("<Escape>", self.close_gui)

        self.live_lbl = CLabel(
            self, text=cnf.scan_win_txt, anchor="w", justify="left",
            )
        self.live_lbl.pack(expand=1, fill="both")

        self.can_btn = CButton(self, text=cnf.lng.cancel)
        self.can_btn.pack(pady=(10, 0))
        self.can_btn.cmd(self.cancel)

        self.live_task = False
        self.update_livelbl()

        cnf.root.update_idletasks()
        self.grab_set_global()

    def cancel(self, e=None):
        cnf.scan_flag = False
        cnf.root.after_cancel(self.live_task)
        self.live_lbl.configure(text=cnf.lng.please_wait)
        while cnf.scaner_task.is_alive():
            cnf.root.update()
        self.close_gui()

    def update_livelbl(self):
        if self.winfo_exists():
            self.live_lbl.configure(text=cnf.scan_win_txt)
            self.live_task = cnf.root.after(100, self.update_livelbl)

        if not cnf.scan_win_txt:
            cnf.root.after_cancel(self.live_task)
            self.close_gui()

    def close_gui(self, e=None):
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()


class StBar(CFrame):
    def __init__(self, master):
        super().__init__(master)

        self.stbar = self.load_stbar()
        self.stbar.pack(fill="x")

    def load_stbar(self):
        frame = CFrame(self)

        btn = CButton(frame, text=cnf.lng.settings, width=9, bg=cnf.bg_color)
        btn.cmd(lambda e: self.settings_cmd(btn))
        btn.pack(side="left", padx=(0, 10))

        upd_btn = CButton(frame, text=cnf.lng.update, width=9, bg=cnf.bg_color)
        upd_btn.cmd(self.update_cmd)
        upd_btn.pack(side="left")
        cnf.stbar_btn = upd_btn

        return frame

    def reload_stbar(self):
        self.stbar.destroy()
        self.stbar = self.load_stbar()
        self.stbar.pack(fill="x")

    def settings_cmd(self, e=None):
        Settings()

    def update_cmd(self, e=None):
        if not cnf.scan_flag:
            if smb_check():
                scaner.scaner_start()
            else:
                scaner.scaner_sheldue()
                SmbAlert()
                return
        else:
            ScanerGui()
