import math
import tkinter
import traceback
from datetime import datetime

import sqlalchemy
import tkmacosx
from PIL import Image, ImageTk

from cfg import cnf
from database import Dbase, Thumbs

from .filter import Filter
from .globals import Globals
from .img_viewer import ImgViewer
from .utils import *
from .widgets import *

__all__ = (
    "Thumbnails",
    )


class ContextTitles(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()

        if cnf.first_load:
            self.please_wait()

        else:
            self.download_group(e)

            self.sep()
            self.download_group_tiffs(e)

            self.sep()
            self.download_group_fullsize(e)

        self.do_popup(e)


class ContextAdvanced(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.db_remove_img(e)
        self.do_popup(e)


class ContextThumbs(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()

        if cnf.first_load:
            self.please_wait()

        else:
            self.imgview(e)
            self.imginfo(e)

            self.sep()
            self.copy_jpg_path(e)
            self.reveal_jpg(e)
            self.download_onefile(e)

            self.sep()
            self.copy_tiffs_paths(e)
            self.reveal_tiffs(e)
            self.download_tiffs(e)

            self.sep()
            self.download_fullsize(e)

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
            textvariable=Globals.search_var,
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

        if Globals.search_var.get():
            self.btn_search.configure(bg=cnf.blue_color)

        self.btn_clear = CButton(btns_frame, text=cnf.lng.clear)
        self.btn_clear.pack(side="left")
        self.btn_clear.cmd(self.search_clear)

        self.search_wid.bind("<Escape>", lambda e: cnf.root.focus_force())
        cnf.root.bind("<Command-f>", lambda e: self.search_wid.focus_force())
        self.search_wid.bind("<Return>", self.search_go)
        self.search_wid.bind("<ButtonRelease-2>", ContextSearch)

    def search_go(self, e=None):
        Globals.search_var.set(self.search_wid.get())
        Globals.start, Globals.end = None, None
        Globals.reload_scroll()

    def search_clear(self, e=None):
        Globals.search_var.set("")
        Globals.reload_scroll()


class ThumbsPrepare:
    def thumbs_prepare(self):
        self.thumbs_lbls = Dbase.conn.execute(self.get_query()).fetchall()
        self.thumbs_lbls = self.decode_thumbs()
        self.thumbs_lbls = self.create_thumbs_dict()

        self.thumb_size = cnf.thumb_size + cnf.thumb_pad

        if cnf.curr_coll == cnf.all_colls:
            self.coll_title = cnf.lng.all_colls
        else:
            self.coll_title = cnf.curr_coll

        filter_row = []

        if cnf.product:
            filter_row.append(cnf.lng.product)
        if cnf.models:
            filter_row.append(cnf.lng.models)
        if cnf.catalog:
            filter_row.append(cnf.lng.catalog)

        filter_row = ", ".join(filter_row)
        self.filter_row = filter_row.lower().capitalize()

        if cnf.sort_modified:
            self.sort_text = cnf.lng.date_changed_by
        else:
            self.sort_text = cnf.lng.date_created_by

    def decode_thumbs(self):
        result = []
        for blob, src, modified in self.thumbs_lbls:
            try:
                decoded = decode_image(blob)
                cropped = crop_image(decoded)
                img = convert_to_rgb(cropped)
                result.append((img, src, modified))

            except Exception:
                print(traceback.format_exc())

        return result

    def create_thumbs_dict(self):
        thumbs_dict = {}

        for img, src, modified in self.thumbs_lbls:
            date_key = datetime.fromtimestamp(modified).date()

            if not any((Globals.start, Globals.end)):
                date_key = f"{cnf.lng.months[date_key.month]} {date_key.year}"
            else:
                date_key = f"{Globals.named_start} - {Globals.named_end}"

            thumbs_dict.setdefault(date_key, [])
            thumbs_dict[date_key].append((img, src))

        return thumbs_dict

    def stamp_dates(self):
        start = datetime.combine(Globals.start, datetime.min.time())
        end = datetime.combine(
            Globals.end, datetime.max.time().replace(microsecond=0)
            )
        return (datetime.timestamp(start), datetime.timestamp(end))

    def get_query(self):
        q = sqlalchemy.select(Thumbs.img150, Thumbs.src, Thumbs.modified)
        search = Globals.search_var.get()

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

        if not any((Globals.start, Globals.end)):
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

        self.topbar = CButton(self.topbar_frame, text=f"▲")
        self.topbar.configure(
            font=('San Francisco Pro', 13, 'normal'),
            bg=cnf.bg_color,
            pady=1,
            )
        self.topbar.pack(pady=(5, 0), side="left", fill="x", expand=1)
        self.topbar.cmd(self.scroll_up)

        sep = CSep(self)
        sep.pack(fill="x", pady=5)

        self.clmns_count = 1

        cnf.root.update_idletasks()

        self.load_scroll()
        self.load_thumbs()

        cnf.root.bind('<Configure>', self.decect_resize)
        self.resize_task = None
        self.search_task = None

        Globals.reload_scroll = self.reload_scroll
        Globals.reload_thumbs = self.reload_thumbs
        Globals.topbar_text = self.topbar_text
        Globals.topbar_default = self.topbar_default

    def load_scroll(self):
        self.scroll_frame = CFrame(self)
        self.scroll_frame.pack(expand=1, fill=tkinter.BOTH)

        self.sframe = tkmacosx.SFrame(
            self.scroll_frame, bg=cnf.bg_color, scrollbarwidth=7)
        self.sframe.pack(expand=1, fill=tkinter.BOTH)

    def load_thumbs(self):
        self.thumbs_prepare()
        self.clmns_count = self.get_clmns_count()

        self.thumbs_frame = CFrame(self.sframe)
        # тут пустое место как я понимаю, для контекста

        title = CLabel(self.thumbs_frame, text=self.coll_title, width=30)
        title.configure(font=('San Francisco Pro', 30, 'bold'))
        title.pack(anchor="center")

        filtr_fr = CFrame(self.thumbs_frame)
        filtr_fr.pack()

        filtr_l = CLabel(filtr_fr)
        filtr_l.configure(
            text=(
                f"{cnf.lng.filter}"
                f"\n{cnf.lng.sort}"
                ),
            font=('San Francisco Pro', 13, 'normal'),
            justify="right",
            anchor="e",
            width=20,
            )
        filtr_l.pack(side="left")

        filtr_r = CLabel(filtr_fr)
        filtr_r.configure(
            text=(
                f"{self.filter_row}"
                f"\n{self.sort_text}"
                ),
            font=('San Francisco Pro', 13, 'normal'),
            justify="left",
            anchor="w",
            width=20
            )
        filtr_r.pack(side="right")

        btn_filter = CButton(self.thumbs_frame, text=cnf.lng.filters)
        btn_filter.pack(pady=(10, 0))
        if any((Globals.start, Globals.end)):
            btn_filter.configure(bg=cnf.blue_color)
        btn_filter.cmd(lambda e: Filter())

        search = ThumbsSearch(self.thumbs_frame)
        search.pack(pady=(10, 0))

        all_src = []
        limit = 500

        for date_key, img_list in self.thumbs_lbls.items():
            chunks = [
                img_list[i:i+limit]
                for i in range(0, len(img_list), limit)
                ]

            t = f"{date_key}, {cnf.lng.total}: {len(img_list)}"
            chunk_title = CLabel(self.thumbs_frame, text=t)
            chunk_title.configure(font=('San Francisco Pro', 18, 'bold'))
            chunk_title.pack(anchor="w", pady=(30, 0), padx=2)

            chunk_title.title = date_key
            chunk_title.paths_list = [i[1] for i in img_list]
            chunk_title.bind("<ButtonRelease-2>", ContextTitles)

            for chunk in chunks:

                chunk_ln = len(chunk)
                rows = math.ceil(chunk_ln/self.clmns_count)

                w = self.thumb_size * self.clmns_count
                h = self.thumb_size * rows

                empty = Image.new("RGBA", (w, h), color=cnf.bg_color)
                row, clmn = 0, 0
                coords = {}

                for x, (img, src) in enumerate(chunk, 1):

                    all_src.append(src)

                    coord = (clmn//self.thumb_size, row//self.thumb_size)
                    coords[coord] = src

                    empty.paste(img, (clmn, row))

                    clmn += self.thumb_size
                    if x % self.clmns_count == 0:
                        row += self.thumb_size
                        clmn = 0

                img = ImageTk.PhotoImage(empty)
                img_lbl = CLabel(self.thumbs_frame, image=img)
                img_lbl.pack(anchor="w")
                img_lbl.image_names = img

                img_lbl.coords = coords
                img_lbl.all_src = all_src

                img_lbl.bind('<ButtonRelease-1>', self.click)
                img_lbl.bind("<ButtonRelease-2>", self.r_click)
                img_lbl.bind("<Command-ButtonRelease-2>", self.r_cmd_click)

        if not self.thumbs_lbls:
            str_var = Globals.search_var.get()

            noimg_t = cnf.lng.no_photo

            if str_var:
                noimg_t = (
                    f"{cnf.lng.no_photo} {cnf.lng.with_name}"
                    f"\n\"{str_var}\""
                    )

            elif any((Globals.start, Globals.end)):
                noimg_t=(
                    f"{cnf.lng.no_photo}"
                    f"\n{Globals.named_start} - {Globals.named_end}"
                    )

            no_images = CLabel(self.thumbs_frame, text=noimg_t)
            no_images.configure(font=('San Francisco Pro', 18, 'bold'))
            no_images.pack(pady=(15, 0))

        more_btn = CButton(
            self.thumbs_frame,
            text=cnf.lng.show_more
            )
        more_btn.cmd(lambda e: self.show_more_cmd())
        more_btn.pack(pady=(15, 0))

        self.thumbs_frame.pack(
            expand=1,
            fill=tkinter.BOTH,
            padx=(self.sframe["scrollbarwidth"], 0)
            )

    def show_more_cmd(self):
        cnf.limit += 150
        Globals.reload_thumbs()

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
                Globals.reload_thumbs()

    def reload_scroll(self):
        self.scroll_frame.destroy()
        self.thumbs_frame.destroy()
        self.load_scroll()
        self.load_thumbs()

    def reload_thumbs(self):
        self.thumbs_frame.destroy()
        self.load_thumbs()

    def get_clmns_count(self):
        clmns = (cnf.root_g["w"] - cnf.menu_w) // cnf.thumb_size
        return 1 if clmns == 0 else clmns

    def get_coords(self, e: tkinter.Event):
        try:
            clmn, row = e.x//self.thumb_size, e.y//self.thumb_size
            e.widget.src = e.widget.coords[(clmn, row)]
            return True

        except KeyError:
            return False

    def click(self, e: tkinter.Event):
        if self.get_coords(e):
            ImgViewer(e.widget.src, e.widget.all_src)

    def r_cmd_click(self, e: tkinter.Event):
        if self.get_coords(e):
            # print(e.widget.src)
            ContextAdvanced(e)

    def r_click(self, e: tkinter.Event):
        if self.get_coords(e):
            ContextThumbs(e)

    def scroll_up(self, e=None):
        self.sframe['canvas'].yview_moveto('0.0')

    def topbar_text(self, text):
        try:
            self.topbar.configure(text=text, bg=cnf.blue_color)

            if len(self.topbar_frame.children) < 2:

                self.topbar_can = CButton(self.topbar_frame, text="Cancel")
                self.topbar_can.configure(bg=cnf.blue_color, pady=1)
                self.topbar_can.cmd(lambda e: cancel_utils_task())
                self.topbar_can.pack(
                    side="left",
                    pady=(5, 0), padx=(0, 10)
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