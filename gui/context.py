import os
import subprocess
import tkinter
from typing import Literal

import sqlalchemy

from cfg import cnf
from database import *
from utils import FinderActions, SysUtils

from .widgets import *

__all__ = ("Context", )


class ContextUtils(SysUtils):
    def reveal_coll(self, collname: str):
        if collname != cnf.all_colls:
            coll_path = os.path.join(cnf.coll_folder, collname)
        else:
            coll_path = cnf.coll_folder

        try:
            subprocess.check_output(["/usr/bin/open", coll_path])
        except subprocess.CalledProcessError:
            subprocess.check_output(["/usr/bin/open", cnf.coll_folder])

    def paste_search(self):
        try:
            pasted = cnf.root.clipboard_get().strip()
            cnf.search_var.set(value=pasted)
        except tkinter.TclError:
            self.print_err()

    def apply_filter(self, filter: Literal["all"] | Literal["cnf > filter values key"],
                     btn: tkinter = None, collname: str = None):
        if filter == "all":
            for k, v in cnf.filter_values.items():
                cnf.filter_values[k] = False
        else:
            for k, v in cnf.filter_values.items():
                cnf.filter_values[k] = False
            cnf.filter_values[filter] = True

        if collname and btn:
            cnf.reload_filters()
            cnf.show_coll(btn=btn, collname=collname)
        else:
            cnf.reload_filters()
            cnf.reload_scroll()

    def copy_text(self, text: str):
        cnf.root.clipboard_clear()
        cnf.root.clipboard_append(string=text)

    def db_remove_img(self, img_src: Literal["file path"]):
        q = (
            sqlalchemy.delete(ThumbsMd).filter(
                ThumbsMd.src==img_src
                ))
        Dbase.conn.execute(q)
        cnf.reload_thumbs()


class MenuCollections(ContextUtils):
    def reveal_coll_context(self, collname: str):
        self.add_command(
            label=cnf.lng.reveal_coll,
            command=lambda:
            self.reveal_coll(collname=collname))

    def show_coll(self, e: tkinter.Event, btn: CButton, collname: str):
        self.add_command(
            label=cnf.lng.view,
            command=lambda:
            cnf.show_coll(btn=btn, collname=collname))

    def apply_filter_menu(
            self, label: str, collname: str, btn: CButton,
            filter: Literal["cnf > lng > filter_names > name", "all"]):

        self.add_command(
            label=label,
            command=lambda:
            self.apply_filter(filter=filter, collname=collname, btn=btn))


class SearchThumbs(ContextUtils):
    def pastesearch(self):
        self.add_command(label=cnf.lng.paste, command=self.paste_search)

    def clear(self):
        self.add_command(
            label=cnf.lng.clear,
            command=lambda:
            cnf.search_var.set(""))


class ImgSingle:
    def imgview(self, img_src: Literal["file path"]):
        from .img_viewer import ImgViewer
        self.add_command(
            label=cnf.lng.view,
            command=lambda:
            ImgViewer(src=img_src))

    def imginfo(self, parrent: CWindow, img_src: Literal["file path"]):
        from .img_info import ImageInfo
        self.add_command(
            label=cnf.lng.info,
            command=lambda:
            ImageInfo(parrent=parrent, src=img_src))

    def reveal_jpg(self, img_src: Literal["file path"]):
        self.add_command(
            label=cnf.lng.find_jpg,
            command=lambda:
            FinderActions(src=img_src, reveal=True))

    def reveal_tiff(self, img_src: Literal["file path"]):
        self.add_command(
            label=cnf.lng.find_tiff,
            command=lambda:
            FinderActions(src=img_src, tiff=True, reveal=True))

    def download_jpg(self, img_src: Literal["file path"]):
        self.add_command(
            label=f"{cnf.lng.download} jpg {cnf.lng.to_downloads}",
            command=lambda:
            FinderActions(src=img_src, download=True))

    def download_tiff(self, img_src: Literal["file path"]):
        self.add_command(
            label=f"{cnf.lng.download} tiff {cnf.lng.to_downloads}",
            command=lambda:
            FinderActions(src=img_src, tiff=True, download=True))

    def copy_jpg_path(self, img_src: Literal["file path"]):
        self.add_command(
            label=cnf.lng.copy_path_jpg,
            command=lambda:
            FinderActions(src=img_src, clipboard=True))

    def copy_tiff_path(self, img_src: Literal["file path"]):
        self.add_command(
            label=cnf.lng.copy_path_tiff,
            command=lambda:
            FinderActions(src=img_src, tiff=True, clipboard=True))

    def download_fullsize(self, img_src: Literal["file path"]):
        self.add_command(
            label=cnf.lng.fullsize,
            command=lambda:
            FinderActions(src=img_src, tiff=True, fullsize=True))

class ImgGroup:
    def download_group(
            self, title: str,
            path_list: tuple[Literal["file path"], ...]):

        self.add_command(
            label=(f"{cnf.lng.copy} jpg\n"
                   f"{cnf.lng.from_pretext} \"{title}\" "
                   f"{cnf.lng.to_downloads}"),
            command=lambda:
            FinderActions(src=path_list, download=True))

    def download_group_tiffs(
            self, title: str,
            path_list: tuple[Literal["file path"], ...]):

        self.add_command(
            label=(f"{cnf.lng.copy} tiff\n"
                   f"{cnf.lng.from_pretext} \"{title}\" "
                   f"{cnf.lng.to_downloads}"),
            command=lambda:
            FinderActions(src=path_list, tiff=True, download=True))

    def download_group_fullsize(
            self, title: str,
            path_list=tuple[Literal["file path"], ...]):
        self.add_command(
            label=(f"{cnf.lng.group_fullsize}\n"
                   f"{cnf.lng.from_pretext} \"{title}\" "
                   f"{cnf.lng.to_downloads}"),
            command=lambda:
            FinderActions(src=path_list, tiff=True, fullsize=True))


class ImgInfo(ContextUtils):
    def copy_text(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.copy,
            command=lambda:
            self.copy_text(text=e.widget.copy))

    def copy_all(self, e:tkinter.Event):
        self.add_command(
            label=cnf.lng.copy_all,
            command=lambda:
            self.copy_text(text=e.widget.get("1.0",tkinter.END)))


class Context(tkinter.Menu, MenuCollections, SearchThumbs, ImgSingle, ImgGroup, ImgInfo):
    def __init__(self):
        tkinter.Menu.__init__(self)

    def sep(self):
        self.add_separator()

    def do_popup(self, e: tkinter.Event):
        try:
            self.tk_popup(x=e.x_root, y=e.y_root)
        finally:
            self.grab_release()
        
    def do_popup_menu(self, e: tkinter.Event, btn: CButton, collname: str):
        try:
            btn.configure(fg_color=cnf.blue_color)
            self.tk_popup(x=e.x_root, y=e.y_root)
        finally:
            if collname == cnf.curr_coll:
                btn.configure(fg_color=cnf.lgray_color)
            else:
                btn.configure(fg_color=cnf.bg_color_menu)
            self.grab_release()

    def db_remove_img(self, img_src: Literal["file path"]):
        self.add_command(
            label=cnf.lng.remove_fromapp,
            command=lambda: self.db_remove_img(src=img_src)
            )

    def apply_filter_thumbs(self, label: str,
                            filter: Literal["cnf > lng > filter_names > name", "all"]):
        self.add_command(
            label=label,
            command=lambda: self.apply_filter(filter=filter)
            )