from . import (Dbase, ImageTk, Thumbs, cfg, convert_to_rgb, crop_image,
               datetime, decode_image, find_jpeg, find_tiff, get_coll_name,
               partial, place_center, sqlalchemy, tkinter, tkmacosx, traceback)
from .img_viewer import ImgViewer
from .widgets import *

__all__ = (
    "Thumbnails",
    )

months_day = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"}

date_start: datetime = None
date_end: datetime = None


def stamp_range():
    start = datetime.combine(date_start, datetime.min.time())
    end = datetime.combine(
        date_end, datetime.max.time().replace(microsecond=0)
        )

    return (datetime.timestamp(start), datetime.timestamp(end))


def stamp_day():
    start = datetime.combine(date_start, datetime.min.time())
    end = datetime.combine(
        date_start, datetime.max.time().replace(microsecond=0)
        )
    return int(start.timestamp()), int(end.timestamp())


def create_query():
    q = sqlalchemy.select(Thumbs.img150, Thumbs.src, Thumbs.modified)

    if cfg.config["SORT_MODIFIED"]:
        q = q.order_by(-Thumbs.modified)
    else:
        q = q.order_by(-Thumbs.created)

    if cfg.config["CURR_COLL"] != "last":
        q = q.filter(Thumbs.collection == cfg.config["CURR_COLL"])

    if not date_start and not date_end:
        q = q.limit(cfg.LIMIT)
    else:
        q = q.limit(1000)

    if date_start and not date_end:
        t = stamp_day()
        q = q.filter(Thumbs.modified > t[0])
        q = q.filter(Thumbs.modified < t[1])
    
    elif all((date_start, date_end)):
        t = stamp_range()
        q = q.filter(Thumbs.modified > t[0])
        q = q.filter(Thumbs.modified < t[1])

    return q


class ContextMenu(tkinter.Menu):
    def __init__(self, master: tkinter.Label, src: str, all_src: list):
        tkinter.Menu.__init__(self, master)

        self.add_command(
            label = "Просмотр",
            command = lambda: ImgViewer(src, all_src)
            )
        self.add_separator()
        self.add_command(
            label = "Инфо",
            command = lambda: ImageInfo(src, cfg.ROOT)
            )
        self.add_command(
            label = "Показать в Finder",
            command = lambda: find_jpeg(src)
            )
        self.add_command(
            label = "Показать tiff",
            command = lambda: find_tiff(src)
            )
        master.bind("<Button-2>", self.do_popup)

    def do_popup(self, event):
        try:
            self.tk_popup(event.x_root, event.y_root)
        finally:
            self.grab_release()


class LimitWin(CWindow):
    def __init__(self):
        super().__init__()
        self.title("Лимит")

        t = (
            "Достигнут лимит отображения в 1000 фото."
            "\nУменьшите диапазон дат для просмотра или"
            "\nпримените фильтр в нужной коллекции."
            )
        lbl = CLabel(self, text=t, justify="left")
        lbl.pack()

        btn = CButton(self, text="Закрыть")
        btn.pack(pady=(15, 0))
        btn.cmd(lambda e: self.cmd())

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def cmd(self):
        self.destroy()
        focus_last()


class FilterWin(CWindow):
    def __init__(self):
        super().__init__()
        self.title("Фильтр")
        f = ("San Francisco Pro", 17, "bold")

        cal_frames = CFrame(self)
        cal_frames.pack()

        left = CFrame(cal_frames)
        left.pack(side="left", padx=(0, 15))

        first = CLabel(left, text="Начало")
        first["font"] = f
        first.pack()

        self.one = CCalendar(left, date_start)
        self.one.pack(pady=(15, 0))

        right = CFrame(cal_frames)
        right.pack(side="left")

        second = CLabel(right, text="Конец")
        second["font"] = f
        second.pack()

        self.two = CCalendar(right, date_end)
        self.two.pack(pady=(15, 0))

        self.oneday_btn = CButton(self, text="За один день")
        self.oneday_btn.pack(pady=(15, 0))
        self.oneday_btn.cmd(lambda e: self.oneday_cmd())
        self.oneday = False

        btns_frame = CFrame(self)
        btns_frame.pack(pady=(15, 0))

        ok_btn = CButton(btns_frame, text="Ок")
        ok_btn.pack(side="left", padx=15)
        ok_btn.cmd(lambda e: self.ok_cmd())

        cancel_btn = CButton(btns_frame, text="Отмена")
        cancel_btn.pack(side="left")
        cancel_btn.cmd(lambda e: self.cancel())

        if date_start and not date_end:
            self.oneday = True
            self.oneday_btn["bg"] = cfg.SELECTED
            self.two.disable_calendar()

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def oneday_cmd(self):
        if not self.oneday:
            self.oneday = True
            self.oneday_btn["bg"] = cfg.SELECTED
            self.two.disable_calendar()

        else:
            self.oneday = False
            self.oneday_btn["bg"] = cfg.BUTTON
            self.two.enable_calendar()

    def ok_cmd(self):
        global date_start, date_end

        date_start = self.one.my_date
        if not self.oneday:
            date_end = self.two.my_date
        else:
            date_end = None

        self.destroy()
        focus_last()
        from gui_start import gui_start
        gui_start.thumbnails.reload_without_scroll()

    def cancel(self):
        self.destroy()
        focus_last()


class Thumbnails(CFrame):
    def __init__(self, master):
        super().__init__(master)
        self.clmns = 1

        cfg.ROOT.update_idletasks()

        self.load_scrollable()
        self.load_thumbnails()

        cfg.ROOT.bind('<Configure>', self.decect_resize)
        self.resize_task = None

    def load_scrollable(self):
        self.scroll_parrent = CFrame(self)
        self.scroll_parrent.pack(expand=1, fill=tkinter.BOTH)

        self.scrollable = tkmacosx.SFrame(
            self.scroll_parrent, bg=cfg.BG, scrollbarwidth=7)
        self.scrollable.pack(expand=1, fill=tkinter.BOTH)

    def load_thumbnails(self):
        self.clmns = self.clmns_count()
        load_db = Dbase.conn.execute(create_query()).fetchall()
        thumbs = self.decode_thumbs(load_db)
        thumbs: dict = self.create_thumbs_dict(thumbs)
        summary = len(load_db)
        all_src = []

        if summary == 1000 and any((date_start, date_end)):
            LimitWin()

        self.thumbnails = CFrame(self.scrollable)

        if cfg.config["CURR_COLL"] == "last":
            txt = "Все коллекции"
        else:
            txt = cfg.config["CURR_COLL"]

        title = CLabel(self.thumbnails, text=txt)
        title.configure(font=('San Francisco Pro', 45, 'bold'))
        title.pack()

        sub_frame = CFrame(self.thumbnails)
        sub_frame.pack(pady=(0, 15))

        sub_l = CFrame(sub_frame)
        sub_l.pack(side="left", padx=5)

        sub_r = CFrame(sub_frame)
        sub_r.pack(side="right", padx=5)

        sub_font=('San Francisco Pro', 13, 'normal')

        first_l = CLabel(sub_l, text="Всего")
        first_l.configure(font=sub_font, justify="right", anchor="e", width=30)
        first_l.pack(anchor="e")

        sec_l = CLabel(sub_l, text="Даты")
        sec_l.configure(font=sub_font, justify="right", anchor="e", width=30)
        sec_l.pack(anchor="e")

        third_l = CLabel(sub_l, text="Сортировка")
        third_l.configure(font=sub_font, justify="right", anchor="e", width=30)
        third_l.pack(anchor="e")

        first_r = CLabel(sub_r, text=f"{summary} фото")
        first_r.configure(font=sub_font, justify="left", anchor="w", width=30)
        first_r.pack(anchor="w")

        if date_start and not date_end:
            dates = (
                f"{date_start.day} {months_day[date_start.month]} "
                f"{date_start.year}"
                )

        elif all((date_start, date_end)):
            start = (
                f"{date_start.day} {months_day[date_start.month]} "
                f"{date_start.year}"
                )
            end = (f"{date_end.day} {months_day[date_end.month]} "
                   f"{date_end.year}"
                   )
            dates = f"{start} - {end}"

        else:
            dates = "За все время"

        sec_r = CLabel(sub_r, text=dates)
        sec_r.configure(font=sub_font, justify="left", anchor="w", width=30)
        sec_r.pack(anchor="w")

        if cfg.config["SORT_MODIFIED"]:
            sort_text = "По дате изменения"
        else:
            sort_text = "По дате создания"

        third_r = CLabel(sub_r, text=sort_text)
        third_r.configure(font=sub_font, justify="left", anchor="w", width=30)
        third_r.pack(anchor="w")

        btns_frame = CFrame(self.thumbnails)
        btns_frame.pack()

        btn_day = CButton(btns_frame, text="Фильтр")
        btn_day["width"] = 13
        btn_day.pack(side="left")
        if any((date_start, date_end)):
            btn_day["bg"] = cfg.SELECTED
        btn_day.cmd(lambda e: FilterWin())

        CSep(btns_frame).pack(fill="y", side="left", padx=(15, 15))

        if cfg.config["SORT_MODIFIED"]:
            sort_btn_t = "Дата изменения"
        else:
            sort_btn_t = "Дата создания"

        btn_sort = CButton(btns_frame, text=sort_btn_t)
        btn_sort["width"] = 13
        btn_sort.pack(side="left")
        btn_sort.cmd(lambda e: self.sort_btn_cmd(btn_sort))

        if any((date_start, date_end)):
            reset = CButton(self.thumbnails, text="Сброс")
            reset.pack(pady=(15, 0))
            reset.cmd(lambda e: self.reset_filter_cmd())

        for (coll, dates), img_list in thumbs.items():

            if cfg.config["CURR_COLL"] == "last":
                title = CLabel(self.thumbnails, text=coll)
                title["font"] = ('San Francisco Pro', 26, 'bold')
                title.pack(anchor="w", pady=(30, 0))

            coll_sub = CLabel(
                self.thumbnails, text=f"{dates}, всего: {len(img_list)}"
                )
            coll_sub.configure(
                font=('San Francisco Pro', 13, 'normal'),
                )
            coll_sub.pack(anchor="w")
            if cfg.config["CURR_COLL"] != "last":
                coll_sub.pack(pady=(30, 0))

            img_row = CFrame(self.thumbnails)
            img_row.pack(fill = tkinter.X, expand=1, anchor=tkinter.W)

            for x, (img, src) in enumerate(img_list, 1):

                all_src.append(src)

                thumb = CButton(img_row)
                thumb.configure(
                    width = cfg.THUMB_SIZE,
                    height = cfg.THUMB_SIZE,
                    bg=cfg.BG,
                    image = img,
                    text = src
                    )
                thumb.pack(side=tkinter.LEFT)

                thumb.image_names = img
                thumb.cmd(partial(self.img_viewer_cmd, src, all_src))

                ContextMenu(thumb, src, all_src)

                if x % self.clmns == 0:
                    img_row = CFrame(self.thumbnails)
                    img_row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

        if summary >= 150:
            more_btn = CButton(self.thumbnails, text="Показать еще")
            more_btn.cmd(lambda e: self.show_more_cmd())
            more_btn.pack(pady=(15, 0))

        self.thumbnails.pack(expand=1, fill=tkinter.BOTH)

    def sort_btn_cmd(self, btn: CButton):
        if cfg.config["SORT_MODIFIED"]:
            cfg.config["SORT_MODIFIED"] = False
            btn["text"] = "Дата создания"
            self.reload_without_scroll()
        else:
            cfg.config["SORT_MODIFIED"] = True
            btn["text"] = "Дата изменения"
            self.reload_without_scroll()

    def img_viewer_cmd(self, src, all_src, e):
        ImgViewer(src, all_src)

    def show_more_cmd(self):
        cfg.LIMIT += 150
        self.reload_without_scroll()

    def reset_filter_cmd(self):
        global date_start, date_end

        date_start = None
        date_end = None

        self.reload_without_scroll()

    def decect_resize(self, e):
        if self.resize_task:
            cfg.ROOT.after_cancel(self.resize_task)
        self.resize_task = cfg.ROOT.after(250, self.update_thumbnails)

    def update_thumbnails(self):
        old_w = cfg.config['ROOT_W']
        new_w = cfg.ROOT.winfo_width()

        if new_w != old_w:
            cfg.config['ROOT_W'] = new_w

            if self.clmns != self.clmns_count():
                w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
                cfg.config['ROOT_W'], cfg.config['ROOT_H'] = w, h
                cfg.ROOT.update_idletasks()
                self.reload_without_scroll()

    def reload_with_scroll(self):
        global date_start, date_end

        date_start = None
        date_end = None

        self.scroll_parrent.destroy()
        self.load_scrollable()
        self.thumbnails.destroy()
        self.load_thumbnails()

    def reload_without_scroll(self):
        self.thumbnails.destroy()
        self.load_thumbnails()

    def clmns_count(self):
        clmns = (cfg.config['ROOT_W'] - 180) // cfg.THUMB_SIZE
        return 1 if clmns == 0 else clmns

    def decode_thumbs(self, thumbs: tuple):
        result = []
        for blob, src, modified in thumbs:
            try:
                decoded = decode_image(blob)
                cropped = crop_image(decoded)
                rgb = convert_to_rgb(cropped)
                img = ImageTk.PhotoImage(rgb)
                result.append((img, src, modified))

            except Exception:
                print(traceback.format_exc())

        return result

    def create_thumbs_dict(self, thumbs: list):
        thumbs_dict = {}
        for img, src, modified in thumbs:
            coll = get_coll_name(src)
            t = datetime.fromtimestamp(modified).date()

            if not date_start and not date_end:
                t = f"{months[t.month]} {t.year}"

            elif date_start and not date_end:
                t = f"{t.day} {months_day[t.month]} {t.year}"

            elif all((date_start, date_end)):
                start = (
                    f"{date_start.day} {months_day[date_start.month]} "
                    f"{date_start.year}"
                    )
                end = (
                    f"{date_end.day} {months_day[date_end.month]} "
                    f"{date_end.year}"
                    )
                t = f"{start} - {end}"

            thumbs_dict.setdefault((coll, t), []).append((img, src))

        return thumbs_dict