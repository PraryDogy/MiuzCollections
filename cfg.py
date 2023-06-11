import json
import os
import shutil
import threading
import tkinter
from lang import Rus, Eng
import locale
import subprocess

__all__ = (
    "conf",
    )


class Config:
    def __init__(self):
        self.app_name = 'MiuzCollections'
        self.app_ver = '3.8.0'
        self.db_name = "db.db"
        self.thumb_err = "thumb.jpg"

        self.cfg_dir = os.path.join(
            os.path.expanduser("~"),
            f"Library", "Application Support", self.app_name
            )
        self.json_dir = os.path.join(self.cfg_dir, "cfg.json")
        self.db_dir = os.path.join(self.cfg_dir, self.db_name)

        self.fg_color = "#E2E2E2"
        self.bg_color = "#19191B"
        self.btn_color = "#2A2A2D"
        # self.sel_color = '#0056D9'
        self.sel_color = "#4B4B4B"
        self.hov_color = '#3A3A3E'
        self.ent_color = "#141416"

        self.thumb_size = 150
        self.menu_w = 180
        self.limit = 150
        self.thumb_pad = 3
        self.all_colls = "all"

        # dynamic variables for gui
        self.lang = None

        # list stores widgets for dynamicaly language change
        self.lang_menu = []
        self.lang_st_bar = []
        self.lang_thumbs = []
        self.lang_sett = []

        self.flag = False
        self.live_text = ""
        self.scaner_task: threading.Thread = None

        # root
        self.root = tkinter.Tk()
        self.root.withdraw()

        # user settings for json
        self.coll_folder = '/Volumes/Shares/Marketing/Photo/_Collections'

        self.curr_coll = self.all_colls

        self.root_w = 700
        self.root_h = 500
        self.root_x = 100
        self.root_y = 100

        self.preview_w = 700
        self.preview_h = 500

        self.autoscan_time = 10

        self.sort_modified = True
        self.catalog = False
        self.product = True
        self.models = True
        self.catalog_name = "Обтравка"
        self.models_name = "Model IMG"
        self.json_lang = "English"

        self.stopwords = [
            "preview", "1x1", "1х1", "crop", "копия", "copy"
            ]

    def load_cfg(self):
        with open(file=self.json_dir, encoding="utf8", mode="r") as file:
            data = json.loads(file.read())

        for key in data:
            if key in self.__dict__:
                setattr(self, key, data[key])

        if self.json_lang == "English":
            self.lang = Eng()
        else:
            self.lang = Rus()

    def write_cfg(self):
        slice_keys = list(self.__dict__)
        start = slice_keys.index("coll_folder")
        slice_keys = slice_keys[start:]

        data = {i: self.__dict__[i] for i in slice_keys}

        with open(file=self.json_dir, encoding='utf8', mode="w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def check_dir(self):
        if not os.path.exists(self.cfg_dir):
            os.mkdir(self.cfg_dir)

        if not os.path.exists(self.json_dir):

            cmd = "return user locale of (get system info)"
            l = subprocess.check_output(["osascript", "-e", cmd], text=True)
            l = l.split("\n")[0]
            if "ru_RU" == l:
                self.json_lang = "Russian"
            else:
                self.json_lang = "English"

            self.write_cfg()

        if not os.path.exists(self.db_dir):
            shutil.copyfile(self.db_name, self.db_dir)

    def get_defaults(self):
        return self.__class__()


conf = Config()
conf.check_dir()
conf.load_cfg()