import math
import tkinter
import traceback
from datetime import datetime

import sqlalchemy
import tkmacosx
from PIL import Image, ImageTk

from cfg import conf
from database import Dbase, Thumbs
from utils import *

from .globals import Globals
from .img_viewer import ImgViewer
from .widgets import *

__all__ = (
    "Thumbnails",
    )


class Dates:
    start: datetime = None
    end: datetime = None
    named_start = None
    named_end = None


class ContextTitles(ContextMenu):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.context_download_group(e)
        self.do_popup(e)


class ContextThumbs(ContextMenu):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.context_view(e)
        self.context_img_info(e)

        self.context_sep()
        self.context_show_jpg(e)
        self.context_download_onefile(e)

        self.context_sep()
        self.context_show_tiffs(e)
        self.context_download_tiffs(e)

        self.do_popup(e)


class ContextSearch(ContextMenu):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.context_clear()
        self.context_paste()
        self.do_popup(e)


class FilterWin(CWindow):
    def __init__(self):
        super().__init__()
        self.bind("<Return>", self.ok_cmd)
        self.title(conf.lang.filter_title)
        f = ("San Francisco Pro", 17, "bold")
        self.reseted = False
        self.date_changed = False

        calendar_frames = CFrame(self)
        calendar_frames.pack()

        left_frame = CFrame(calendar_frames)
        left_frame.pack(side="left", padx=(0, 15))

        left_title = CLabel(left_frame, text=conf.lang.filter_start)
        left_title["font"] = f
        left_title.pack()

        self.l_calendar = CCalendar(left_frame, Dates.start)
        self.l_calendar.pack()

        right_frame = CFrame(calendar_frames)
        right_frame.pack(side="left")

        right_title = CLabel(right_frame, text=conf.lang.filter_end)
        right_title["font"] = f
        right_title.pack()

        self.r_calendar = CCalendar(right_frame, Dates.end)
        self.r_calendar.pack()

        if any((Dates.start, Dates.end)):
            cals_t = f"{Dates.named_start} - {Dates.named_end}"
        else:
            cals_t = conf.lang.filter_notselected
        self.cals_titles = CLabel(self, text=cals_t)
        self.cals_titles.configure(font=f)
        self.cals_titles.pack()

        cals_reset = CButton(self, text=conf.lang.settings_reset)
        cals_reset.pack(pady=(15, 0))
        cals_reset.cmd(self.cals_titles_reset)

        CSep(self).pack(fill="x", padx=15, pady=15)

        grop_frame = CFrame(self)
        grop_frame.pack()

        self.product = CButton(grop_frame, text=conf.lang.filter_product)
        if conf.product:
            self.product.configure(bg=conf.sel_color)
        self.product.pack(side="left")
        self.product.cmd(self.product_cmd)

        self.models = CButton(grop_frame, text=conf.lang.filter_models)
        if conf.models:
            self.models.configure(bg=conf.sel_color)
        self.models.pack(side="left", padx=15)
        self.models.cmd(self.models_cmd)

        self.catalog = CButton(grop_frame, text=conf.lang.filter_catalog)
        if conf.catalog:
            self.catalog.configure(bg=conf.sel_color)
        self.catalog.pack(side="left")
        self.catalog.cmd(self.catalog_cmd)

        if conf.sort_modified:
            sort_btn_t = conf.lang.filter_changed
        else:
            sort_btn_t = conf.lang.filter_created

        self.btn_sort = CButton(self, text=sort_btn_t)
        self.btn_sort.configure(width=13)
        self.btn_sort.pack(pady=(15, 0))
        self.btn_sort.cmd(self.sort_btn_cmd)

        marketing_lbl = CLabel(
            self, text="\n".join(conf.lang.filter_descr),
            anchor="w", justify="left")
        marketing_lbl.pack(anchor="w", pady=(15, 0))

        CSep(self).pack(fill="x", padx=150, pady=15)

        btns_frame = CFrame(self)
        btns_frame.pack(pady=(15, 0))

        ok_btn = CButton(btns_frame, text=conf.lang.ok)
        ok_btn.pack(side="left", padx=15)
        ok_btn.cmd(self.ok_cmd)

        cancel_btn = CButton(btns_frame, text=conf.lang.cancel)
        cancel_btn.pack(side="left")
        cancel_btn.cmd(lambda e: self.cancel())

        conf.root.update_idletasks()

        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()
        Globals.filter_text_cmd = self.cals_titles_cmd

    def named_date(self, date: datetime):
        day = f"{date.day} "
        month = f"{conf.lang.months_p[date.month]} "
        year = f"{date.year}"
        return day + month + year

    def cals_titles_cmd(self):
        start = self.named_date(self.l_calendar.my_date)
        end = self.named_date(self.r_calendar.my_date)
        self.cals_titles.configure(text=f"{start} - {end}")
        self.date_changed = True

    def cals_titles_reset(self, e=None):
        for i in (self.l_calendar, self.r_calendar):
            i.clicked = False
            i.reset_cal()
        self.reseted = True
        self.date_changed = False
        self.cals_titles.configure(text=conf.lang.filter_notselected)

    def sort_btn_cmd(self, e):
        if self.btn_sort["text"] == conf.lang.filter_changed:
            self.btn_sort.configure(text=conf.lang.filter_created)
        else:
            self.btn_sort.configure(text=conf.lang.filter_changed)

    def product_cmd(self, e=None):
        if self.product["bg"] == conf.sel_color:
            self.product.configure(bg=conf.btn_color)
        else:
            self.product.configure(bg=conf.sel_color)

    def catalog_cmd(self, e=None):
        if self.catalog["bg"] == conf.sel_color:
            self.catalog.configure(bg=conf.btn_color)
        else:
            self.catalog.configure(bg=conf.sel_color)

    def models_cmd(self, e=None):
        if self.models["bg"] == conf.sel_color:
            self.models.configure(bg=conf.btn_color)
        else:
            self.models.configure(bg=conf.sel_color)

    def ok_cmd(self, e=None):
        if self.date_changed:
            Dates.start = self.l_calendar.my_date
            Dates.end = self.r_calendar.my_date
            Dates.named_start = self.named_date(Dates.start)
            Dates.named_end = self.named_date(Dates.end)

        if self.reseted:
            Dates.start = None
            Dates.end = None

        if self.product["bg"] == conf.sel_color:
            conf.product = True
        else:
            conf.product = False

        if self.models["bg"] == conf.sel_color:
            conf.models = True
        else:
            conf.models = False

        if self.catalog["bg"] == conf.sel_color:
            conf.catalog = True
        else:
            conf.catalog = False

        if not any((conf.product, conf.models, conf.catalog)):
            conf.product = True
            conf.models = True
            conf.catalog = True

        if self.btn_sort["text"] == conf.lang.filter_created:
            conf.sort_modified = False
        else:
            conf.sort_modified = True

        self.destroy()
        focus_last()
        Globals.reload_thumbs()

    def cancel(self):
        self.destroy()
        focus_last()


class ThumbSearch(tkinter.Entry):
    def __init__(self, master: tkinter):
        super().__init__(
            master,
            width=20,
            textvariable=Globals.search_var,
            bg=conf.ent_color,
            insertbackground="white",
            fg=conf.fg_color,
            highlightthickness=0,
            justify="center",
            selectbackground=conf.btn_color,
            border=1
            )

        traces = Globals.search_var.trace_vinfo()
        if traces:
            Globals.search_var.trace_vdelete(*traces[0])
        Globals.search_var.trace("w", lambda *args: self.search_task_set())

        self.bind("<Escape>", lambda e: conf.root.focus_force())
        conf.root.bind("<Command-f>", lambda e: self.focus_force())
        self.bind("<ButtonRelease-2>", lambda e: ContextSearch(e))
        self.search_task = None

    def search_task_set(self):
        if self.search_task:
            conf.root.after_cancel(self.search_task)
        self.search_task = conf.root.after(1000, self.search_go)

    def search_go(self):
        Globals.reload_scroll()
        conf.root.focus_force()


class ThumbnailsPrepare:
    def thumbs_prepare(self):
        self.clmns_count = self.get_clmns_count()

        self.thumbs_lbls = Dbase.conn.execute(self.get_query()).fetchall()
        self.thumbs_lbls = self.decode_thumbs()
        self.thumbs_lbls = self.create_thumbs_dict()

        self.thumb_size = conf.thumb_size + conf.thumb_pad

        if conf.curr_coll == conf.all_colls:
            self.coll_title = conf.lang.all_colls
        else:
            self.coll_title = conf.curr_coll

        filter_row = []

        if conf.product:
            filter_row.append(conf.lang.thumbs_product)
        if conf.models:
            filter_row.append(conf.lang.thumbs_models)
        if conf.catalog:
            filter_row.append(conf.lang.thumbs_catalog)

        filter_row = ", ".join(filter_row)
        self.filter_row = filter_row.lower().capitalize()

        if conf.sort_modified:
            self.sort_text = conf.lang.thumbs_changed
        else:
            self.sort_text = conf.lang.thumbs_created

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

            if not any((Dates.start, Dates.end)):
                date_key = f"{conf.lang.months[date_key.month]} {date_key.year}"
            else:
                date_key = f"{Dates.named_start} - {Dates.named_end}"

            thumbs_dict.setdefault(date_key, [])
            thumbs_dict[date_key].append((img, src))

        return thumbs_dict

    def stamp_dates(self):
        start = datetime.combine(Dates.start, datetime.min.time())
        end = datetime.combine(
            Dates.end, datetime.max.time().replace(microsecond=0)
            )
        return (datetime.timestamp(start), datetime.timestamp(end))

    def get_query(self):
        q = sqlalchemy.select(Thumbs.img150, Thumbs.src, Thumbs.modified)
        search = Globals.search_var.get()

        if search:
            search.replace("\n", "").strip()
            q = q.filter(Thumbs.src.like("%" + search + "%"))

        if conf.sort_modified:
            q = q.order_by(-Thumbs.modified)
        else:
            q = q.order_by(-Thumbs.created)

        if conf.curr_coll != conf.all_colls:
            q = q.filter(Thumbs.collection == conf.curr_coll)

        filters = []

        if conf.models:
            filters.append(Thumbs.src.like("%" + conf.models_name + "%"))

        if conf.catalog:
            filters.append(Thumbs.src.like("%" + conf.catalog_name + "%"))

        if conf.product:
            tmp = sqlalchemy.and_(
                Thumbs.src.not_like("%" + conf.catalog_name + "%"),
                Thumbs.src.not_like("%" + conf.models_name + "%")
                )
            filters.append(tmp)

        q = q.filter(sqlalchemy.or_(*filters))

        if not any((Dates.start, Dates.end)):
            q = q.limit(conf.limit)

        else:
            t = self.stamp_dates()
            q = q.filter(Thumbs.modified > t[0])
            q = q.filter(Thumbs.modified < t[1])

        return q


class Thumbnails(CFrame, ThumbnailsPrepare):
    def __init__(self, master):
        super().__init__(master)

        move_top = CButton(self, text="▲  ")
        move_top.configure(
            font=('San Francisco Pro', 13, 'normal'),
            bg=conf.bg_color,
            width=50
            )
        move_top.pack(pady=3)
        move_top.cmd(self.scroll_up)

        self.clmns_count = 1

        conf.root.update_idletasks()

        self.load_scroll()
        self.load_thumbs()

        conf.root.bind('<Configure>', self.decect_resize)
        self.resize_task = None
        self.search_task = None

        Globals.reload_scroll = self.reload_scroll
        Globals.reload_thumbs = self.reload_thumbs

    def load_scroll(self):
        self.scroll_frame = CFrame(self)
        self.scroll_frame.pack(expand=1, fill=tkinter.BOTH)

        self.sframe = tkmacosx.SFrame(
            self.scroll_frame, bg=conf.bg_color, scrollbarwidth=7)
        self.sframe.pack(expand=1, fill=tkinter.BOTH)

    def load_thumbs(self):
        self.thumbs_prepare()

        self.thumbs_frame = CFrame(self.sframe)

        title_frame = CFrame(self.thumbs_frame)
        title_frame.pack()

        main_title = CLabel(title_frame, text=self.coll_title, width=30)
        main_title.configure(font=('San Francisco Pro', 30, 'bold'))
        main_title.pack(anchor="center")
        conf.lang_thumbs.append(main_title)

        main_sub_frame = CFrame(title_frame)
        main_sub_frame.pack(pady=(0, 15))

        sub_font=('San Francisco Pro', 13, 'normal')

        l_subtitle_t = (
            f"{conf.lang.thumbs_filter}"
            f"\n{conf.lang.thumbs_sort}"
            )
        l_subtitle = CLabel(main_sub_frame, text=l_subtitle_t)
        l_subtitle.configure(
            font=sub_font,
            justify="right",
            anchor="e",
            width=35
            )
        l_subtitle.pack(side="left", padx=(0, 10))

        r_subtitle_t = (
            f"{self.filter_row}"
            f"\n{self.sort_text}"
            )
        r_subtitle = CLabel(main_sub_frame, text=r_subtitle_t)
        r_subtitle.configure(
            font=sub_font,
            justify="left",
            anchor="w",
            width=45
            )
        r_subtitle.pack(side="right")

        btn_filter = CButton(title_frame, text=conf.lang.thumbs_filters)
        btn_filter.pack()
        if any((Dates.start, Dates.end)):
            btn_filter.configure(bg=conf.sel_color)
        btn_filter.cmd(lambda e: FilterWin())

        search = ThumbSearch(title_frame)
        search.pack(pady=(15, 0), ipady=2)

        all_src = []
        limit = 500

        for date_key, img_list in self.thumbs_lbls.items():
            
            chunks = [
                img_list[i:i+limit]
                for i in range(0, len(img_list), limit)
                ]

            t = f"{date_key}, {conf.lang.thumbs_total}: {len(img_list)}"
            chunk_title = CLabel(self.thumbs_frame, text=t)
            chunk_title.configure(font=('San Francisco Pro', 18, 'bold'))
            chunk_title.pack(anchor="w", pady=(30, 0), padx=2)

            chunk_title.title = date_key
            chunk_title.paths_list = (i[1] for i in img_list)
            chunk_title.bind("<ButtonRelease-2>", ContextTitles)

            for chunk in chunks:

                chunk_ln = len(chunk)
                rows = math.ceil(chunk_ln/self.clmns_count)

                w = self.thumb_size * self.clmns_count
                h = self.thumb_size * rows

                empty = Image.new("RGBA", (w, h), color=conf.bg_color)
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
                img_lbl.name = (date_key, chunk)
                img_lbl.coords = coords
                img_lbl.all_src = all_src
                img_lbl.bind('<ButtonRelease-1>', self.click)
                img_lbl.bind("<ButtonRelease-2>", self.r_click)

        if not self.thumbs_lbls:
            no_img_lst = [conf.lang.thumbs_nophoto]
            str_var = Globals.search_var.get()
            if str_var:
                no_img_lst.append(f"{conf.lang.thumbs_withname} {str_var}")
            if any((Dates.start, Dates.end)):
                no_img_lst.append(f"{Dates.named_start} - {Dates.named_end}")

            no_images = CLabel(self.thumbs_frame, text="\n".join(no_img_lst))
            no_images.configure(font=('San Francisco Pro', 18, 'bold'))
            no_images.pack(pady=(15, 0))

        more_btn = CButton(
            self.thumbs_frame,
            text=conf.lang.thumbs_showmore
            )
        more_btn.cmd(lambda e: self.show_more_cmd())
        more_btn.pack(pady=(15, 0))

        self.thumbs_frame.pack(expand=1, fill=tkinter.BOTH)

    def show_more_cmd(self):
        conf.limit += 150
        Globals.reload_thumbs()

    def decect_resize(self, e):
        if self.resize_task:
            conf.root.after_cancel(self.resize_task)
        self.resize_task = conf.root.after(500, self.frame_resize)

    def frame_resize(self):
        old_w = conf.root_w
        new_w = conf.root.winfo_width()

        if new_w != old_w:
            conf.root_w = new_w

            if self.clmns_count != self.get_clmns_count():
                w, h = conf.root.winfo_width(), conf.root.winfo_height()
                conf.root_w, conf.root_h = w, h
                conf.root.update_idletasks()
                Globals.reload_thumbs()

    def reload_scroll(self):
        Dates.start, Dates.end = None, None
        conf.lang_thumbs.clear()

        self.scroll_frame.destroy()
        self.thumbs_frame.destroy()
        self.load_scroll()
        self.load_thumbs()

    def reload_thumbs(self):
        conf.lang_thumbs.clear()
        self.thumbs_frame.destroy()
        self.load_thumbs()

    def get_clmns_count(self):
        clmns = (conf.root_w - conf.menu_w) // conf.thumb_size
        return 1 if clmns == 0 else clmns

    def click(self, e: tkinter.Event):
        try:
            clmn, row = e.x//self.thumb_size, e.y//self.thumb_size
            src = e.widget.coords[(clmn, row)]
        except KeyError:
            return

        ImgViewer(src, e.widget.all_src)

    def r_click(self, e: tkinter.Event):
        try:
            clmn, row = e.x//self.thumb_size, e.y//self.thumb_size
            e.widget.src = e.widget.coords[(clmn, row)]
        except KeyError:
            return

        ContextThumbs(e)

    def scroll_up(self, e=None):
        self.sframe['canvas'].yview_moveto('0.0')