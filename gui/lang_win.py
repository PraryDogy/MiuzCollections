from cfg import cnf
from lang import Eng, Rus

from .utils import *
from .widgets import *

__all__ = ("LangWin", )


class LangWin(CWindow):
    def __init__(self, bg=cnf.bg_color, padx=15, pady=15, **kwargs):

        en, ru = Eng(), Rus()

        super().__init__(bg, padx, pady, **kwargs)
        w, h = 200, 100
        self.minsize(w, h)
        place_center(self, w, h)        
        self.title(en.lang_label)

        title = CLabel(self, text=en.lang_label)
        title.pack()

        for i in (en, ru):

            btn = CButton(self, text=i.language)
            btn.pack(pady=(10, 0), fill="x")
            btn.cmd(lambda e: self.set_lng(lng_name=i.name))

        self.update_idletasks()
        self.grab_set_global()

    def set_lng(self, lng_name: str):
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