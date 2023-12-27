import tkinter

import sqlalchemy

from cfg import cnf
from database import Dbase, ThumbsMd

from .context import Context
from .widgets import *

__all__ = ("Menu",)


class ContextMenu(Context):
    def __init__(self, e: tkinter.Event, btn: CButton, collname: str):
        Context.__init__(self)
        self.show_coll(e=e, btn=btn, collname=collname)
        self.reveal_coll_context(collname=collname)
        self.sep()

        for k, v in cnf.lng.filter_names.items():
            self.apply_filter_menu(label=v, collname=collname, btn=btn,
                                   filter=k)

        self.apply_filter_menu(label=cnf.lng.show_all, collname=collname,
                               btn=btn, filter="all")

        self.do_popup_menu(e=e, btn=btn, collname=collname)


class Menu(CScroll):
    def __init__(self, master: tkinter):
        CScroll.__init__(self, master=master, fg_color=cnf.bg_color_menu,
                         corner_radius=0, width=cnf.menu_w,
                         scroll_color=cnf.sel_color_menu)

        try:
            self.__menu_frame = self.__load_menu_buttons()
        except Exception:
            self.print_err(write=True)

        self.__menu_frame.pack(anchor="w", fill="x")

    def __load_menu_buttons(self):
        frame = CFrame(master=self, bg=cnf.bg_color_menu)

        title = CButton(master=frame, text=cnf.lng.menu,
                        font=("San Francisco Pro", 14, "bold"),
                        fg_color=cnf.bg_color_menu,
                        text_color=cnf.tit_color_menu,
                        anchor="w")
        title.pack(pady=(15,15), padx=10, anchor="w", fill="x")

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(ThumbsMd.collection)
            .distinct()
            ).fetchall()
        colls_list = (i[0] for i in colls_list)

        menus = {coll.lstrip('0123456789').strip(): coll
                 for coll in colls_list
                 }

        sort_keys = sorted(menus.keys())

        menus = {fake_name: menus[fake_name]
                 for fake_name in sort_keys}

        last = CButton(master=frame, text=cnf.lng.all_colls, anchor="w",
                       fg_color=cnf.bg_color_menu,
                       text_color=cnf.fg_color_menu)
        last.pack(pady=(0, 15), fill="x", padx=10, anchor="w")

        last.cmd(lambda e: cnf.show_coll(btn=last, collname=cnf.all_colls))
        last.bind(sequence="<Button-2>", command=lambda e:
                  ContextMenu(e=e, btn=last, collname=cnf.all_colls))

        for fakename, collname in menus.items():
            btn = CButton(master=frame, text=fakename[:23],
                          fg_color=cnf.bg_color_menu, 
                          text_color=cnf.fg_color_menu, anchor="w")
            btn.pack(fill="x", padx=10, anchor="w")

            btn.cmd(lambda e, btn=btn, collname=collname:
                    cnf.show_coll(btn=btn, collname=collname))
            btn.bind(sequence="<Button-2>",
                     command=lambda e, btn=btn, collname=collname:
                     ContextMenu(e=e, btn=btn, collname=collname))

            if collname == cnf.curr_coll:
                btn.configure(fg_color=cnf.sel_color_menu)
                self.sel_btn = btn
    
        if cnf.curr_coll == cnf.all_colls:
            last.configure(fg_color=cnf.sel_color_menu)
            self.sel_btn = last

        return frame

    def reload_menu(self):
        self.__menu_frame.destroy()
        self.__menu_frame = self.__load_menu_buttons()
        self.__menu_frame.pack(anchor="w", fill="x")
    
    def show_coll(self, btn: CButton, collname: str):
        cnf.limit = 150

        if hasattr(self, "sel_btn"):
            self.sel_btn.configure(fg_color=cnf.bg_color_menu)

        btn.configure(fg_color=cnf.sel_color_menu)
        self.sel_btn = btn
        cnf.curr_coll = collname

        cnf.date_start, cnf.date_end = None, None
        cnf.search_var.set(value="")
