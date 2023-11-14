import math
import tkinter
import traceback
from datetime import datetime

import sqlalchemy
from PIL import Image, ImageTk

from cfg import cnf
from database import Dbase, ThumbsMd

from .filter import Filter
from .img_viewer import ImgViewer
from .utils import *
from .widgets import *
from typing import Union, Tuple



__all__ = (
    "Thumbs",
    )


class ContextFilter(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()

        for k, v in cnf.lng.filter_names.items():
            self.apply_filter_thumbs(label=v, filter=k)

        self.apply_filter_thumbs(label=cnf.lng.show_all, filter="all")

        self.do_popup(e=e)


class ContextTitles(Context):
    def __init__(self, e: tkinter.Event, title: str, img_path_list: list):
        super().__init__()

        self.download_group(title=title, paths_list=img_path_list)

        self.sep()
        self.download_group_tiffs(title=title, paths_list=img_path_list)

        self.sep()
        self.download_group_fullsize(title=title, paths_list=img_path_list)

        self.do_popup(e=e)


class ContextAdvanced(Context):
    def __init__(self, e: tkinter.Event, img_src: str):
        super().__init__()
        self.db_remove_img(img_src=img_src)
        self.do_popup(e=e)


class ContextThumbs(Context):
    def __init__(self, e: tkinter.Event, img_src: str):
        super().__init__()

        self.imgview(img_src=img_src)
        self.imginfo(parrent=e.widget.winfo_toplevel(), img_src=img_src)

        self.sep()
        self.copy_jpg_path(img_src=img_src)
        self.reveal_jpg(img_src=img_src)
        self.download_onefile(img_src=img_src)

        self.sep()
        self.copy_tiffs_paths(img_src=img_src)
        self.reveal_tiffs(img_src=img_src)
        self.download_tiffs(img_src=img_src)

        self.sep()
        self.download_fullsize(img_src=img_src)

        self.do_popup(e=e)


class ContextSearch(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.clear()
        self.pastesearch()
        self.do_popup(e=e)


class ThumbsDict(dict):
    def __init__(self):
        super().__init__()
        data = Dbase.conn.execute(self.get_query()).fetchall()
        decoded = self.decode_thumbs(thumbs_raw=data)
        self.update(self.create_thumbs_dict(thumbs_raw=decoded))

    def decode_thumbs(self, thumbs_raw: Tuple[Tuple[bytes, str, int]]):
        result = []
        for blob, src, modified in thumbs_raw:
            try:
                decoded = decode_image(image=blob)
                cropped = crop_image(img=decoded)
                img = convert_to_rgb(image=cropped)
                result.append((img, src, modified))

            except Exception:
                print(traceback.format_exc())

        return result

    def create_thumbs_dict(self, thumbs_raw: Tuple[Tuple[bytes, str, int]]):
        thumbs_dict = {}

        for img, src, modified in thumbs_raw:
            date_key = datetime.fromtimestamp(modified).date()

            if not any((cnf.start, cnf.end)):
                date_key = f"{cnf.lng.months[date_key.month]} {date_key.year}"
            else:
                date_key = f"{cnf.named_start} - {cnf.named_end}"

            thumbs_dict.setdefault(date_key, [])
            thumbs_dict[date_key].append((img, src))

        return thumbs_dict

    def stamp_dates(self):
        start = datetime.combine(cnf.start, datetime.min.time())
        end = datetime.combine(
            cnf.end, datetime.max.time().replace(microsecond=0)
            )
        return (datetime.timestamp(start), datetime.timestamp(end))

    def get_query(self):
        q = sqlalchemy.select(ThumbsMd.img150, ThumbsMd.src, ThumbsMd.modified)

        search = cnf.search_var.get()
        if search:
            search.replace("\n", "").strip()
            q = q.filter(ThumbsMd.src.like("%" + search + "%"))

        if cnf.curr_coll != cnf.all_colls:
            q = q.filter(ThumbsMd.collection == cnf.curr_coll)

        filters = []
        for k, v in cnf.filter_true_names.items():
            if cnf.filter_values[k]:
                if cnf.filter_true_names[k]:
                    filters.append(
                        ThumbsMd.src.like(
                            "%" + f"/{cnf.filter_true_names[k]}/" + "%"
                            )
                            )
        q = q.filter(sqlalchemy.or_(*filters))

        if not any((cnf.start, cnf.end)):
            q = q.limit(cnf.limit)
        else:
            t = self.stamp_dates()
            q = q.filter(ThumbsMd.modified > t[0])
            q = q.filter(ThumbsMd.modified < t[1])

        q = q.order_by(-ThumbsMd.modified)
        return q


class ResetDatesBtn(CButton):
    def __init__(self, master: tkinter, fg_color: str = cnf.btn_color,
                width: int = 75, **kw):
        super().__init__(master=master, fg_color=fg_color, width=width,
                         text=cnf.lng.reset_dates, **kw)
        self.cmd(self.reset_dates_cmd)

    def reset_dates_cmd(self, e):
        cnf.start, cnf.end = None, None
        cnf.reload_scroll()


class ResetSearchBtn(CButton):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, text=cnf.lng.reset_search, **kw)
        self.cmd(self.reset_search_cmd)

    def reset_search_cmd(self, e):
        cnf.search_var.set("")
        cnf.reload_scroll()


class ResetFiltersBtn(CButton):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, text=cnf.lng.show_all, **kw)
        self.cmd(self.reset_filters_cmd)

    def reset_filters_cmd(self, e):
        for k, v in cnf.filter_values.items():
            cnf.filter_values[k] = False
        cnf.reload_scroll()


class SearchWid(CEntry):
    def __init__(self, master: tkinter, **kw):
        super().__init__(
            master,
            textvariable=cnf.search_var,
            width=200,
            **kw)

        self.bind("<Escape>", lambda e: cnf.root.focus_force())
        cnf.root.bind("<Command-f>", lambda e: self.focus_force())

        self.bind("<Return>", self.search_go)
        self.bind("<ButtonRelease-2>", ContextSearch)

        cnf.search_var.trace("w", lambda *args: self.create_search_task(args))
        self.search_task = None
        self.old_search_var = None

    def cancel_search_task(self):
        if self.search_task:
            cnf.root.after_cancel(self.search_task)

    def create_search_task(self, *args):
        search_var = cnf.search_var.get()
        if search_var:
            if search_var != self.old_search_var:
                self.cancel_search_task()
                self.search_task = cnf.root.after(1000, self.search_go)

    def search_go(self, e=None):
        self.cancel_search_task()
        self.old_search_var = cnf.search_var.get()
        cnf.search_var.set(self.get())
        cnf.start, cnf.end = None, None
        cnf.reload_scroll()
        cnf.root.focus_force()


class FiltersWid(CFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        self.filter_btns = {}

        for k, v in cnf.lng.filter_names.items():
            btn = CButton(self, text=cnf.lng.filter_names[k])
            btn.pack(side="left", fill="x", padx=(0, 5))
            self.filter_btns[btn] = k

        for k, v in self.filter_btns.items():
            k.cmd(lambda e, v=v: self.filters_cmd(v))

        self.dates_btn = CButton(self, text=cnf.lng.dates)
        self.dates_btn.pack(side="left", fill="x", padx=(0, 5))
        self.dates_btn.cmd(lambda e: Filter())

        self.reload_filters()

    def filters_cmd(self, v):
        cnf.filter_values[v] = False if cnf.filter_values[v] else True
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


class TopBar(CFrame):
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

        self.filters = FiltersWid(second_row)
        self.filters.pack(anchor="w")

    def set_title(self):
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


class NoImages(CFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        str_var = cnf.search_var.get()
        noimg_t = cnf.lng.no_photo

        no_images = CLabel(self, text=noimg_t,
                           font=("San Francisco Pro", 18, "bold"))
        no_images.pack(pady=(15, 0))

        if str_var:
            noimg_t = (
                f"{cnf.lng.no_photo} {cnf.lng.with_name}"
                f"\n\"{str_var}\""
                )
            no_images.configure(text=noimg_t)
            ResetSearchBtn(self).pack(pady=(15, 0))

        elif any((cnf.start, cnf.end)):
            noimg_t = (
                f"{cnf.lng.no_photo}"
                f"\n{cnf.named_start} - {cnf.named_end}"
                )
            no_images.configure(text=noimg_t)
            ResetDatesBtn(self).pack(pady=(15, 0))

        else:
            ResetFiltersBtn(self).pack(pady=(15, 0))


class AboveThumbs(CFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        if any((cnf.start, cnf.end)):
            ResetDatesBtn(self).pack(pady=(15, 0))
        elif cnf.search_var.get():
            ResetSearchBtn(self).pack(pady=(15, 0))


class ImgGridTitle(CLabel):
    def __init__(self, master: tkinter,
                 title: str,img_src_list: list,
                 bg=cnf.bg_color, fg=cnf.fg_color,
                 font=("San Francisco Pro", 18, "bold"),
                 ):

        text = f"{title}, {cnf.lng.total}: {len(img_src_list)}"
        if cnf.search_var.get():
            text = (
                f"{cnf.lng.photo} {cnf.lng.with_name} "
                f"\"{cnf.search_var.get()}\"\n{text}"
                )

        super().__init__(master, bg=bg, fg=fg, font=font,
                         text=text, anchor="w", justify="left")

        self.bind(
            "<ButtonRelease-2>", (
                lambda e, title=title,
                paths_list=img_src_list: 
                ContextTitles(e, title, paths_list)
                ))


class ImgGrid(CLabel):
    def __init__(self, master, grid_w, grid_h,
                 bg=cnf.bg_color, fg=cnf.fg_color, anchor="w"):

        super().__init__(master=master, bg=bg, fg=fg, anchor=anchor)

        self.bind("<ButtonRelease-1>", self.__click)
        self.bind("<ButtonRelease-2>", self.__r_click)
        self.bind("<Command-ButtonRelease-2>", self.__r_cmd_click)

        self.empty = Image.new("RGBA", (grid_w, grid_h), bg)
        self.coords = {}

    def set_tk_img(self):
        img = ImageTk.PhotoImage(self.empty)
        self.configure(image=img)
        self.image_names = img

    def grid_paste(self, img, grid_x, grid_y, src):
        self.empty.paste(img, (grid_x, grid_y))

        coord = (grid_x // (cnf.thumbsize + cnf.thumbspad),
                 grid_y // (cnf.thumbsize + cnf.thumbspad))
        self.coords[coord] = src
        cnf.all_src.append(src)

    def __get_coords(self, e: tkinter.Event):
        try:
            clmn = e.x // (cnf.thumbsize + cnf.thumbspad)
            row = e.y // (cnf.thumbsize + cnf.thumbspad)
            return self.coords[(clmn, row)]
        except KeyError:
            return False

    def __click(self, e: tkinter.Event):
        img_src = self.__get_coords(e)
        if img_src:
            ImgViewer(img_src)

    def __r_cmd_click(self, e: tkinter.Event):
        img_src = self.__get_coords(e)
        if img_src:
            ContextAdvanced(e, img_src)

    def __r_click(self, e: tkinter.Event):
        img_src = self.__get_coords(e)
        if img_src:
            ContextThumbs(e, img_src)
        else:
            ContextFilter(e)


class Thumbs(CFrame):
    def __init__(self, master):
        super().__init__(master)

        self.notibar = NotifyBar(self)
        self.notibar.pack(fill="x", padx=15, pady=(5, 5))

        self.topbar = TopBar(self)
        self.topbar.bind("<ButtonRelease-2>", ContextFilter)
        self.topbar.pack(padx=15, fill="x")

        sep = CSep(self)
        sep.pack(fill="x", padx=1, pady=(10, 0))

        cnf.root.update_idletasks()

        self.resize_task = None
        cnf.root.bind("<Configure>", self.decect_resize)

        self.load_scroll()
        self.load_thumbs()
        self.bind_scroll_thumbs()

    def load_scroll(self):
        self.scroll_parrent = CFrame(self)
        self.scroll_parrent.pack(expand=1, fill="both")

        self.scroll = CScroll(self.scroll_parrent)
        self.scroll.pack(expand=1, fill="both")

        self.notibar.btn_up.uncmd()
        self.notibar.btn_up.cmd(self.scroll.moveup)

    def load_thumbs(self):
        thumbs_dict = ThumbsDict()

        if thumbs_dict:
            self.above_thumbsframe = AboveThumbs(self.scroll)
            self.above_thumbsframe.pack()
        else:
            self.above_thumbsframe = NoImages(self.scroll)
            self.above_thumbsframe.pack()
            for i in (self.scroll, self.above_thumbsframe):
                i.get_parrent().bind("<ButtonRelease-2>", ContextFilter)

        self.thumbs_frame = CFrame(self.scroll, width=10)
        self.thumbs_frame.pack(anchor="w", padx=5)
        self.thumbs_frame.bind("<ButtonRelease-2>", ContextFilter)

        grid_limit = 500
        self.clmns = self.get_clmns_count()
        grid_w = self.clmns * (cnf.thumbsize + cnf.thumbspad)

        for x, (date_key, img_list) in enumerate(thumbs_dict.items()):
            chunks = [
                img_list[i:i + grid_limit]
                for i in range(0, len(img_list), grid_limit)
                ]

            grid_title = ImgGridTitle(master=self.thumbs_frame,
                                      title=date_key,
                                      img_src_list=[i[1] for i in img_list])
            grid_title_pad = 30 if x != 0 else 15
            grid_title.pack(anchor="w", pady=(grid_title_pad, 0))

            for chunk in chunks:
                rows = math.ceil(len(chunk) / self.clmns)
                grid_h = rows * (cnf.thumbsize + cnf.thumbspad)
                grid_x, grid_y = 0, 0

                grid_img = ImgGrid(master=self.thumbs_frame,
                                   grid_w=grid_w, grid_h=grid_h)
                grid_img.pack(anchor="w")

                for img_num, (img_obj, img_src) in enumerate(chunk, 0):
                    grid_img.grid_paste(img=img_obj, grid_x=grid_x,
                                        grid_y=grid_y, src=img_src)

                    grid_x = grid_x + cnf.thumbsize + cnf.thumbspad

                    if (img_num + 1) % self.clmns == 0:
                        grid_y = grid_y + cnf.thumbsize + cnf.thumbspad
                        grid_x = 0

                grid_img.set_tk_img()

        ln_thumbs = len([item for val in thumbs_dict.values() for item in val])

        if ln_thumbs == cnf.limit:
            more_btn = CButton(self.thumbs_frame, text=cnf.lng.show_more)
            more_btn.cmd(lambda e: self.show_more_cmd())
            more_btn.pack(pady=15)

    def bind_scroll_thumbs(self):
        for i in (
            self.scroll_parrent, self.scroll, self.thumbs_frame,
            *self.thumbs_frame.winfo_children()
            ):
            self.scroll.set_scrolltag("thumbs_scroll", i.get_parrent())
        self.scroll.bind_autohide_scroll("thumbs_scroll")

    def show_more_cmd(self):
        cnf.limit += 150
        cnf.reload_thumbs()

    def decect_resize(self, e):
        if self.resize_task:
            cnf.root.after_cancel(self.resize_task)
        self.resize_task = cnf.root.after(500, self.thumbs_resize)

    def thumbs_resize(self):
        old_w = cnf.root_g["w"]
        new_w = cnf.root.winfo_width()

        if new_w != old_w:
            cnf.root_g["w"] = new_w

            if self.clmns != self.get_clmns_count():
                w, h = cnf.root.winfo_width(), cnf.root.winfo_height()
                cnf.root_g["w"], cnf.root_g["h"] = w, h
                cnf.root.update_idletasks()
                cnf.reload_thumbs()

    def reload_scroll(self):
        for i in (self.scroll_parrent, self.scroll):
            i.destroy()
        cnf.all_src.clear()
        self.topbar.filters.reload_filters()
        self.topbar.set_title()
        self.load_scroll()
        self.load_thumbs()
        self.bind_scroll_thumbs()
        cnf.root.focus_force()

    def reload_thumbs(self):
        for i in (self.above_thumbsframe, self.thumbs_frame):
            i.destroy()
        cnf.all_src.clear()
        self.load_thumbs()
        cnf.root.focus_force()

    def get_clmns_count(self):
        w = cnf.root.winfo_width() - cnf.menu_w - cnf.scroll_width
        return w // (cnf.thumbsize + cnf.thumbspad)
