import json
import os
import shutil
import threading
import tkinter
from datetime import datetime
import traceback
try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal


__all__ = (
    "cnf",
    )


class ConfigGui:
    def reload_strbar(self):
        from gui.application import app
        app.stbar.reload_stbar()

    def reload_menu(self):
        from gui.application import app
        app.menu.reload_menu()

    def show_coll(self, btn, collname):
        from gui.application import app
        app.menu.show_coll(btn, collname)
        self.set_topbar_title()
        self.reload_scroll()

    def notibar_text(self, text):
        from gui.application import app
        app.topbar.notibar.notibar_text(text)

    def notibar_default(self):
        from gui.application import app
        app.topbar.notibar.notibar_default()

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

    def load_langwin(self):
        from gui.lang_win import LangWin
        LangWin()

    def set_topbar_title(self):
        from gui.application import app
        app.topbar.funcbar.set_topbar_title()

    def reload_filters(self):
        from gui.application import app
        app.topbar.funcbar.filters_wid.reload_filters()

    def move_up(self):
        from gui.application import app
        app.thumbs.scroll.moveup()


class User:
    def __init__(self) -> None:
        self.coll_folder = "/Volumes/Shares/Marketing/Photo/_Collections"
        self.down_folder = f"{os.path.expanduser('~')}/Downloads"
        self.curr_coll = "None"
        self.user_lng = "None"
        self.scan_time = 10

        self.root_g = {"w": 700, "h": 500, "x": 100, "y": 100}
        self.imgview_g = {"w": 700, "h": 500, "x": 100, "y": 100}

        self.filter_values = {"prod": False, "mod": False, "cat": False,
                              "other": False}

        self.filter_true_names = {"prod": "1 IMG", "mod": "2 Model IMG",
                                  "cat": "5 Обтравка"}


class Config(ConfigGui, User):
    def __init__(self):
        ConfigGui.__init__(self)
        User.__init__(self)
        self.app_name = "MiuzCollections"
        self.app_ver = "3.9.3"
        self.db_name = "db.db"
        self.cfg_name = "cfg.json"
        self.thumb_err = "thumb.jpg"
        self.lng = None

        self.cfg_dir = os.path.join(os.path.expanduser("~"),
            f"Library", "Application Support", self.app_name)
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
        self.thumbsize = 150
        self.thumbspad = 3
        self.limit = 150
        self.hidescroll_ms = 1000
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

    def load_cfg(self):
        with open(file=self.json_dir, encoding="utf8", mode="r") as file:
            data: dict = json.loads(s=file.read())

        for k, v in data.items():
            if hasattr(self, k):
                if isinstance(v, dict):
                    v = self.__fix_dict(namedict=k, userdict=v)
                setattr(self, k, v)

        if not os.path.exists(os.path.join(self.coll_folder, self.curr_coll)):
            self.curr_coll = self.all_colls

        self.set_language(lang_name=self.user_lng)

    def write_cfg(self):
        data = {i: getattr(self, i) for i in list(User().__dict__)}

        with open(file=self.json_dir, encoding="utf8", mode="w") as file:
            json.dump(obj=data, fp=file, indent=4, ensure_ascii=False)

    def set_language(self, lang_name: Literal["en", "ru"]):
        from lang import Rus, Eng

        ru, en = Rus(), Eng()
        if lang_name not in (ru.name, en.name):
            self.lng = en
            self.user_lng = en.name
            self.load_langwin()
        else:
            self.lng = [i for i in (ru, en) if i.name==lang_name][0]
            self.user_lng = lang_name

    def check_dir(self):
        if not os.path.exists(path=self.cfg_dir):
            os.mkdir(path=self.cfg_dir)

        if not os.path.exists(path=self.json_dir):
            self.write_cfg()

        if not os.path.exists(path=self.db_dir):
            shutil.copyfile(src=self.db_name, dst=self.db_dir)

    def __fix_dict(self, namedict: str, userdict: dict):
        cnf_dict: dict = getattr(self, namedict)

        for k, v in cnf_dict.items():
            if k not in userdict:
                userdict[k] = v

        return {k: v
                for k, v in userdict.items()
                if k in cnf_dict}


cnf = Config()
cnf.check_dir()
cnf.load_cfg()
cnf.write_cfg()
