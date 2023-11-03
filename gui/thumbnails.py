import math
import tkinter
import traceback
from datetime import datetime
from functools import partial

import sqlalchemy
import tkmacosx
from PIL import Image, ImageTk

from cfg import cnf
from database import Dbase, Thumbs

from .filter import Filter
from .img_viewer import ImgViewer
from .utils import *
from .widgets import *

__all__ = (
    "Thumbnails",
    )


class ThumbsPrepare:
    def decode_thumbs(self, thumbs_raw):
        result = []
        for blob, src, modified in thumbs_raw:
            try:
                decoded = decode_image(blob)
                cropped = crop_image(decoded)
                img = convert_to_rgb(cropped)
                result.append((img, src, modified))

            except Exception:
                print(traceback.format_exc())

        return result

    def create_thumbs_dict(self, thumbs_raw):
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
        q = sqlalchemy.select(Thumbs.img150, Thumbs.src, Thumbs.modified)
        search = cnf.search_var.get()

        if search:
            search.replace("\n", "").strip()
            q = q.filter(Thumbs.src.like("%" + search + "%"))

        q = q.order_by(-Thumbs.modified)

        if cnf.curr_coll != cnf.all_colls:
            q = q.filter(Thumbs.collection == cnf.curr_coll)

        filters = []

        if cnf.filter["mod"]:
            filters.append(Thumbs.src.like("%" + cnf.models_name + "%"))

        if cnf.filter["cat"]:
            filters.append(Thumbs.src.like("%" + cnf.catalog_name + "%"))

        if cnf.filter["prod"]:
            tmp = sqlalchemy.and_(
                Thumbs.src.not_like("%" + cnf.catalog_name + "%"),
                Thumbs.src.not_like("%" + cnf.models_name + "%")
                )
            filters.append(tmp)

        q = q.filter(sqlalchemy.or_(*filters))

        if not any((cnf.start, cnf.end)):
            q = q.limit(cnf.limit)

        else:
            t = self.stamp_dates()
            q = q.filter(Thumbs.modified > t[0])
            q = q.filter(Thumbs.modified < t[1])

        return q
    

class ContextFilter(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()

        self.apply_filter(e, label=cnf.lng.product, filter="prod")
        self.apply_filter(e, label=cnf.lng.models, filter="mod")
        self.apply_filter(e, label=cnf.lng.catalog, filter="cat")
        self.apply_filter(e, label=cnf.lng.show_all, filter="all")

        self.do_popup(e)


class ContextTitles(Context):
    def __init__(self, e: tkinter.Event, title, paths_list):
        super().__init__()

        if cnf.first_load:
            self.please_wait()

        else:
            self.download_group(title, paths_list)

            self.sep()
            self.download_group_tiffs(title, paths_list)

            self.sep()
            self.download_group_fullsize(title, paths_list)

        self.do_popup(e)


class ContextAdvanced(Context):
    def __init__(self, e: tkinter.Event, img_src):
        super().__init__()
        self.db_remove_img(img_src)
        self.do_popup(e)


class ContextThumbs(Context):
    def __init__(self, e: tkinter.Event, img_src, all_src):
        super().__init__()

        if cnf.first_load:
            self.please_wait()

        else:
            self.imgview(img_src, all_src)
            self.imginfo(e.widget.winfo_toplevel(), img_src)

            self.sep()
            self.copy_jpg_path(img_src)
            self.reveal_jpg(img_src)
            self.download_onefile(img_src)

            self.sep()
            self.copy_tiffs_paths(img_src)
            self.reveal_tiffs(img_src)
            self.download_tiffs(img_src)

            self.sep()
            self.download_fullsize(img_src)

        self.do_popup(e)


class ContextSearch(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.clear()
        self.pastesearch()
        self.do_popup(e)


class ThumbsSearch(CFrame):
    def __init__(self, master: tkinter):
        super().__init__(master, bg="red")

        fr = CFrame(self)
        fr.pack(anchor="e")

        CLabel(
            fr, width=1, bg=cnf.dgray_color).pack(side="left", fill="y")

        self.search_wid = tkinter.Entry(
            fr,
            textvariable=cnf.search_var,
            bg=cnf.dgray_color,
            insertbackground="white",
            fg=cnf.blue_color,
            justify="left",
            border=0,
            highlightthickness=0,
            width=12
            )
        self.search_wid.pack(ipady=6, side="left")

        self.btn_clear = CButton(
            fr, text="⌫", width=3, bg=cnf.dgray_color, pady=5)
        self.btn_clear.pack(side="left")
        self.btn_clear.cmd(self.search_clear)

        self.btn_search = CButton(
            fr, text="✓", width=3, bg=cnf.dgray_color, pady=5)
        self.btn_search.pack(side="left")
        self.btn_search.cmd(self.search_go)

        self.search_wid.bind("<Escape>", lambda e: cnf.root.focus_force())
        cnf.root.bind("<Command-f>", lambda e: self.search_wid.focus_force())
        self.search_wid.bind("<Return>", self.search_go)
        self.search_wid.bind("<ButtonRelease-2>", ContextSearch)

    def search_go(self, e=None):
        cnf.search_var.set(self.search_wid.get())
        cnf.start, cnf.end = None, None
        cnf.reload_scroll()

    def search_clear(self, e=None):
        cnf.search_var.set("")
        cnf.reload_scroll()


class FilterRow(CFrame):
    def __init__(self, master: tkinter):
        super().__init__(master)

        if not any(i for i in cnf.filter.values()):
            for i in cnf.filter.keys():
                cnf.filter[i] = True

        prod = CButton(self, text=cnf.lng.product)
        prod.pack(side="left", fill="x")

        CSep(self).pack(side="left", fill="y", padx=5)

        mod = CButton(self, text=cnf.lng.models)
        mod.pack(side="left", fill="x")

        CSep(self).pack(side="left", fill="y", padx=5)

        cat = CButton(self, text=cnf.lng.catalog)
        cat.pack(side="left", fill="x")

        CSep(self).pack(side="left", fill="y", padx=5)

        filter = CButton(
            self, text=cnf.lng.dates, bg=cnf.bg_color, width=7)
        filter.cmd(lambda e: Filter())
        filter.pack(side="left", fill="x")

        if any((cnf.start, cnf.end)):
            filter.configure(bg=cnf.btn_color)

        btns = {"prod": prod, "mod": mod, "cat": cat}

        for k, v in btns.items():
            v.configure(width=7, bg=cnf.bg_color)
            v.configure(bg=cnf.btn_color) if cnf.filter[k] else None
            v.cmd(lambda e, k=k: self.filtr_cmd(k))

    def filtr_cmd(self, key):
        cnf.filter[key] = False if cnf.filter[key] else True
        cnf.reload_scroll()


class TitleRow(CFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        if cnf.curr_coll == cnf.all_colls:
            coll_title = cnf.lng.all_colls
        else:
            coll_title = cnf.curr_coll

        title = CButton(
            self, text=coll_title, bg=cnf.bg_color, anchor="w", justify="left",
            font=("San Francisco Pro", 22, "bold"))
        title.grid(column=0, row=0, sticky="w")

        self.filters = FilterRow(self)
        self.filters.grid(column=1, row=0)

        search = ThumbsSearch(self)
        search.rowconfigure(0, weight=1)
        search.columnconfigure(2, weight=1)
        search.grid(column=2, row=0, sticky="e")

        self.columnconfigure(tuple(range(2)), weight=1)
        self.rowconfigure(tuple(range(1)), weight=1)

        self.bind("<Configure>", self.min)
        self.small = False

    def min(self, e: tkinter.Event):
        if not self.small:
            if e.width < 670:
                print("small")
                self.small = True
                self.filters.grid(row=1, column=0, sticky="nesw")
                self.rowconfigure(1, weight=1)

        elif self.small and e.width > 670:
            print("big")
            self.small = False
            self.filters.grid(row=0, column=1, sticky="nesw")


class Thumbnails(CFrame, ThumbsPrepare):
    def __init__(self, master):
        super().__init__(master)
        self.topbar_frame = CFrame(self)
        self.topbar_frame.pack(fill="x")

        self.topbar = CButton(
            self.topbar_frame, text=f"▲",
            font=("San Francisco Pro", 13, "normal"),
            bg=cnf.bg_color, pady=1,
            )
        self.topbar.pack(
            pady=(5, 0), side="left", fill="x", expand=1, padx=(5, 0))
        self.topbar.cmd(lambda e: self.sframe["canvas"].yview_moveto("0.0"))

        self.clmns_count = 1
        self.thumbs_pad = 3
        self.thumbsize = cnf.thumb_size + self.thumbs_pad

        cnf.root.update_idletasks()

        self.load_scroll()
        self.load_thumbs()

        cnf.root.bind("<Configure>", self.decect_resize)
        self.resize_task = None
        self.search_task = None

    def load_scroll(self):
        self.titles = TitleRow(self)
        self.titles.bind("<ButtonRelease-2>", ContextFilter)
        self.titles.pack(padx=(15, 15), fill="x")

        self.title_sep = CSep(self)
        self.title_sep.pack(fill="x", pady=(5, 0), padx=1)

        self.scroll_frame = CFrame(self)
        self.scroll_frame.pack(expand=1, fill=tkinter.BOTH)

        self.sframe = tkmacosx.SFrame(
            self.scroll_frame, bg=cnf.bg_color, scrollbarwidth=1)
        self.sframe.pack(expand=1, fill=tkinter.BOTH, padx=(15, 0))

    def load_thumbs(self):
        self.clmns_count = self.get_clmns_count()

        thumbs_dict = Dbase.conn.execute(self.get_query()).fetchall()
        thumbs_dict = self.decode_thumbs(thumbs_dict)
        thumbs_dict = self.create_thumbs_dict(thumbs_dict)

        scrl_w = self.sframe.cget("scrollbarwidth")
        self.thumbs_frame = CFrame(
            self.sframe, width=(self.thumbsize) * self.clmns_count)
        self.thumbs_frame.pack(expand=1, anchor="w", padx=(scrl_w, 10-scrl_w))
        self.thumbs_frame.bind("<ButtonRelease-2>", ContextFilter)

        all_src = []
        limit = 500
        w = self.thumbsize*self.clmns_count

        for date_key, img_list in thumbs_dict.items():
            chunks = [
                img_list[i:i+limit]
                for i in range(0, len(img_list), limit)
                ]

            chunk_t = f"{date_key}, {cnf.lng.total}: {len(img_list)}"
            if cnf.search_var.get():
                chunk_t = (
                    f"{cnf.lng.photo} {cnf.lng.with_name} "
                    f"\"{cnf.search_var.get()}\"\n{chunk_t}"
                    )

            chunk_title = CLabel(
                self.thumbs_frame, text=chunk_t, anchor="w", justify="left",
                font=("San Francisco Pro", 18, "bold")
                )
            chunk_title.pack(anchor="w", pady=(30, 0))

            chunk_title.bind(
                "<ButtonRelease-2>", (
                    lambda e, title=date_key,
                    paths_list=[i[1] for i in img_list]: 
                    ContextTitles(e, title, paths_list)
                    ))

            for chunk in chunks:

                chunk_ln = len(chunk)
                rows = math.ceil(chunk_ln/self.clmns_count)
                
                h = (self.thumbsize) * rows

                empty = Image.new("RGBA", (w, h), color=cnf.bg_color)
                row, clmn = 0, 0
                coords = {}

                for x, (img, src) in enumerate(chunk, 1):

                    all_src.append(src)

                    coord = (clmn//(self.thumbsize), row//(self.thumbsize))
                    coords[coord] = src

                    empty.paste(img, (clmn, row))

                    clmn += (self.thumbsize)
                    if x % self.clmns_count == 0:
                        row += (self.thumbsize)
                        clmn = 0

                img = ImageTk.PhotoImage(empty)
                img_lbl = CLabel(self.thumbs_frame, image=img)
                img_lbl.pack(anchor="w")
                img_lbl.image_names = img

                img_lbl.bind("<ButtonRelease-1>", (
                    lambda e, all_src=all_src, coords=coords:
                    self.click(e, all_src, coords)
                    ))

                img_lbl.bind("<ButtonRelease-2>", (
                    lambda e, all_src=all_src, coords=coords:
                    self.r_click(e, all_src, coords)
                    ))

                img_lbl.bind("<Command-ButtonRelease-2>", (
                    lambda e, coords=coords: self.r_cmd_click(e, coords)
                    ))

        if not thumbs_dict:
            self.thumbs_frame.pack(anchor="center")
        
            str_var = cnf.search_var.get()
            noimg_t = cnf.lng.no_photo

            if str_var:
                noimg_t = (
                    f"{cnf.lng.no_photo} {cnf.lng.with_name}"
                    f"\n\"{str_var}\""
                    )

            elif any((cnf.start, cnf.end)):
                noimg_t=(
                    f"{cnf.lng.no_photo}"
                    f"\n{cnf.named_start} - {cnf.named_end}"
                    )

            no_images = CLabel(
                self.thumbs_frame, text=noimg_t,
                font=("San Francisco Pro", 18, "bold")
                )
            no_images.pack(pady=(15, 0))

        more_btn = CButton(self.thumbs_frame, text=cnf.lng.show_more)
        more_btn.cmd(lambda e: self.show_more_cmd())
        more_btn.pack(pady=(15, 0))

    def show_more_cmd(self):
        cnf.limit += 150
        cnf.reload_thumbs()

    def decect_resize(self, e):
        if self.resize_task:
            cnf.root.after_cancel(self.resize_task)
        self.resize_task = cnf.root.after(500, self.frame_resize)

    def frame_resize(self):
        old_w = cnf.root_g["w"]
        new_w = cnf.root.winfo_width()

        if new_w != old_w:
            cnf.root_g["w"] = new_w

            if self.clmns_count != self.get_clmns_count():
                w, h = cnf.root.winfo_width(), cnf.root.winfo_height()
                cnf.root_g["w"], cnf.root_g["h"] = w, h
                cnf.root.update_idletasks()
                cnf.reload_thumbs()

    def reload_scroll(self):
        for i in (
            self.titles, self.scroll_frame, self.thumbs_frame, self.title_sep):
            i.destroy()
        self.load_scroll()
        self.load_thumbs()

    def reload_thumbs(self):
        self.thumbs_frame.destroy()
        self.load_thumbs()

    def get_clmns_count(self):
        clmns = (cnf.root_g["w"] - cnf.menu_w) // (cnf.thumb_size)
        return 1 if clmns == 0 else clmns

    def get_coords(self, e: tkinter.Event, coords: dict):
        try:
            clmn, row = e.x//(self.thumbsize), e.y//(self.thumbsize)
            return coords[(clmn, row)]
        except KeyError:
            return False

    def click(self, e: tkinter.Event, all_src: list, coords: dict):
        img_src = self.get_coords(e, coords)
        if img_src:
            ImgViewer(img_src, all_src)

    def r_cmd_click(self, e: tkinter.Event, coords):
        img_src = self.get_coords(e, coords)
        if img_src:
            ContextAdvanced(e, img_src)

    def r_click(self, e: tkinter.Event, all_src: list, coords: dict):
        img_src = self.get_coords(e, coords)
        if img_src:
            ContextThumbs(e, img_src, all_src)
        else:
            ContextFilter(e)

    def topbar_text(self, text):
        try:
            self.topbar.configure(text=text, bg=cnf.blue_color)

            if len(self.topbar_frame.children) < 2:

                self.topbar_can = CButton(
                    self.topbar_frame, text=cnf.lng.cancel, bg=cnf.blue_color,
                    pady=1
                    )
                self.topbar_can.configure()
                self.topbar_can.cmd(lambda e: cancel_utils_task())
                self.topbar_can.pack(
                    side="left",
                    pady=(5, 0), padx=(1, 5)
                    )

        except RuntimeError as e:
            print("thumbnails > topbar text error")
            print(e)


    def topbar_default(self):
        try:
            self.topbar_can.destroy()
        except AttributeError as e:
            print("thumbnails > no topbar cancel button")
            print(e)

        try:
            self.topbar.configure(text=f"▲", bg=cnf.bg_color)
        except RuntimeError as e:
            print("thumbnails > can't configure topbar to default")
            print(e)