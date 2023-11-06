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


__all__ = (
    "Thumbs",
    )


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


class ThumbsDict(dict):
    def __init__(self):
        super().__init__()
        data = Dbase.conn.execute(self.get_query()).fetchall()
        decoded = self.decode_thumbs(data)
        self.update(self.create_thumbs_dict(decoded))

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
        q = sqlalchemy.select(ThumbsMd.img150, ThumbsMd.src, ThumbsMd.modified)
        search = cnf.search_var.get()

        if search:
            search.replace("\n", "").strip()
            q = q.filter(ThumbsMd.src.like("%" + search + "%"))

        q = q.order_by(-ThumbsMd.modified)

        if cnf.curr_coll != cnf.all_colls:
            q = q.filter(ThumbsMd.collection == cnf.curr_coll)

        filters = []

        if cnf.filter["mod"]:
            filters.append(ThumbsMd.src.like("%" + cnf.models_name + "%"))

        if cnf.filter["cat"]:
            filters.append(ThumbsMd.src.like("%" + cnf.catalog_name + "%"))

        if cnf.filter["prod"]:
            tmp = sqlalchemy.and_(
                ThumbsMd.src.not_like("%" + cnf.catalog_name + "%"),
                ThumbsMd.src.not_like("%" + cnf.models_name + "%")
                )
            filters.append(tmp)

        q = q.filter(sqlalchemy.or_(*filters))

        if not any((cnf.start, cnf.end)):
            q = q.limit(cnf.limit)

        else:
            t = self.stamp_dates()
            q = q.filter(ThumbsMd.modified > t[0])
            q = q.filter(ThumbsMd.modified < t[1])

        return q
    

class SearchWid(RFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        fr = CFrame(self, bg=cnf.dgray_color)
        fr.pack(anchor="e", padx=1, pady=1)

        CLabel(fr, width=0, bg=cnf.dgray_color).pack(side="left", fill="y")

        self.search_wid = tkinter.Entry(
            fr,
            textvariable=cnf.search_var,
            bg=cnf.dgray_color,
            insertbackground="white",
            fg=cnf.fg_color,
            justify="left",
            border=0,
            highlightthickness=0,
            width=20,
            )
        self.search_wid.pack(side="left", fill="y")

        self.btn_clear = CButton(
            fr, text="⨂", width=3, fg_color=cnf.dgray_color, corner_radius=0,
            )
        self.btn_clear.pack(side="left", padx=(0, 5))
        self.btn_clear.cmd(self.search_clear)

        self.btn_search = CButton(
            fr, text="✓", width=3, fg_color=cnf.dgray_color, corner_radius=0,
            )
        self.btn_search.pack(side="left", padx=(0, 5))
        self.btn_search.cmd(self.search_go)

        self.search_wid.bind("<Escape>", lambda e: cnf.root.focus_force())
        cnf.root.bind("<Command-f>", lambda e: self.search_wid.focus_force())
        self.search_wid.bind("<Return>", self.search_go)
        self.search_wid.bind("<ButtonRelease-2>", ContextSearch)

    def search_go(self, e=None):
        cnf.search_var.set(self.search_wid.get())
        cnf.start, cnf.end = None, None
        cnf.reload_scroll()
        cnf.root.focus_force()

    def search_clear(self, e=None):
        cnf.search_var.set("")
        cnf.reload_scroll()


class FiltersWid(CFrame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        if not any(i for i in cnf.filter.values()):
            for i in cnf.filter.keys():
                cnf.filter[i] = True

        prod = CButton(self, text=cnf.lng.product)
        prod.pack(side="left", fill="x", padx=(0, 5))

        mod = CButton(self, text=cnf.lng.models)
        mod.pack(side="left", fill="x", padx=(0, 5))

        cat = CButton(self, text=cnf.lng.catalog)
        cat.pack(side="left", fill="x", padx=(0, 5))

        self.filter_btns = {cat: "cat", mod: "mod", prod: "prod"}

        for k, v in self.filter_btns.items():
            k.cmd(lambda e, v=v: self.filters_cmd(v))

        self.dates_btn = CButton(self, text=cnf.lng.dates)
        self.dates_btn.pack(side="left", fill="x", padx=(0, 5))
        self.dates_btn.cmd(lambda e: Filter())

        self.filters_configure()

    def filters_cmd(self, v):
        cnf.filter[v] = False if cnf.filter[v] else True
        cnf.reload_scroll()

    def filters_configure(self):
        for k, v in self.filter_btns.items():
            k: CButton
            t = k.cget("text").split()[0]
            if cnf.filter[v]:
                k.configure(fg_color=cnf.btn_color, text=t + " ⨂")
            else:
                k.configure(fg_color=cnf.bg_color, text=t + " ⨁")

        t = self.dates_btn.cget("text").split()[0]
        if any((cnf.start, cnf.end)):
            self.dates_btn.configure(fg_color=cnf.btn_color, text=t + " ⨂")
        else:
            self.dates_btn.configure(fg_color=cnf.bg_color, text=t + " ⨁")


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
    def __init__(self, master: tkinter):
        super().__init__(master)

        self.btn_up = CButton(self, text=f"▲", fg_color=cnf.bg_color)
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
            self.btn_up.configure(text=f"▲", fg_color=cnf.bg_color)
        except RuntimeError as e:
            print("thumbnails > can't configure topbar to default")
            print(e)


class ResetDatesBtn(CButton):
    def __init__(self, master: tkinter, text=cnf.lng.reset_dates, **kw):
        super().__init__(master, text=text, **kw)
        self.cmd(self.reset_dates_cmd)

    def reset_dates_cmd(self, e):
        cnf.start, cnf.end = None, None
        cnf.reload_scroll()


class NoImages(CFrame):
    def __init__(self, master: CScroll, *kw):
        super().__init__(master)

        str_var = cnf.search_var.get()
        noimg_t = cnf.lng.no_photo

        no_images = CLabel(
            master, text=noimg_t,
            font=("San Francisco Pro", 18, "bold")
            )
        no_images.pack(pady=(15, 0))

        reset = CButton(master)

        if str_var:
            noimg_t = (
                f"{cnf.lng.no_photo} {cnf.lng.with_name}"
                f"\n\"{str_var}\""
                )
            no_images.configure(text=noimg_t)
            reset.configure(text=cnf.lng.reset)
            reset.cmd(self.reset_search)
            reset.pack(pady=(15, 0))

        elif any((cnf.start, cnf.end)):
            noimg_t = (
                f"{cnf.lng.no_photo}"
                f"\n{cnf.named_start} - {cnf.named_end}"
                )
            no_images.configure(text=noimg_t)
            ResetDatesBtn(master).pack(pady=(15, 0))

        else:
            reset.configure(text=cnf.lng.show_all)
            reset.cmd(self.reset_filters)
            reset.pack(pady=(15, 0))

        for i in (master.get_parrent(),  no_images):
            i.bind("<ButtonRelease-2>", ContextFilter)

    def reset_filters(self, e):
        for k, v in cnf.filter.items():
            cnf.filter[k] = True
        cnf.reload_scroll()

    def reset_search(self, e):
        cnf.search_var.set("")
        cnf.reload_scroll()


class Thumbs(CFrame):
    def __init__(self, master):
        super().__init__(master)

        self.notibar = NotifyBar(self)
        self.notibar.pack(fill="x", padx=15, pady=(5, 5))

        self.topbar = TopBar(self)
        self.topbar.bind("<ButtonRelease-2>", ContextFilter)
        self.topbar.pack(padx=15, fill="x")

        sep = CSep(self)
        sep.pack(fill="x", pady=(5, 0), padx=1)

        self.clmns_count = 1
        self.thumbs_pad = 3
        self.thumbsize = cnf.thumb_size + self.thumbs_pad

        cnf.root.update_idletasks()

        self.resize_task = None
        cnf.root.bind("<Configure>", self.decect_resize)

        self.load_scroll()
        self.load_thumbs()

    def load_scroll(self):
        self.scroll_parrent = CFrame(self)
        self.scroll_parrent.pack(expand=1, fill="both")

        self.scroll = CScroll(self.scroll_parrent)
        self.scroll.pack(expand=1, fill="both")
        self.scroll.bind("<Enter>", lambda e: self.scroll.focus_force())

        self.notibar.btn_up.uncmd()
        self.notibar.btn_up.cmd(self.scroll.moveup)

    def load_thumbs(self):
        thumbs_dict = ThumbsDict()

        self.thumbs_frame = CFrame(self.scroll)
        self.thumbs_frame.pack(anchor="w", padx=(0, 15))
        self.thumbs_frame.bind("<ButtonRelease-2>", ContextFilter)

        if any((cnf.start, cnf.end)) and thumbs_dict:
            ResetDatesBtn(self.thumbs_frame).pack(pady=(15, 0))

        all_src = []
        limit = 500
        self.clmns_count = self.get_clmns_count()
        w = self.thumbsize*self.clmns_count

        for x, (date_key, img_list) in enumerate(thumbs_dict.items()):
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
            pad = 30 if x != 0 else 15
            chunk_title.pack(anchor="w", pady=(pad, 0), padx=self.thumbs_pad)

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
                img_lbl = CLabel(self.thumbs_frame, image=img, anchor="w")
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


        ln_thumbs = sum(len(i) for i in list(thumbs_dict.values()))

        if not thumbs_dict:
            NoImages(self.scroll).pack()

        elif thumbs_dict and ln_thumbs == cnf.limit:
            more_btn = CButton(self.thumbs_frame, text=cnf.lng.show_more)
            more_btn.cmd(lambda e: self.show_more_cmd())
            more_btn.pack(pady=(15, 0))

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

            if self.clmns_count != self.get_clmns_count():
                w, h = cnf.root.winfo_width(), cnf.root.winfo_height()
                cnf.root_g["w"], cnf.root_g["h"] = w, h
                cnf.root.update_idletasks()
                cnf.reload_thumbs()

    def reload_scroll(self):
        for i in (self.scroll_parrent, self.scroll):
            i.destroy()
        self.topbar.filters.filters_configure()
        self.topbar.set_title()
        self.load_scroll()
        self.load_thumbs()

    def reload_thumbs(self):
        self.thumbs_frame.destroy()
        self.load_thumbs()

    def get_clmns_count(self):
        padx = self.thumbs_frame.pack_info()["padx"][1]*2
        clmns = (cnf.root.winfo_width()-cnf.menu_w-padx)//(self.thumbsize)
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
