from . import (Dbase, Image, ImageTk, Thumbs, conf, convert_to_rgb, crop_image,
               datetime, decode_image, find_jpeg, find_tiff, math, partial,
               place_center, sqlalchemy, tkinter, tkmacosx, traceback)
from .img_viewer import ImgViewer
from .widgets import *

__all__ = (
    "Thumbnails",
    )


d_start: datetime = None
d_end: datetime = None
search_item = None


class ContextMenu(tkinter.Menu):
    def __init__(self, src: str, all_src: list, e: tkinter.Event):
        super().__init__()

        self.add_command(
            label=conf.lang.preview,
            command=lambda: ImgViewer(src, all_src)
            )
        self.add_separator()
        self.add_command(
            label=conf.lang.info,
            command=lambda: ImageInfo(src)
            )
        self.add_command(
            label=conf.lang.show_finder,
            command = lambda: find_jpeg(src)
            )
        self.add_command(
            label=conf.lang.show_tiff,
            command = lambda: find_tiff(src)
            )

        self.do_popup(e)

    def do_popup(self, event):
        try:
            self.tk_popup(event.x_root, event.y_root)
        finally:
            self.grab_release()


class FilterWin(CWindow):
    def __init__(self):
        super().__init__()
        self.bind("<Return>", self.ok_cmd)
        self.title(conf.lang.filter_title)
        f = ("San Francisco Pro", 17, "bold")

        calendar_frames = CFrame(self)
        calendar_frames.pack()

        left_frame = CFrame(calendar_frames)
        left_frame.pack(side="left", padx=(0, 15))

        left_title = CLabel(left_frame, text=conf.lang.filter_start)
        left_title["font"] = f
        left_title.pack()

        self.left_calendar = CCalendar(left_frame, d_start)
        self.left_calendar.pack()

        right_frame = CFrame(calendar_frames)
        right_frame.pack(side="left")

        right_title = CLabel(right_frame, text=conf.lang.filter_end)
        right_title["font"] = f
        right_title.pack()

        self.right_calendar = CCalendar(right_frame, d_end)
        self.right_calendar.pack()

        self.oneday_btn = CButton(self, text=conf.lang.filter_oneday)
        self.oneday_btn.pack()
        self.oneday_btn.cmd(lambda e: self.oneday_cmd())

        self.oneday = False

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

        self.sort_modified = conf.sort_modified

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

        if d_start and not d_end:
            self.oneday = True
            self.oneday_btn["bg"] = conf.sel_color
            self.right_calendar.disable_calendar()

        conf.root.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

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

    def oneday_cmd(self):
        self.left_calendar.clicked = True

        if not self.oneday:
            self.oneday = True
            self.oneday_btn["bg"] = conf.sel_color
            self.right_calendar.disable_calendar()

        else:
            self.oneday = False
            self.oneday_btn["bg"] = conf.btn_color
            self.right_calendar.enable_calendar()

    def ok_cmd(self, e=None):
        global d_start, d_end

        if any((self.left_calendar.clicked, self.right_calendar.clicked)):
            d_start = self.left_calendar.my_date

            if not self.oneday:
                d_end = self.right_calendar.my_date
            else:
                d_end = None

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
        from . import app
        app.thumbnails.reload_without_scroll()

    def cancel(self):
        self.destroy()
        focus_last()


class ThumbnailsSearch:
    def search_frame(self, master: tkinter):
        try:
            self.var = tkinter.StringVar(value=search_item)
        except AttributeError:
            tkinter.StringVar(value="-")

        self.cust_ent = tkinter.Entry(
            master,
            width=20,
            textvariable=self.var,
            bg=conf.ent_color,
            insertbackground="white",
            fg=conf.fg_color,
            highlightthickness=0,
            justify="center",
            selectbackground=conf.btn_color,
            border=1
            )
        self.var.trace("w", lambda *args: self.search_task_set())
        self.cust_ent.bind("<Escape>", self.search_esc)
        return self.cust_ent

    def reload_search(self):
        """for external use in menu frame"""
        global search_item
        search_item = None

    def search_esc(self, e=None):
        conf.root.focus_force()

    def search_task_set(self):
        if self.search_task:
            conf.root.after_cancel(self.search_task)
        self.search_task = conf.root.after(1000, self.search_go)

    def search_go(self):
        global search_item
        search_item = self.var.get()
        search_item = search_item.replace("\n", "").strip()
        self.reload_with_scroll()
        conf.root.focus_force()


class ThumbnailsPrepare:
    def thumbs_prepare(self):
        self.all_src = []
        self.thumbs_coords = dict()
        self.clmns_count = self.get_clmns_count()

        self.thumbs_lbls = Dbase.conn.execute(self.get_query()).fetchall()
        self.total = len(self.thumbs_lbls)

        self.thumbs_lbls = self.decode_thumbs()
        self.thumbs_lbls = self.create_thumbs_dict()

        self.size = conf.thumb_size + conf.thumb_pad

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
        limit = 500
        chunk_thumbs = [
            self.thumbs_lbls[i:i+limit]
            for i in range(0, len(self.thumbs_lbls), limit)
        ]

        for chunk, img_list in enumerate(chunk_thumbs):
            for img, src, modified in img_list:
                key = datetime.fromtimestamp(modified).date()

                if not any((d_start, d_end)):
                    key = f"{conf.lang.months[key.month]} {key.year}"

                elif d_start and not d_end:
                    key = f"{key.day} {conf.lang.months_p[key.month]} {key.year}"

                elif all((d_start, d_end)):
                    start = (
                        f"{d_start.day} {conf.lang.months_p[d_start.month]} "
                        f"{d_start.year}"
                        )
                    end = (
                        f"{d_end.day} {conf.lang.months_p[d_end.month]} "
                        f"{d_end.year}"
                        )
                    key = f"{start} - {end}"

                if len(chunk_thumbs) > 1:
                    thumbs_dict.setdefault(
                        (len(self.thumbs_lbls),f"{chunk}:{key}"), []
                        ).append((img, src))
                else:
                    thumbs_dict.setdefault(
                        (None, key), []
                        ).append((img, src))

        return thumbs_dict

    def stamp_range(self):
        start = datetime.combine(d_start, datetime.min.time())
        end = datetime.combine(
            d_end, datetime.max.time().replace(microsecond=0)
            )
        return (datetime.timestamp(start), datetime.timestamp(end))

    def stamp_day(self):
        start = datetime.combine(d_start, datetime.min.time())
        end = datetime.combine(
            d_start, datetime.max.time().replace(microsecond=0)
            )
        return int(start.timestamp()), int(end.timestamp())

    def get_query(self):
        global search_item

        q = sqlalchemy.select(Thumbs.img150, Thumbs.src, Thumbs.modified)

        if search_item:
            q = q.filter(Thumbs.src.like("%" + search_item + "%"))
            q = q.order_by(-Thumbs.modified)
            return q

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

        if not any((d_start, d_end)):
            q = q.limit(conf.limit)

        elif d_start and not d_end:
            t = self.stamp_day()
            q = q.filter(Thumbs.modified > t[0])
            q = q.filter(Thumbs.modified < t[1])
        
        elif all((d_start, d_end)):
            t = self.stamp_range()
            q = q.filter(Thumbs.modified > t[0])
            q = q.filter(Thumbs.modified < t[1])

        return q


class Thumbnails(CFrame, ThumbnailsSearch, ThumbnailsPrepare):
    def __init__(self, master):
        super().__init__(master)
        self.clmns_count = 1

        conf.root.update_idletasks()

        self.load_scrollable()
        self.load_thumbnails()

        conf.root.bind('<Configure>', self.decect_resize)
        self.resize_task = None
        self.search_task = None

    def load_scrollable(self):
        self.scroll_frame = CFrame(self)
        self.scroll_frame.pack(expand=1, fill=tkinter.BOTH)

        self.sframe = tkmacosx.SFrame(
            self.scroll_frame, bg=conf.bg_color, scrollbarwidth=7)
        self.sframe.pack(expand=1, fill=tkinter.BOTH)

        self.sframe.bind_all("<ButtonRelease-1>", self.g_click)

    def g_click(e: tkinter.Event=None, ee: tkinter.Event=None):
        try:
            if ee.widget.widgetName == "frame":
                ee.widget.focus()
        except AttributeError:
            print("thumbnails global click error")

    def load_thumbnails(self):
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
        l_subtitle.pack(anchor="e", side="left", padx=(0, 10))

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
        r_subtitle.pack(anchor="w", side="right")

        filt_reset = CFrame(title_frame)
        filt_reset.pack()

        btn_filter = CButton(filt_reset, text=conf.lang.thumbs_filters)
        btn_filter.pack(side="left", padx=(0, 15))
        if any((d_start, d_end)):
            btn_filter.configure(bg=conf.sel_color)
        btn_filter.cmd(lambda e: FilterWin())

        reset = CButton(filt_reset, text=conf.lang.thumbs_reset)
        reset.pack(side="left")
        reset.cmd(lambda e: self.reset_filter_cmd())

        self.search_frame(title_frame).pack(pady=(15, 0), ipady=2)

        for (chunk_ln, dates), img_list in self.thumbs_lbls.items():

            dates_title = dates.split(":")[-1]
            ln_title = str(chunk_ln) if chunk_ln else len(img_list)

            thumbs_title = CLabel(
                self.thumbs_frame,
                text=(
                f"{dates_title}, "
                f"{conf.lang.thumbs_summary.lower()}: {ln_title}"
                ),
                anchor="w",
                justify="left",
                )
            thumbs_title["font"] = ('San Francisco Pro', 18, 'bold')
            thumbs_title.pack(anchor="w", pady=(30, 0), padx=2)

            w = self.size * self.clmns_count
            h = self.size * (math.ceil(len(img_list) / self.clmns_count))
            empty = Image.new("RGBA", (w, h), color=conf.bg_color)

            row, clmn = 0, 0
            for x, (img, src) in enumerate(img_list, 1):

                self.all_src.append(src)
                self.thumbs_coords.setdefault(
                    dates, dict()
                    )[(clmn//self.size, row//self.size)] = src

                empty.paste(img, (clmn, row))

                clmn += self.size
                if x % self.clmns_count == 0:
                    row += self.size
                    clmn = 0

            img = ImageTk.PhotoImage(empty)
            img_lbl = CLabel(self.thumbs_frame, image=img, text=dates)
            img_lbl.pack(anchor="w")
            img_lbl.image_names = img
            img_lbl.bind('<ButtonRelease-1>', partial(self.click))
            img_lbl.bind("<ButtonRelease-2>", partial(self.r_click))

        if self.total >= 150:
            more_btn = CButton(
                self.thumbs_frame,
                text=conf.lang.thumbs_showmore
                )
            more_btn.cmd(lambda e: self.show_more_cmd())
            more_btn.pack(pady=(15, 0))

        self.thumbs_frame.pack(expand=1, fill=tkinter.BOTH)

    def show_more_cmd(self):
        conf.limit += 150
        self.reload_without_scroll()

    def reset_filter_cmd(self):
        global d_start, d_end, search_item

        d_start = None
        d_end = None

        self.reload_without_scroll()

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
                self.reload_without_scroll()

    def reload_with_scroll(self):
        global d_start, d_end

        d_start = None
        d_end = None
        conf.lang_thumbs.clear()

        self.scroll_frame.destroy()
        self.load_scrollable()
        self.thumbs_frame.destroy()
        self.load_thumbnails()

    def reload_without_scroll(self):
        conf.lang_thumbs.clear()
        self.thumbs_frame.destroy()
        self.load_thumbnails()

    def get_clmns_count(self):
        clmns = (conf.root_w - conf.menu_w) // conf.thumb_size
        return 1 if clmns == 0 else clmns

    def click(self, e: tkinter.Event):
        try:
            clmn, row = e.x//self.size, e.y//self.size
            src = self.thumbs_coords[e.widget.cget("text")][(clmn, row)]
        except KeyError:
            return

        ImgViewer(src, self.all_src)

    def r_click(self, e: tkinter.Event):
        try:
            clmn, row = e.x//self.size, e.y//self.size
            src = self.thumbs_coords[e.widget.cget("text")][(clmn, row)]
        except KeyError:
            return

        ContextMenu(src, self.all_src, e)