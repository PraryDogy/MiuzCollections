import math

from PIL import Image

from . import (Dbase, ImageTk, Thumbs, conf, convert_to_rgb, crop_image,
               datetime, decode_image, find_jpeg, find_tiff, partial,
               place_center, sqlalchemy, tkinter, tkmacosx, traceback)
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

    if conf.sort_modified:
        q = q.order_by(-Thumbs.modified)
    else:
        q = q.order_by(-Thumbs.created)

    if conf.curr_coll != "last":
        q = q.filter(Thumbs.collection == conf.curr_coll)

    # только имиджи - маркетинг труе, каталог фалсе
    # только каталожка - маркетинг фалсе, каталог труе
    # показать все- маркетинг и каталог фалсе

    if conf.marketing:
        q = q.filter(sqlalchemy.not_(Thumbs.src.contains(conf.catalog_name)))

    elif conf.catalog:
        q = q.filter(Thumbs.src.contains(conf.catalog_name))

    if not date_start and not date_end:
        q = q.limit(conf.limit)

    elif date_start and not date_end:
        t = stamp_day()
        q = q.filter(Thumbs.modified > t[0])
        q = q.filter(Thumbs.modified < t[1])
    
    elif all((date_start, date_end)):
        t = stamp_range()
        q = q.filter(Thumbs.modified > t[0])
        q = q.filter(Thumbs.modified < t[1])

    return q


class ContextMenu(tkinter.Menu):
    def __init__(self, src: str, all_src: list, e: tkinter.Event):
        super().__init__()

        self.add_command(
            label = "Просмотр",
            command = lambda: ImgViewer(src, all_src)
            )
        self.add_separator()
        self.add_command(
            label = "Инфо",
            command = lambda: ImageInfo(src)
            )
        self.add_command(
            label = "Показать в Finder",
            command = lambda: find_jpeg(src)
            )
        self.add_command(
            label = "Показать tiff",
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
        self.one.pack()

        right = CFrame(cal_frames)
        right.pack(side="left")

        second = CLabel(right, text="Конец")
        second["font"] = f
        second.pack()

        self.two = CCalendar(right, date_end)
        self.two.pack()

        self.oneday_btn = CButton(self, text="За один день")
        self.oneday_btn.pack()
        self.oneday_btn.cmd(lambda e: self.oneday_cmd())
        self.oneday = False

        CSep(self).pack(fill="x", padx=15, pady=15)

        grop_frame = CFrame(self)
        grop_frame.pack()

        self.marketing = CButton(grop_frame, text="Имиджи")
        if conf.marketing:
            self.marketing.configure(bg=conf.sel_color)
        self.marketing.pack(side="left")
        self.marketing.cmd(self.marketing_cmd)

        self.catalog = CButton(grop_frame, text="Каталог")
        if conf.catalog:
            self.catalog.configure(bg=conf.sel_color)
        self.catalog.pack(side="left", padx=15)
        self.catalog.cmd(self.catalog_cmd)

        self.show_all = CButton(grop_frame, text="Все фото")
        if not any((conf.marketing, conf.catalog)):
            self.show_all.configure(bg=conf.sel_color)
        self.show_all.pack(side="left")
        self.show_all.cmd(self.show_all_cmd)

        if conf.sort_modified:
            sort_btn_t = "Дата изменения"
        else:
            sort_btn_t = "Дата создания"

        self.sort_modified = conf.sort_modified

        self.btn_sort = CButton(self, text=sort_btn_t)
        self.btn_sort.configure(width=13)
        self.btn_sort.pack(pady=(20, 0))
        self.btn_sort.cmd(self.sort_btn_cmd)

        marketing_t = (
            "Имиджи - показывать только рекламные фото.",
            "Каталог - показывать только каталожные фото.",
            "Сортировка - по дате изменения или по дате создания."
            )
        marketing_lbl = CLabel(
            self, text="\n".join(marketing_t), anchor="w", justify="left")
        marketing_lbl.pack(anchor="w", pady=(15, 0))

        CSep(self).pack(fill="x", padx=150, pady=15)

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
            self.oneday_btn["bg"] = conf.sel_color
            self.two.disable_calendar()

        conf.root.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def sort_btn_cmd(self, e):
        if conf.sort_modified:
            conf.sort_modified = False
            self.btn_sort.configure(text="Дата создания")
        else:
            conf.sort_modified = True
            self.btn_sort.configure(text="Дата изменения")

    def marketing_cmd(self, e):
        if not conf.marketing:
            conf.marketing = True
            conf.catalog = False
            self.marketing.configure(bg=conf.sel_color)
            self.catalog.configure(bg=conf.btn_color)
            self.show_all.configure(bg=conf.btn_color)

    def catalog_cmd(self, e):
        if not conf.catalog:
            conf.marketing = False
            conf.catalog = True
            self.marketing.configure(bg=conf.btn_color)
            self.catalog.configure(bg=conf.sel_color)
            self.show_all.configure(bg=conf.btn_color)

    def show_all_cmd(self, e):
        if any((conf.marketing, conf.catalog)):
            conf.marketing = False
            conf.catalog = False
            self.marketing.configure(bg=conf.btn_color)
            self.catalog.configure(bg=conf.btn_color)
            self.show_all.configure(bg=conf.sel_color)

    def oneday_cmd(self):
        if not self.oneday:
            self.oneday = True
            self.oneday_btn["bg"] = conf.sel_color
            self.two.disable_calendar()

        else:
            self.oneday = False
            self.oneday_btn["bg"] = conf.btn_color
            self.two.enable_calendar()

    def ok_cmd(self):
        global date_start, date_end

        if any((self.one.clicked, self.two.clicked)):
            date_start = self.one.my_date
            if not self.oneday:
                date_end = self.two.my_date
            else:
                date_end = None

        self.destroy()
        focus_last()
        from . import app
        app.thumbnails.reload_without_scroll()

    def cancel(self):
        self.destroy()
        focus_last()


class Thumbnails(CFrame):
    def __init__(self, master):
        super().__init__(master)
        self.clmns = 1

        conf.root.update_idletasks()

        self.load_scrollable()
        self.load_thumbnails()

        conf.root.bind('<Configure>', self.decect_resize)
        self.resize_task = None

    def load_scrollable(self):
        self.scroll_parrent = CFrame(self)
        self.scroll_parrent.pack(expand=1, fill=tkinter.BOTH)

        self.scrollable = tkmacosx.SFrame(
            self.scroll_parrent, bg=conf.bg_color, scrollbarwidth=7)
        self.scrollable.pack(expand=1, fill=tkinter.BOTH)

    def load_thumbnails(self):
        self.all_src = []
        self.all_thumbs = dict()
        self.clmns = self.clmns_count()
        load_db = Dbase.conn.execute(create_query()).fetchall()
        padding = 4
        thumbs = self.decode_thumbs(load_db)
        thumbs: dict = self.create_thumbs_dict(thumbs)
        self.size = conf.thumb_size + padding
        summary = len(load_db)

        if conf.curr_coll == "last":
            txt = "Все коллекции"
        else:
            txt = conf.curr_coll

        filter_row = []

        if conf.marketing:
            filter_row.append("Только имиджи")
        elif conf.catalog:
            filter_row.append("Только каталог")
        elif not any((conf.marketing, conf.catalog)):
            filter_row.append("Все фото")

        if date_start and not date_end:
            filter_row.append(
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
            filter_row.append(f"{start} - {end}")
        else:
            filter_row.append("за все время")

        filter_row = ", ".join(filter_row)

        if conf.sort_modified:
            sort_text = "По дате изменения"
        else:
            sort_text = "По дате создания"

        self.thumbnails = CFrame(self.scrollable)

        title = CLabel(self.thumbnails, text=txt)
        title.configure(font=('San Francisco Pro', 45, 'bold'))
        title.pack()

        sub_frame = CFrame(self.thumbnails)
        sub_frame.pack(pady=(0, 15))

        sub_font=('San Francisco Pro', 13, 'normal')

        l_subtitle = CLabel(sub_frame, text="Всего\nФильтр\nСортировка")
        l_subtitle.configure(font=sub_font, justify="right", anchor="e", width=30)
        l_subtitle.pack(anchor="e", side="left", padx=5)

        r_text = f"{summary} фото\n{filter_row}\n{sort_text}"
        r_subtitle = CLabel(sub_frame, text=r_text)
        r_subtitle.configure(font=sub_font, justify="left", anchor="w", width=30)
        r_subtitle.pack(anchor="w", side="right", padx=5)

        btns_frame = CFrame(self.thumbnails)
        btns_frame.pack()

        btn_day = CButton(btns_frame, text="Фильтры")
        btn_day["width"] = 13
        btn_day.pack(side="left")
        if any((date_start, date_end)):
            btn_day["bg"] = conf.sel_color
        btn_day.cmd(lambda e: FilterWin())

        if any((date_start, date_end)):
            reset = CButton(self.thumbnails, text="Сброс")
            reset.pack(pady=(15, 0))
            reset.cmd(lambda e: self.reset_filter_cmd())

        for dates, img_list in thumbs.items():
            thumbs_title = CLabel(
                self.thumbnails,
                text=f"{dates}, всего: {len(img_list)}",
                anchor="w",
                justify="left",
                )
            thumbs_title["font"] = ('San Francisco Pro', 18, 'bold')
            thumbs_title.pack(anchor="w", pady=(30, 0), padx=2)

            w = self.size * self.clmns
            h = self.size * (math.ceil(len(img_list) / self.clmns))
            empty = Image.new("RGBA", (w, h), color=conf.bg_color)

            row, clmn = 0, 0
            for x, (img, src) in enumerate(img_list, 1):

                self.all_src.append(src)
                self.all_thumbs.setdefault(
                    dates, dict()
                    )[(clmn//self.size, row//self.size)] = src

                empty.paste(img, (clmn, row))

                clmn += self.size
                if x % self.clmns == 0:
                    row += self.size
                    clmn = 0

            img = ImageTk.PhotoImage(empty)
            img_lbl = CLabel(self.thumbnails, image=img, text=dates)
            img_lbl.pack(anchor="w")
            img_lbl.image_names = img
            img_lbl.bind('<Button-1>', partial(self.click))
            img_lbl.bind("<Button-2>", partial(self.r_click))

        if summary >= 150:
            more_btn = CButton(self.thumbnails, text="Показать еще")
            more_btn.cmd(lambda e: self.show_more_cmd())
            more_btn.pack(pady=(15, 0))

        self.thumbnails.pack(expand=1, fill=tkinter.BOTH)

    def img_viewer_cmd(self, src, all_src, e):
        ImgViewer(src, all_src)

    def show_more_cmd(self):
        conf.limit += 150
        self.reload_without_scroll()

    def reset_filter_cmd(self):
        global date_start, date_end

        date_start = None
        date_end = None

        self.reload_without_scroll()

    def decect_resize(self, e):
        if self.resize_task:
            conf.root.after_cancel(self.resize_task)
        self.resize_task = conf.root.after(250, self.update_thumbnails)

    def update_thumbnails(self):
        old_w = conf.root_w
        new_w = conf.root.winfo_width()

        if new_w != old_w:
            conf.root_w = new_w

            if self.clmns != self.clmns_count():
                w, h = conf.root.winfo_width(), conf.root.winfo_height()
                conf.root_w, conf.root_h = w, h
                conf.root.update_idletasks()
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
        clmns = (conf.root_w - conf.menu_w) // conf.thumb_size
        return 1 if clmns == 0 else clmns

    def decode_thumbs(self, thumbs: tuple):
        result = []
        for blob, src, modified in thumbs:
            try:
                decoded = decode_image(blob)
                cropped = crop_image(decoded)
                img = convert_to_rgb(cropped)
                result.append((img, src, modified))

            except Exception:
                print(traceback.format_exc())

        return result

    def create_thumbs_dict(self, thumbs: list):
        thumbs_dict = {}
        for img, src, modified in thumbs:
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

            thumbs_dict.setdefault(t, []).append((img, src))

        return thumbs_dict

    def click(self, e: tkinter.Event):
        try:
            clmn, row = e.x//self.size, e.y//self.size
            src = self.all_thumbs[e.widget.cget("text")][(clmn, row)]
        except KeyError:
            return

        ImgViewer(src, self.all_src)

    def r_click(self, e: tkinter.Event):
        try:
            clmn, row = e.x//self.size, e.y//self.size
            src = self.all_thumbs[e.widget.cget("text")][(clmn, row)]
        except KeyError:
            return

        ContextMenu(src, self.all_src, e)