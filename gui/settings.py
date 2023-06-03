from . import (Dbase, Thumbs, auto_scan, conf, filedialog, on_exit,
               place_center, smb_check, sqlalchemy, tkinter, cancel_scan)
from .widgets import *

__all__ = (
    "Settings",
    )


class Settings(CWindow):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.cancel_cmd)
        self.bind('<Command-w>', self.cancel_cmd)
        self.bind('<Escape>', self.cancel_cmd)
        self.title(conf.lang.settings_title)
        self.geometry("400x270")

        self.main_wid = self.main_widget()
        self.main_wid.pack(expand=True, fill="both")

        conf.root.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.changed_lang = False
        self.scan_again = False

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

        t = conf.lang.settings_descr
        self.sett_desc = CLabel(frame, text=t, anchor="w", justify="left")
        self.sett_desc.pack(anchor="w", pady=(15, 0))
        conf.lang_sett.append(self.sett_desc)

        cancel_frame = CFrame(frame)
        cancel_frame.pack(expand=True)

        CSep(cancel_frame).pack(pady=15, fill=tkinter.X)

        save_btn = CButton(cancel_frame, text=conf.lang.ok)
        save_btn.cmd(self.save_cmd)
        save_btn.pack(padx=(0, 10), side="left")
        conf.lang_sett.append(save_btn)

        cancel_btn = CButton(cancel_frame, text=conf.lang.cancel)
        cancel_btn.cmd(self.cancel_cmd)
        cancel_btn.pack(side="left")
        conf.lang_sett.append(cancel_btn)

        return frame

    def change_lang(self):
        wids = conf.lang_menu + conf.lang_sett + conf.lang_st_bar + conf.lang_thumbs

        for wid in (wids):
            for k, v in self.old_lang.__dict__.items():
                try:
                    if wid["text"] == v:
                        wid["text"] = conf.lang.__dict__[k]
                except tkinter.TclError:
                    print("change lang widget err", wid.widgetName)

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

    def select_path_cmd(self):
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
        self.destroy()
        focus_last()

    def save_cmd(self, e=None):
        conf.lang_sett.clear()
        conf.coll_folder = self.path_widget['text']

        if self.lang_btn["text"] == "English":
            conf.json_lang = "English"
        else:
            conf.json_lang = "Russian"

        conf.write_cfg()
        self.destroy()
        focus_last()

        if self.scan_again:
            self.scan_again = False

            cancel_scan()

            if smb_check():
                auto_scan()
            else:
                SmbAlert()

        if self.changed_lang:
            from .application import app
            app.thumbnails.reload_with_scroll()
