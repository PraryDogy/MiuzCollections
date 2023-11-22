import tkinter
from typing import Literal

from cfg import cnf

from .utils import *
from .widgets import *
from utils_p import FinderActions

__all__ = ("Context", )


class MenuCollections:
    def reveal_coll(self, collname: str):
        self.add_command(
            label=cnf.lng.reveal_coll,
            command=lambda:
            reveal_coll(collname=collname))

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
            apply_filter(filter=filter, collname=collname, btn=btn))



class SearchThumbs:
    def pastesearch(self):
        self.add_command(label=cnf.lng.paste, command=paste_search)

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


class ImgInfo:
    def copy_text(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.copy,
            command=lambda:
            copy_text(text=e.widget.copy))

    def copy_all(self, e:tkinter.Event):
        self.add_command(
            label=cnf.lng.copy_all,
            command=lambda:
            copy_text(text=e.widget.get("1.0",tkinter.END)))


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
            command=lambda: db_remove_img(src=img_src)
            )

    def apply_filter_thumbs(self, label: str,
                            filter: Literal["cnf > lng > filter_names > name", "all"]):
        self.add_command(
            label=label,
            command=lambda: apply_filter(filter=filter)
            )