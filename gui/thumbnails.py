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


class ContextFilter(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()

        self.apply_filter(e, cnf.lng.product)
        self.apply_filter(e, cnf.lng.models)
        self.apply_filter(e, cnf.lng.catalog)
        self.apply_filter(e, cnf.lng.show_all)

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
        super().__init__(master)

        self.search_wid = tkinter.Entry(
            self,
            textvariable=cnf.search_var,
            bg=cnf.dgray_color,
            insertbackground="white",
            fg=cnf.fg_color,
            justify="center",
            selectbackground=cnf.btn_color,
            border=1,
            highlightthickness=0,
            )
        self.search_wid.pack(fill="x", ipady=2, ipadx=2)

        btns_frame = CFrame(self)
        btns_frame.pack(pady=(10, 0))

        self.btn_search = CButton(btns_frame, text=cnf.lng.search)
        self.btn_search.pack(side="left")
        self.btn_search.cmd(self.search_go)

        CSep(btns_frame).pack(fill="y", side="left", padx=10)

        if cnf.search_var.get():
            self.btn_search.configure(bg=cnf.blue_color)

        self.btn_clear = CButton(btns_frame, text=cnf.lng.clear)
        self.btn_clear.pack(side="left")
        self.btn_clear.cmd(self.search_clear)

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

        if cnf.sort_modified:
            q = q.order_by(-Thumbs.modified)
        else:
            q = q.order_by(-Thumbs.created)

        if cnf.curr_coll != cnf.all_colls:
            q = q.filter(Thumbs.collection == cnf.curr_coll)

        filters = []

        if cnf.models:
            filters.append(Thumbs.src.like("%" + cnf.models_name + "%"))

        if cnf.catalog:
            filters.append(Thumbs.src.like("%" + cnf.catalog_name + "%"))

        if cnf.product:
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
        self.topbar.pack(pady=(5, 0), side="left", fill="x", expand=1)
        self.topbar.cmd(lambda e: self.sframe["canvas"].yview_moveto("0.0"))

        CSep(self).pack(fill="x", pady=5)

        self.clmns_count = 1
        self.thumbsize = cnf.thumb_size + 3

        cnf.root.update_idletasks()

        self.load_scroll()
        self.load_thumbs()

        cnf.root.bind("<Configure>", self.decect_resize)
        self.resize_task = None
        self.search_task = None

    def load_scroll(self):
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

        self.thumbs_frame = CFrame(self.sframe)
        self.thumbs_frame.pack(
            expand=1,
            fill=tkinter.BOTH,
            padx=(self.sframe.cget("scrollbarwidth"), 0)
            )

        if cnf.curr_coll == cnf.all_colls:
            coll_title = cnf.lng.all_colls
        else:
            coll_title = cnf.curr_coll

        title = CLabel(
            self.thumbs_frame, text=coll_title, width=30,
            font=("San Francisco Pro", 24, "bold")
            )
        title.pack(anchor="center")

        filtr_fr = CFrame(self.thumbs_frame)
        filtr_fr.pack()

        filtr_l = CLabel(
            filtr_fr, font=("San Francisco Pro", 13, "normal"),
            justify="right", anchor="e", width=20,
            text=(
                f"{cnf.lng.filter}"
                f"\n{cnf.lng.sort}"
                ),
                )
        filtr_l.pack(side="left")

        filter_row = []
        if cnf.product:
            filter_row.append(cnf.lng.product)
        if cnf.models:
            filter_row.append(cnf.lng.models)
        if cnf.catalog:
            filter_row.append(cnf.lng.catalog)
        filter_row = ", ".join(filter_row)

        if cnf.sort_modified:
            sort_text = cnf.lng.date_changed_by
        else:
            sort_text = cnf.lng.date_created_by

        filtr_r = CLabel(
            filtr_fr, font=("San Francisco Pro", 13, "normal"),
            justify="left", anchor="w", width=20,
            text=(
                f"{filter_row}"
                f"\n{sort_text}"
                ),
                )
        filtr_r.pack(side="right")

        for i in (self.thumbs_frame, title, filtr_l, filtr_r):
            i.bind("<ButtonRelease-2>", ContextFilter)

        btn_filter = CButton(self.thumbs_frame, text=cnf.lng.filters)
        btn_filter.pack(pady=(10, 0))
        if any((cnf.start, cnf.end)):
            btn_filter.configure(bg=cnf.blue_color)
        btn_filter.cmd(lambda e: Filter())

        search = ThumbsSearch(self.thumbs_frame)
        search.pack(pady=(10, 0))

        all_src = []
        limit = 500

        for date_key, img_list in thumbs_dict.items():
            chunks = [
                img_list[i:i+limit]
                for i in range(0, len(img_list), limit)
                ]

            chunk_title = CLabel(
                self.thumbs_frame,
                text=f"{date_key}, {cnf.lng.total}: {len(img_list)}",
                font=("San Francisco Pro", 18, "bold"),
                )
            chunk_title.pack(anchor="w", pady=(30, 0), padx=2)

            chunk_title.bind(
                "<ButtonRelease-2>", (
                    lambda e, title=date_key,
                    paths_list=[i[1] for i in img_list]: 
                    ContextTitles(e, title, paths_list)
                    ))

            for chunk in chunks:

                chunk_ln = len(chunk)
                rows = math.ceil(chunk_ln/self.clmns_count)

                w = (self.thumbsize) * self.clmns_count
                h = (self.thumbsize) * rows

                empty = Image.new("RGBA", (w, h), color=cnf.bg_color)
                row, clmn = 0, 0
                coords = {}

                for x, (img, src) in enumerate(chunk, 1):

                    all_src.append(src)

                    coord = (clmn//(self.thumbsize), row//(self.thumbsize))
                    coords[coord] = src

                    # img = img.resize((146, 146))
                    # framed = Image.new("RGBA", (150, 150), color='#ffffff')
                    # framed.paste(img, (2, 2))
                    # img = framed

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
        self.scroll_frame.destroy()
        self.thumbs_frame.destroy()
        self.load_scroll()
        self.load_thumbs()

    def reload_thumbs(self):
        self.thumbs_frame.destroy()
        self.load_thumbs()

    def get_clmns_count(self):
        clmns = (cnf.root_g["w"] - cnf.menu_w) // (cnf.thumb_size-3)
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
                    pady=(5, 0), padx=(1, 0)
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