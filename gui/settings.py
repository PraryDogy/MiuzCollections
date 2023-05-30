from . import (Dbase, Thumbs, conf, filedialog, on_exit, os, place_center, re,
               scaner, smb_check, sqlalchemy, tkinter)
from .widgets import *

path_widget = tkinter.Label
SCAN_AGAIN = False

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
        conf.lang_sett.append(self)

        self.geometry("400x320")

        self.main_wid = self.main_widget()
        self.main_wid.pack(expand=True, fill="both")

        conf.root.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.changed_lang = False

    def main_widget(self):
        global path_widget

        frame = CFrame(self)

        path_name = CLabel(frame, text=conf.lang.settings_label)
        path_name.pack(anchor="w")
        conf.lang_sett.append(path_name)

        path_widget = CLabel(
            frame,
            text=f"{conf.coll_folder}",
            anchor="w",
            justify="left"
            )
        path_widget.pack(expand=True, fill="both")

        select_frame = CFrame(frame)
        select_frame.pack(pady=(5, 0))

        select_path = CButton(select_frame, text=conf.lang.settings_browse)
        select_path.cmd(lambda e: self.select_path_cmd())
        select_path.pack(side="left")
        conf.lang_sett.append(select_path)

        asklang_frame = CFrame(frame)
        asklang_frame.pack(pady=(15, 0))

        self.ask_btn = CButton(asklang_frame, text=conf.lang.settings_askexit)
        self.ask_btn.pack(side="left")
        self.ask_btn.cmd(self.ask_exit_cmd)
        conf.lang_sett.append(self.ask_btn)

        if conf.ask_exit:
            self.ask_btn.configure(bg=conf.sel_color)

        self.lang_btn = CButton(asklang_frame)
        self.lang_btn.pack(side="left", padx=(15, 0))
        self.lang_btn.cmd(self.lang_cmd)

        if conf.json_lang == "Russian":
            self.lang_btn.configure(text="Русский")
        else:
            self.lang_btn.configure(text="English")

        restore_btn = CButton(frame, text=conf.lang.settings_reset)
        restore_btn.cmd(lambda e, x=restore_btn: self.default_cmd(x))
        restore_btn.pack(pady=(15, 0))
        conf.lang_sett.append(restore_btn)

        t = conf.lang.settings_descr
        self.sett_desc = CLabel(frame, text=t, anchor="w", justify="left")
        self.sett_desc.pack(expand=True, fill="both", pady=(15, 0))
        conf.lang_sett.append(self.sett_desc)

        cancel_frame = CFrame(frame)
        cancel_frame.pack(expand=True)

        CSep(cancel_frame).pack(pady=15, fill=tkinter.X)

        save_btn = CButton(cancel_frame, text=conf.lang.ok)
        save_btn.cmd(lambda e: self.save_cmd())
        save_btn.pack(padx=(0, 10), side="left")
        conf.lang_sett.append(save_btn)

        cancel_btn = CButton(cancel_frame, text=conf.lang.cancel)
        cancel_btn.cmd(self.cancel_cmd)
        cancel_btn.pack(side="left")
        conf.lang_sett.append(cancel_btn)

        return frame

    def lang_cmd(self, e=None):
        from lang import Rus, Eng

        self.changed_lang = True

        if self.lang_btn["text"] == "English":
            self.lang_btn["text"] = "Русский"
            self.title("Настройки")
            conf.lang = Rus()

            for wid in (
                *conf.lang_menu, *conf.lang_sett,*conf.lang_st_bar, 
                *conf.lang_thumbs
                ):
                for k, v in Eng().__dict__.items():
                    if wid.widgetName == "label" and wid["text"] == v:
                        wid["text"] = conf.lang.__dict__[k]
        else:
            self.lang_btn["text"] = "English"
            self.title("Settings")
            conf.lang = Eng()

            for wid in (
                *conf.lang_menu, *conf.lang_sett,*conf.lang_st_bar, 
                *conf.lang_thumbs
                ):
                 for k, v in Rus().__dict__.items():
                    if wid.widgetName == "label" and wid["text"] == v:
                        wid["text"] = conf.lang.__dict__[k]

    def ask_exit_cmd(self, e):
        if self.ask_btn["bg"] == conf.btn_color:
            self.ask_btn.configure(bg=conf.sel_color)
        else:
            self.ask_btn.configure(bg=conf.btn_color)

    def select_path_cmd(self):
        global path_widget, SCAN_AGAIN
        path = filedialog.askdirectory(initialdir = conf.coll_folder)

        if len(path) == 0:
            return

        if path_widget["text"] != path:
            path_widget['text'] = path
            SCAN_AGAIN = True

    def default_cmd(self, btn: CButton):
        global SCAN_AGAIN

        btn.press()
        default = conf.get_defaults()
        path_widget['text'] = default.coll_folder

        Dbase.conn.execute(sqlalchemy.delete(Thumbs))
        Dbase.conn.execute("VACUUM")

        SCAN_AGAIN = True

    def cancel_cmd(self, e=None):
        if self.changed_lang:
            self.lang_cmd()

        conf.lang_sett.clear()
        self.destroy()
        focus_last()

    def save_cmd(self):
        global SCAN_AGAIN, SCANER_PERMISSION

        conf.lang_sett.clear()

        conf.coll_folder = path_widget['text']

        if self.ask_btn["bg"] == conf.sel_color:
            conf.ask_exit = True
            conf.root.protocol("WM_DELETE_WINDOW", AskExit)
            conf.root.createcommand("tk::mac::Quit" , AskExit)
        else:
            conf.ask_exit = False
            conf.root.createcommand("tk::mac::Quit" , on_exit)
            conf.root.protocol("WM_DELETE_WINDOW", on_exit)

        if self.lang_btn["text"] == "English":
            conf.json_lang = "English"
        else:
            conf.json_lang = "Russian"

        conf.write_cfg()
        self.destroy()
        focus_last()

        if SCAN_AGAIN:
            SCAN_AGAIN = False
            conf.flag = False

            try:
                while conf.scaner_task.is_alive():
                    conf.root.update()
            except AttributeError:
                print("settings.py: no task scaner")
            if smb_check():
                scaner()
            else:
                SmbAlert()
        elif self.changed_lang:
            from .application import app
            app.thumbnails.reload_with_scroll()
