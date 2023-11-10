import re
import tkinter

import sqlalchemy

from cfg import cnf
from database import Dbase, ThumbsMd

from .widgets import *

__all__ = (
    "Menu",
    )


class ContextMenu(Context):
    def __init__(self, e: tkinter.Event, btn, collname):
        super().__init__()
        self.show_coll(e, btn, collname)
        self.reveal_coll(collname)
        self.sep()

        for k, v in cnf.lng.filter_names.items():
            self.apply_filter_menu(
                label=v, filter=k, collname=collname, btn=btn)

        self.apply_filter_menu(
            label=cnf.lng.show_all, filter="all", collname=collname, btn=btn)

        self.do_popup_menu(e, btn, collname)


class Menu(CScroll):
    def __init__(self, master: tkinter):
        super().__init__(
            master, fg_color=cnf.bg_color_menu, corner_radius=0,
            width=cnf.menu_w
            )

        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack(anchor="w", fill="x")
        self.bind("<Enter>", lambda e: self.focus_force)
        self.bind_scroll_menu()

    def load_menu_buttons(self):
        frame = CFrame(self, bg=cnf.bg_color_menu)

        title = CButton(
            frame, text=cnf.lng.menu, font=("San Francisco Pro", 14, "bold"),
            fg_color=cnf.bg_color_menu, text_color=cnf.tit_color_menu,
            anchor="w",
            )
        title.pack(pady=(15,15), padx=10, anchor="w", fill="x")

        colls_list = Dbase.conn.execute(
            sqlalchemy.select(ThumbsMd.collection)
            .distinct()
            ).fetchall()
        colls_list = (i[0] for i in colls_list)

        menus = {
            coll.lstrip('0123456789').strip(): coll
            for coll in colls_list
            }

        sort_keys = sorted(menus.keys())

        menus = {
            fake_name: menus[fake_name]
            for fake_name in sort_keys
            }

        last = CButton(
            frame, text=cnf.lng.all_colls, anchor="w",
            fg_color=cnf.bg_color_menu, text_color=cnf.fg_color_menu
            )
        last.cmd(
            lambda e: cnf.show_coll(last, cnf.all_colls)
            )
        last.bind("<Button-2>", lambda e: ContextMenu(e, last, cnf.all_colls))
        last.pack(pady=(0, 15), fill="x", padx=10, anchor="w")

        for fakename, collname in menus.items():
            btn = CButton(
                frame, text=fakename[:23], fg_color=cnf.bg_color_menu, 
                text_color=cnf.fg_color_menu, anchor="w",
                )
            btn.pack(fill="x", padx=10, anchor="w")

            btn.cmd(
                lambda e,
                btn=btn, collname=collname: cnf.show_coll(btn, collname)
                )
            btn.bind("<Button-2>", (
                lambda e,
                btn=btn, collname=collname: ContextMenu(e, btn, collname)
                ))

            if collname == cnf.curr_coll:
                btn.configure(fg_color=cnf.sel_color_menu)
                self.sel_btn = btn
    
        if cnf.curr_coll == cnf.all_colls:
            last.configure(fg_color=cnf.sel_color_menu)
            self.sel_btn = last

        return frame

    def bind_scroll_menu(self):
        for i in (self, self.menu_frame, *self.menu_frame.winfo_children()):
            self.set_tag("scroll_menu", i.get_parrent())
        self.bind_autohide_scroll("scroll_menu")

    def reload_menu(self):
        self.menu_frame.destroy()
        self.menu_frame = self.load_menu_buttons()
        self.menu_frame.pack(anchor="w", fill="x")
        self.bind("<Enter>", lambda e: self.focus_force)
        self.bind_scroll_menu()
    
    def show_coll(self, btn: CButton, collname):
        cnf.limit = 150

        if hasattr(self, "sel_btn"):
            self.sel_btn.configure(fg_color=cnf.bg_color_menu)

        btn.configure(fg_color=cnf.sel_color_menu)
        self.sel_btn = btn
        cnf.curr_coll = collname

        cnf.start, cnf.end = None, None
        cnf.search_var.set("")
        cnf.reload_scroll()