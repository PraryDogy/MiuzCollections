import json
import os
import shutil
import threading
import tkinter
from lang import Rus, Eng
import subprocess

__all__ = (
    "cnf",
    )


class Config:
    def __init__(self):
        self.app_name = "MiuzCollections"
        self.app_ver = "3.9.2"
        self.db_name = "db.db"
        self.cfg_name = "cfg.json"
        self.thumb_err = "thumb.jpg"

        self.cfg_dir = os.path.join(
            os.path.expanduser("~"),
            f"Library", "Application Support", self.app_name
            )
        self.json_dir = os.path.join(self.cfg_dir, self.cfg_name)
        self.db_dir = os.path.join(self.cfg_dir, self.db_name)

        self.fg_color = "#E2E2E2"
        self.bg_color = "#19191B"
        self.btn_color = "#2A2A2D"
        self.blue_color = "#0056D9"
        self.lgray_color = "#4B4B4B"
        self.dgray_color = "#141416"

        self.thumb_size = 150 + 3
        self.menu_w = 180
        self.limit = 150
        self.all_colls = "all"

        # dynamic variables for gui
        self.lng = Rus()
        self.first_load = True
        self.scan_flag = False
        self.topbar_flag = True
        self.scan_win_txt = ""
        self.scaner_task: threading.Thread = None

        self.product_name = "IMG"
        self.catalog_name = "Обтравка"
        self.models_name = "Model IMG"

        # root
        self.root = tkinter.Tk()
        self.root.withdraw()

        # user settings for json
        self.coll_folder = "/Volumes/Shares/Marketing/Photo/_Collections"
        self.down_folder = f"{os.path.expanduser('~')}/Downloads"

        self.curr_coll = self.all_colls

        self.root_g = {"w": 700, "h": 500, "x": 100, "y": 100}
        self.imgview_g = {"w": 700, "h": 500, "x": 100, "y": 100}

        self.scan_time = 10

        self.sort_modified = True
        self.catalog = False
        self.product = True
        self.models = True
        self.lang = self.lng.name

    def load_cfg(self):
        with open(file=self.json_dir, encoding="utf8", mode="r") as file:
            data = json.loads(file.read())

        for key in data:
            if key in self.__dict__:
                setattr(self, key, data[key])

    def write_cfg(self):
        self.lang = self.lng.name
        slice_keys = list(self.__dict__)
        start = slice_keys.index("coll_folder")
        slice_keys = slice_keys[start:]

        data = {i: self.__dict__[i] for i in slice_keys}

        with open(file=self.json_dir, encoding="utf8", mode="w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def check_dir(self):
        if not os.path.exists(self.cfg_dir):
            os.mkdir(self.cfg_dir)

        if not os.path.exists(self.json_dir):

            cmd = "return user locale of (get system info)"
            l = subprocess.check_output(["osascript", "-e", cmd], text=True)
            l = l.split("\n")[0]
            if "ru_RU" == l:
                self.lng = Rus()
                self.lang = self.lng.name
            else:
                self.lng = Eng()
                self.lang = self.lng.name

            self.write_cfg()

        if not os.path.exists(self.db_dir):
            shutil.copyfile(self.db_name, self.db_dir)


cnf = Config()
cnf.check_dir()
cnf.load_cfg()
cnf.write_cfg()