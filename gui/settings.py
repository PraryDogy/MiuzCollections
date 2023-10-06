import tkinter
from tkinter import filedialog

from cfg import conf
from scaner import Scaner
from utils import *

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
        self.title(conf.lang.settings_title)
        self.geometry("400x310")

        self.changed_lang = False
        self.scan_again = False
        self.old_curr_coll = conf.curr_coll

        self.main_wid = self.main_widget()
        self.main_wid.pack(expand=True, fill="both")

        conf.root.update_idletasks()

        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def main_widget(self):
        frame = CFrame(self)

        path_name = CLabel(
            frame,
            text=conf.lang.settings_label,
            anchor="w",
            justify="left"
            )
        path_name.pack(anchor="w")
        conf.lang_sett.append(path_name)

        self.path_widget = CLabel(
            frame,
            text=f"{conf.coll_folder}",
            anchor="w",
            justify="left"
            )
        self.path_widget.pack(anchor="w")

        select_path = CButton(frame, text=conf.lang.settings_browse)
        select_path.cmd(self.select_path_cmd)
        select_path.pack(pady=(5, 0))
        conf.lang_sett.append(select_path)

        asklang_frame = CFrame(frame)
        asklang_frame.pack(pady=(15, 0))

        self.lang_btn = CButton(asklang_frame)
        self.lang_btn.pack(side="left", padx=(0, 15))
        self.lang_btn.cmd(self.lang_cmd)

        if conf.json_lang == "Russian":
            self.lang_btn.configure(text="Русский")
        else:
            self.lang_btn.configure(text="English")

        self.reset_btn = CButton(asklang_frame, text=conf.lang.settings_reset)
        self.reset_btn.cmd(self.default_cmd)
        self.reset_btn.pack(side="left")
        conf.lang_sett.append(self.reset_btn)

        autoscan_frame = CFrame(frame)
        autoscan_frame.pack(pady=(15, 0))

        self.autoscan_min = CButton(autoscan_frame, text="<")
        self.autoscan_min.configure(width=1, bg=conf.bg_color)
        self.autoscan_min.pack(side="left", pady=(0, 2))
        self.autoscan_min.cmd(self.change_mins_cmd)

        conf.lang.autoscan_time = conf.autoscan_time
        self.temp_mins = conf.autoscan_time
        conf.lang.update_autoscan()

        self.autoupd_wid = CLabel(
            autoscan_frame,
            text=conf.lang.sett_autoscan,
            width=30
            )
        self.autoupd_wid.pack(side="left")
        conf.lang_sett.append(self.autoupd_wid)

        self.autoscan_max = CButton(autoscan_frame, text=">")
        self.autoscan_max.configure(width=1, bg=conf.bg_color)
        self.autoscan_max.pack(side="left", pady=(0, 2))
        self.autoscan_max.cmd(self.change_mins_cmd)

        t = conf.lang.settings_descr
        self.sett_desc = CLabel(frame, text=t, anchor="w", justify="left")
        self.sett_desc.pack(anchor="w", pady=(15, 0))
        conf.lang_sett.append(self.sett_desc)

        cancel_frame = CFrame(frame)
        cancel_frame.pack(expand=True)

        CSep(cancel_frame).pack(pady=15, fill=tkinter.X)

        save_btn = CButton(cancel_frame, text=conf.lang.ok)
        save_btn.cmd(self.save_cmd)
        save_btn.pack(padx=(0, 15), side="left")
        conf.lang_sett.append(save_btn)

        cancel_btn = CButton(cancel_frame, text=conf.lang.cancel)
        cancel_btn.cmd(self.cancel_cmd)
        cancel_btn.pack(side="left")
        conf.lang_sett.append(cancel_btn)

        return frame

    def change_mins_cmd(self, e=None):
        t = e.widget["text"]
        times = {1: 5, 2: 10, 3: 30, 4: 60}
        key = [k for k, v in times.items() if v == conf.autoscan_time][0]

        if t == "<":
            try:
                conf.autoscan_time = times[key-1]
            except KeyError:
                conf.autoscan_time = times[4]
        else:
            try:
                conf.autoscan_time = times[key+1]
            except KeyError:
                conf.autoscan_time = times[1]

        conf.lang.autoscan_time = conf.autoscan_time
        conf.lang.update_autoscan()
        self.autoupd_wid.configure(text=conf.lang.sett_autoscan)

    def change_lang(self):
        conf.lang.autoscan_time = conf.autoscan_time
        conf.lang.update_autoscan()
        self.autoupd_wid.configure(text=conf.lang.sett_autoscan)

        wids = conf.lang_menu + conf.lang_sett
        wids = wids + conf.lang_stbar + conf.lang_thumbs

        for wid in (wids):
            for k, v in self.old_lang.__dict__.items():
                try:
                    if wid["text"] == v:
                        wid["text"] = conf.lang.__dict__[k]
                except tkinter.TclError:
                    print("change lang widget err", wid.widgetName)
                    print(wid.__dict__)

    def lang_cmd(self, e=None):
        from lang import Eng, Rus

        self.changed_lang = True

        if self.lang_btn["text"] == "English":
            self.lang_btn["text"] = "Русский"
            self.title("Настройки")

            self.old_lang = conf.lang
            conf.lang = Rus()

            self.change_lang()

        else:
            self.lang_btn["text"] = "English"
            self.title("Settings")

            self.old_lang = conf.lang
            conf.lang = Eng()

            self.change_lang()

    def select_path_cmd(self, e=None):
        path = filedialog.askdirectory(initialdir=conf.coll_folder)

        if len(path) == 0:
            return

        if self.path_widget["text"] != path:
            self.path_widget['text'] = path
            self.scan_again = True

    def default_cmd(self, e=None):
        self.reset_btn.press()
        default = conf.get_defaults()
        self.path_widget['text'] = default.coll_folder
        self.scan_again = True

    def cancel_cmd(self, e=None):
        if self.changed_lang:
            self.lang_cmd()

        conf.lang_sett.clear()
        conf.autoscan_time = self.temp_mins

        self.destroy()
        focus_last()

    def save_cmd(self, e=None):
        conf.lang_sett.clear()
        conf.coll_folder = self.path_widget['text']
        conf.smb_ip = smb_ip()

        if self.lang_btn["text"] == "English":
            conf.json_lang = "English"
        else:
            conf.json_lang = "Russian"

        conf.write_cfg()
        self.destroy()
        focus_last()

        if self.scan_again:
            conf.curr_coll = conf.all_colls
            self.scan_again = False
            if smb_check():
                Scaner().auto_scan()
            else:
                SmbAlert()

        if self.changed_lang:
            Globals.reload_scroll()
