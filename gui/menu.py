import os
import subprocess
import tkinter

import sqlalchemy

from cfg import cnf
from database import Dbase, ThumbsMd
from utils import SysUtils

from .widgets import *

__all__ = ("Menu",)


class Context(tkinter.Menu):
    def __init__(self):
        tkinter.Menu.__init__(self)

    def sep(self):
        self.add_separator()

    def do_popup(self, e: tkinter.Event, btn: CButton, collname: str):
        try:
            btn.configure(fg_color=cnf.blue_color)
            self.tk_popup(x=e.x_root, y=e.y_root)
        finally:
            if collname == cnf.curr_coll:
                btn.configure(fg_color=cnf.lgray_color)
            else:
                btn.configure(fg_color=cnf.bg_color_menu)
            self.grab_release()


class ContextUtils(SysUtils):
    def reveal_coll_filtered_cmd(self, collname: str, filter: str):
        if collname != cnf.all_colls:
            coll_parrent = os.path.join(cnf.coll_folder, collname)
            coll_path = os.path.join(coll_parrent, filter)
        try:
            subprocess.check_output(["/usr/bin/open", coll_path])
        except (subprocess.CalledProcessError, UnboundLocalError):
            try:
                subprocess.check_output(["/usr/bin/open", coll_parrent])
            except UnboundLocalError:
                subprocess.check_output(["/usr/bin/open", cnf.coll_folder])

    def reveal_coll(self, collname: str):
        if collname != cnf.all_colls:
            coll_path = os.path.join(cnf.coll_folder, collname)
        else:
            coll_path = cnf.coll_folder

        try:
            subprocess.check_output(["/usr/bin/open", coll_path])
        except subprocess.CalledProcessError:
            subprocess.check_output(["/usr/bin/open", cnf.coll_folder])


class ContextMenuBase(Context, ContextUtils):
    def __init__(self):
        Context.__init__(self)

    def show_coll(self, e: tkinter.Event, btn: CButton, collname: str):
        self.add_command(
            label=cnf.lng.view,
            command=lambda:
            cnf.show_coll(btn=btn, collname=collname))

    def reveal_coll_context(self, collname: str):
        self.add_command(
            label=cnf.lng.reveal_coll,
            command=lambda:
            self.reveal_coll(collname=collname))

    def reveal_coll_filtered(self, collname: str, label: str, filter: str):
        self.add_command(
            label=f"{cnf.lng.open} {label.lower()}",
            command=lambda:
            self.reveal_coll_filtered_cmd(collname=collname, filter=filter))


class ContextMenu(ContextMenuBase):
    def __init__(self, e: tkinter.Event, btn: CButton, collname: str):
        ContextMenuBase.__init__(self)
        self.show_coll(e=e, btn=btn, collname=collname)

        self.sep()

        self.reveal_coll_context(collname=collname)

        for k, v in cnf.filter_true_names.items():
            self.reveal_coll_filtered(collname=collname, filter=v,
                                      label=cnf.lng.filter_names[k])

        self.do_popup(e=e, btn=btn, collname=collname)


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

        try:
            self.sel_btn.configure(fg_color=cnf.bg_color_menu)
        except tkinter.TclError:
            self.print_err()

        btn.configure(fg_color=cnf.sel_color_menu)
        self.sel_btn = btn
        cnf.curr_coll = collname

        cnf.date_start, cnf.date_end = None, None
        cnf.search_var.set(value="")
