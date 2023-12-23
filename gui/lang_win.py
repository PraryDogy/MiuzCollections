from cfg import cnf
from lang import Eng, Rus
from utils import SysUtils

from .widgets import *

__all__ = ("LangWin", )


class LangWin(CWindow, SysUtils):
    def __init__(self, bg=cnf.bg_color, padx=15, pady=15):

        en, ru = Eng(), Rus()

        CWindow.__init__(self, bg=bg, padx=padx, pady=pady)
        w, h = 200, 100
        self.minsize(width=w, height=h)
        self.place_center(w=w, h=h)        
        self.title(string=en.lang_label)

        title = CLabel(master=self, text=en.lang_label)
        title.pack()

        for i in (en, ru):

            btn = CButton(master=self, text=i.language)
            btn.pack(pady=(10, 0), fill="x")
            btn.cmd(lambda e: self.__set_lng(lng_name=i.name))

        self.update_idletasks()
        self.grab_set_global()

    def __set_lng(self, lng_name: str):
        from lang import Eng, Rus
        en, ru = Eng(), Rus()

        for i in (en, ru):
            if i.name == lng_name:
                cnf.user_lng = lng_name
                cnf.set_language(lang_name=lng_name)
                self.destroy()
                cnf.set_topbar_title()
                cnf.reload_filters()
                cnf.reload_menu()
                cnf.reload_strbar()
                cnf.reload_scroll()
                return