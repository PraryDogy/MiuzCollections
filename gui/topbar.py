import tkinter

from cfg import cnf
from utils import SysUtils, FinderBase

from .calendar_win import CalendarWin
from .context import Context
from .widgets import *

__all__ = ("TopBar", )


class ContextSearch(Context):
    def __init__(self, e: tkinter.Event):
        Context.__init__(self)
        self.clear()
        self.pastesearch()
        self.do_popup(e=e)


class SearchWid(CEntry):
    def __init__(self, master: tkinter, width: int = 200,
                 textvariable: tkinter.Variable = cnf.search_var, **kw):
        CEntry.__init__(self, master=master, width=width,
                        textvariable=textvariable, **kw)

        self.bind(sequence="<Escape>", command=lambda e: cnf.root.focus_force())
        cnf.root.bind(sequence="<Command-f>", func=lambda e: self.focus_force())

        self.bind(sequence="<Return>", command=self.__search_go)
        self.bind(sequence="<ButtonRelease-2>", command=ContextSearch)

        cnf.search_var.trace(mode="w", callback=lambda *args:
                             self.__create_search_task(args))
        self.__search_task = None
        self.__old_search_var = None

    def __cancel_search_task(self):
        if self.__search_task:
            cnf.root.after_cancel(self.__search_task)

    def __create_search_task(self, *args):
        search_var = cnf.search_var.get()
        if search_var:
            if search_var != self.__old_search_var:
                self.__cancel_search_task()
                self.__search_task = cnf.root.after(1000, self.__search_go)
        else:
            cnf.reload_scroll()
            cnf.root.focus_force()

    def __search_go(self, e=None):
        self.__cancel_search_task()
        self.__old_search_var = cnf.search_var.get()
        cnf.search_var.set(value=self.get())
        cnf.date_start, cnf.date_end = None, None
        cnf.reload_scroll()
        self.focus_force()


class FiltersWid(CFrame):
    def __init__(self, master: tkinter, bg: str = cnf.bg_color, **kwargs):
        CFrame.__init__(self, master=master, bg=bg, **kwargs)

        self.__filter_btns = {}

        for k, v in cnf.lng.filter_names.items():
            btn = CButton(master=self, text=cnf.lng.filter_names[k])
            btn.pack(side="left", fill="x", padx=(0, 5))
            self.__filter_btns[btn] = k

        for k, v in self.__filter_btns.items():
            k.cmd(lambda e, v=v: self.__filter_btn_cmd(v=v))

        self.dates_btn = CButton(master=self, text=cnf.lng.dates)
        self.dates_btn.pack(side="left", fill="x", padx=(0, 5))
        self.dates_btn.cmd(self.open_calendar)

        self.reload_filters()

    def open_calendar(self, e: tkinter.Event = None):
        self.calendar_win = CalendarWin()

    def __filter_btn_cmd(self, v):
        cnf.filter_values[v] = False if cnf.filter_values[v] else True
        self.reload_filters()
        cnf.reload_scroll()

    def reload_filters(self):
        for k, v in self.__filter_btns.items():
            k: CButton
            if cnf.filter_values[v]:
                k.configure(fg_color=cnf.btn_color,
                            text=cnf.lng.filter_names[v] + " ⨂")
            else:
                k.configure(fg_color=cnf.bg_color,
                            text=cnf.lng.filter_names[v] + " ⨁")

        if any((cnf.date_start, cnf.date_end)):
            self.dates_btn.configure(fg_color=cnf.btn_color,
                                     text=cnf.lng.dates + " ⨂")
        else:
            self.dates_btn.configure(fg_color=cnf.bg_color,
                                     text=cnf.lng.dates + " ⨁")


class FuncBar(CFrame):
    def __init__(self, master: tkinter, bg: str = cnf.bg_color, **kwargs):
        CFrame.__init__(self, master=master, bg=bg, **kwargs)

        if cnf.curr_coll == cnf.all_colls:
            coll_title = cnf.lng.all_colls
        else:
            coll_title = cnf.curr_coll

        first_row = CFrame(master=self)
        first_row.pack(fill="x", pady=(0, 5))
        second_row = CFrame(master=self)
        second_row.pack(fill="x")

        self.__topbar_title = CLabel(master=first_row, text=coll_title, anchor="w", 
                                     font=("San Francisco Pro", 22, "bold"))
        self.__topbar_title.pack(anchor="w", side="left")

        search = SearchWid(master=first_row)
        search.pack(anchor="e", side="right")

        self.filters_wid = FiltersWid(master=second_row)
        self.filters_wid.pack(anchor="w")

    def set_topbar_title(self):
        if cnf.curr_coll == cnf.all_colls:
            coll_title = cnf.lng.all_colls
        else:
            coll_title = cnf.curr_coll

        self.__topbar_title.configure(text=coll_title)
   

class NotifyBar(CFrame, FinderBase, SysUtils):
    def __init__(self, master: tkinter, bg: str = cnf.bg_color, **kwargs):
        CFrame.__init__(self, master=master, bg=bg, **kwargs)

        self.__fg_color = bg

        self.__btn_up = CButton(self, text=f"▲", fg_color=bg)
        self.__btn_up.pack(side="left", fill="x", expand=1)
        self.__btn_up.cmd(lambda e: cnf.move_up())

    def notibar_text(self, text: str):
        try:
            self.__btn_up.configure(text=text, fg_color=cnf.blue_color)
            if len(self.children) < 2:
                self._topbar_can = CButton(master=self, text=cnf.lng.cancel,
                                          fg_color=cnf.blue_color)
                self._topbar_can.cmd(lambda e: self.cancel_utils_task())
                self._topbar_can.pack(side="left", padx=(1, 0))
        except RuntimeError:
            self.print_err()

    def notibar_default(self):
        if hasattr(self, "_topbar_can"):
            self._topbar_can.destroy()
            self.__btn_up.configure(text=f"▲", fg_color=self.__fg_color)


class TopBar(CFrame):
    def __init__(self, master: tkinter):
        CFrame.__init__(self, master=master)

        self.notibar = NotifyBar(self)
        self.notibar.pack(fill="x", padx=15, pady=(5, 5))

        self.funcbar = FuncBar(self)
        self.funcbar.pack(padx=15, fill="x")
