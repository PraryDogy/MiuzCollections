import tkinter

from cfg import cnf

from .filter import Filter
from .utils import *
from .widgets import *


class ContextSearch(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.clear()
        self.pastesearch()
        self.do_popup(e=e)


class SearchWid(CEntry):
    def __init__(self, master: tkinter, **kw):
        super().__init__(
            master,
            textvariable=cnf.search_var,
            width=200,
            **kw)

        self.bind("<Escape>", lambda e: cnf.root.focus_force())
        cnf.root.bind("<Command-f>", lambda e: self.focus_force())

        self.bind("<Return>", self.__search_go)
        self.bind("<ButtonRelease-2>", ContextSearch)

        cnf.search_var.trace("w", lambda *args: self.__create_search_task(args))
        self.search_task = None
        self.old_search_var = None

    def __cancel_search_task(self):
        if self.search_task:
            cnf.root.after_cancel(self.search_task)

    def __create_search_task(self, *args):
        search_var = cnf.search_var.get()
        if search_var:
            if search_var != self.old_search_var:
                self.__cancel_search_task()
                self.search_task = cnf.root.after(1000, self.__search_go)

    def __search_go(self, e=None):
        self.__cancel_search_task()
        self.old_search_var = cnf.search_var.get()
        cnf.search_var.set(self.get())
        cnf.start, cnf.end = None, None
        cnf.reload_scroll()
        self.focus_force()


class FiltersWid(CFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        self.filter_btns = {}

        for k, v in cnf.lng.filter_names.items():
            btn = CButton(self, text=cnf.lng.filter_names[k])
            btn.pack(side="left", fill="x", padx=(0, 5))
            self.filter_btns[btn] = k

        for k, v in self.filter_btns.items():
            k.cmd(lambda e, v=v: self.__filter_btn_cmd(v))

        self.dates_btn = CButton(self, text=cnf.lng.dates)
        self.dates_btn.pack(side="left", fill="x", padx=(0, 5))
        self.dates_btn.cmd(lambda e: Filter())

        self.reload_filters()

    def __filter_btn_cmd(self, v):
        cnf.filter_values[v] = False if cnf.filter_values[v] else True
        self.reload_filters()
        cnf.reload_scroll()

    def reload_filters(self):
        for k, v in self.filter_btns.items():
            k: CButton
            if cnf.filter_values[v]:
                k.configure(fg_color=cnf.btn_color,
                            text=cnf.lng.filter_names[v] + " ⨂")
            else:
                k.configure(fg_color=cnf.bg_color,
                    text=cnf.lng.filter_names[v] + " ⨁")

        if any((cnf.start, cnf.end)):
            self.dates_btn.configure(
                fg_color=cnf.btn_color,
                text=cnf.lng.dates + " ⨂"
                )
        else:
            self.dates_btn.configure(
                fg_color=cnf.bg_color,
                text=cnf.lng.dates + " ⨁"
                )


class FuncBar(CFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        if cnf.curr_coll == cnf.all_colls:
            coll_title = cnf.lng.all_colls
        else:
            coll_title = cnf.curr_coll

        first_row = CFrame(self)
        first_row.pack(fill="x", pady=(0, 5))
        second_row = CFrame(self)
        second_row.pack(fill="x")

        self.topbar_title = CLabel(
            first_row, text=coll_title, anchor="w",
            font=("San Francisco Pro", 22, "bold"))
        self.topbar_title.pack(anchor="w", side="left")

        search = SearchWid(first_row)
        search.pack(anchor="e", side="right")

        self.filters_wid = FiltersWid(second_row)
        self.filters_wid.pack(anchor="w")

    def set_topbar_title(self):
        if cnf.curr_coll == cnf.all_colls:
            coll_title = cnf.lng.all_colls
        else:
            coll_title = cnf.curr_coll

        self.topbar_title.configure(text=coll_title)


class NotifyBar(CFrame):
    def __init__(self, master: tkinter, fg_color=cnf.bg_color, **kw):
        self.fg_color = fg_color
        super().__init__(master, bg=fg_color, **kw)

        self.btn_up = CButton(self, text=f"▲", fg_color=fg_color)
        self.btn_up.pack(side="left", fill="x", expand=1)
        self.btn_up.cmd(lambda e: cnf.move_up())

    def notibar_text(self, text):
        try:
            self.btn_up.configure(text=text, fg_color=cnf.blue_color)
            if len(self.children) < 2:
                self.topbar_can = CButton(
                    self, text=cnf.lng.cancel, fg_color=cnf.blue_color,
                    )
                self.topbar_can.configure()
                self.topbar_can.cmd(lambda e: cancel_utils_task())
                self.topbar_can.pack(side="left", padx=(1, 0))
        except RuntimeError as e:
            print("thumbnails > topbar text error")
            print(e)

    def notibar_default(self):
        try:
            self.topbar_can.destroy()
        except AttributeError as e:
            print("thumbnails > no topbar cancel button")
            print(e)
        try:
            self.btn_up.configure(text=f"▲", fg_color=self.fg_color)
        except RuntimeError as e:
            print("thumbnails > can't configure topbar to default")
            print(e)


class TopBar(NotifyBar):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        self.notibar = NotifyBar(self)
        self.notibar.pack(fill="x", padx=15, pady=(5, 5))

        self.funcbar = FuncBar(self)
        self.funcbar.pack(padx=15, fill="x")
