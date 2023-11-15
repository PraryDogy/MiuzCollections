from cfg import cnf
from .widgets import *
from lang import Rus, Eng
from .utils import *

class LangWin(CWindow):
    def __init__(self, bg=cnf.bg_color, padx=15, pady=15, **kwargs):
        super().__init__(bg, padx, pady, **kwargs)
        w, h = 200, 100
        self.minsize(w, h)
        place_center(cnf.root, self, w, h)
        
        en, ru = Eng(), Rus()

        title = CLabel(self, text=en.lang_label)
        title.pack()

        

        for i in (en, ru):

            btn = CButton(self, text=i.language)
            btn.pack(pady=(10, 0), fill="x")


        self.update_idletasks()
        self.grab_set_global()