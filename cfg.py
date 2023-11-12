import json
import os
import shutil
import subprocess
import threading
import tkinter
from datetime import datetime
import traceback
from lang import Eng, Rus

__all__ = (
    "cnf",
    )


class Config:
    def __init__(self):
        self.app_name = "MiuzCollections"
        self.app_ver = "3.9.3"
        self.db_name = "db.db"
        self.cfg_name = "cfg.json"
        self.thumb_err = "thumb.jpg"
        self.lng = None

        self.cfg_dir = os.path.join(
            os.path.expanduser("~"),
            f"Library", "Application Support", self.app_name
            )
        self.json_dir = os.path.join(self.cfg_dir, self.cfg_name)
        self.db_dir = os.path.join(self.cfg_dir, self.db_name)

        self.fg_color = "#E2E2E2"
        self.bg_color = "#1e1e1e"
        self.btn_color = "#303030"
        self.blue_color = "#0056D9"
        self.lgray_color = "#4B4B4B"
        self.dgray_color = "#141416"

        self.bg_color_menu = "#383838"
        self.sel_color_menu = "#525252"
        self.tit_color_menu = "#7b7b7b"
        self.fg_color_menu = "#e9e9e9"

        self.corner = 8
        self.scroll_width = 17
        self.menu_w = 200
        self.thumb_size = 150
        self.limit = 150
        self.autohide_scroll = 2000
        self.all_colls = "all"

        # root
        self.root = tkinter.Tk()
        self.root.withdraw()

        # global variables
        self.stbar_btn: tkinter.Label = None
        self.search_var = tkinter.StringVar(value="") # thumbnails > ThumbsSearch()
        self.start: datetime = None
        self.end: datetime = None
        self.named_start: str = None # datetime as readable text
        self.named_end: str = None # datetime as readable text
        self.set_calendar_title = None # filter > Filter().set_calendar_title()
        self.scan_flag = False
        self.topbar_flag = True
        self.scan_win_txt = ""
        self.scaner_task: threading.Thread = None
        self.all_src = []

        self.product_name = "IMG"
        self.catalog_name = "Обтравка"
        self.models_name = "Model IMG"

        # user settings for json
        self.coll_folder = "/Volumes/Shares/Marketing/Photo/_Collections"
        self.down_folder = f"{os.path.expanduser('~')}/Downloads"

        self.curr_coll = self.all_colls

        self.root_g = {"w": 700, "h": 500, "x": 100, "y": 100}
        self.imgview_g = {"w": 700, "h": 500, "x": 100, "y": 100}

        self.scan_time = 10

        self.filter_values = {"prod": True, "mod": True, "cat": False}

        self.filter_true_names = {
            "prod": "1 IMG", "mod": "2 Model IMG", "cat": "5 Обтравка"}

        self.user_lang = None

    def load_cfg(self):
        with open(file=self.json_dir, encoding="utf8", mode="r") as file:
            data: dict = json.loads(file.read())

        for k, v in data.items():
            if k in self.__dict__:
                setattr(self, k, v)

    def write_cfg(self):
        slice_keys = list(self.__dict__)
        start = slice_keys.index("coll_folder")
        slice_keys = slice_keys[start:]

        data = {i: self.__dict__[i] for i in slice_keys}

        with open(file=self.json_dir, encoding="utf8", mode="w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def set_lng(self):
        from lang import Rus, Eng
        for i in (Rus(), Eng()):
            if i.name == self.user_lang:
                self.lng = i
                break

        if not self.lng:
            self.set_system_lng()

    def set_system_lng(self):
        cmd = "return user locale of (get system info)"
        l = subprocess.check_output(["osascript", "-e", cmd], text=True)
        l = l.split("\n")[0]
        if "ru_RU" == l:
            self.lng = Rus()
            self.user_lang = self.lng.name
        else:
            self.lng = Eng()
            self.user_lang = self.lng.name

    def check_dir(self):
        if not os.path.exists(self.cfg_dir):
            os.mkdir(self.cfg_dir)

        if not os.path.exists(self.json_dir):
            self.set_system_lng()
            self.write_cfg()

        if not os.path.exists(self.db_dir):
            shutil.copyfile(self.db_name, self.db_dir)

    def reload_thumbs(self):
        from gui.application import app
        app.thumbs.reload_thumbs()

    def reload_scroll(self):
        try:
            from gui.application import app
            app.thumbs.reload_scroll()
        except Exception as ex:
            print("cfg > reload scroll import err")
            traceback.print_exception(type(ex), ex, ex.__traceback__)

    def reload_strbar(self):
        from gui.application import app
        app.stbar.reload_stbar()

    def reload_menu(self):
        from gui.application import app
        app.menu.reload_menu()

    def show_coll(self, btn, collname):
        from gui.application import app
        app.menu.show_coll(btn, collname)

    def notibar_text(self, text):
        from gui.application import app
        app.thumbs.notibar.notibar_text(text)

    def notibar_default(self):
        from gui.application import app
        app.thumbs.notibar.notibar_default()


cnf = Config()
cnf.check_dir()
cnf.load_cfg()
cnf.set_lng()
cnf.write_cfg()