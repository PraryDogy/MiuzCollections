from . import (Dbase, ImageTk, Thumbs, calendar, cfg, convert_to_rgb,
               crop_image, datetime, decode_image, find_jpeg, find_tiff,
               get_coll_name, partial, place_center, sqlalchemy, tkinter,
               tkmacosx, traceback)
from .img_viewer import ImgViewer
from .widgets import *
from tkcalendar import Calendar

__all__ = (
    "Thumbnails",
    )

months = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь"}

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

day_value: datetime = None
month_value: datetime = None
sel_btn = None


def clmns_count():
    clmns = (cfg.config['ROOT_W'] - 180) // cfg.THUMB_SIZE
    return 1 if clmns == 0 else clmns


def decode_thumbs(thumbs: tuple):
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

def create_thumbs_dict(thumbs: list):
    thumbs_dict = {}
    for img, src, modified in thumbs:
        coll = get_coll_name(src)
        t = datetime.fromtimestamp(modified).date()

        if day_value:
            t = f"{t.day} {months_day[t.month]} {t.year}"
        else:
            t = f"{months[t.month]} {t.year}"

        thumbs_dict.setdefault((coll, t), []).append((img, src))

    return thumbs_dict


def stamp_month():
    _, t_end = calendar.monthrange(
        int(month_value.year), int(month_value.month)
        )

    start = f"{1}-{month_value.month}-{month_value.year}"
    start = datetime.strptime(start, "%d-%m-%Y")

    end = f"{t_end}-{month_value.month}-{month_value.year}"
    end = datetime.strptime(end, "%d-%m-%Y")

    return (datetime.timestamp(start), datetime.timestamp(end))


def stamp_day():
    start = datetime.combine(day_value.date(), datetime.min.time())
    end = datetime.combine(
        day_value.date(), datetime.max.time().replace(microsecond=0)
        )
    return int(start.timestamp()), int(end.timestamp())


def create_query():
    q = sqlalchemy.select(
        Thumbs.img150, Thumbs.src, Thumbs.modified
        ).limit(cfg.LIMIT).order_by(-Thumbs.modified)

    if cfg.config["CURR_COLL"] != "last":
        q = q.filter(Thumbs.collection == cfg.config["CURR_COLL"])

    if day_value:
        t = stamp_day()
        q = q.filter(Thumbs.modified > t[0])
        q = q.filter(Thumbs.modified < t[1])
    
    elif month_value:
        t = stamp_month()
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


class CComboBox(tkmacosx.SFrame):
    def __init__(self, master, items_list):
        super().__init__(
            master,
            bg=cfg.BG,
            scrollbarwidth=5,
            width=100
            )

        for i in items_list:
            d = CLabel(
                self, text=str(i), anchor="w", width=10, bg=cfg.BUTTON,
                padx=5
                )
            d["bg"] = cfg.BUTTON

            d.pack(anchor="w", padx=(5, 0))
            d.bind("<ButtonRelease-1>", partial(self.cmd, d))

        self.btns = self.winfo_children()
        self.var = None

    def cmd(self, btn, e):
        global sel_btn
        for i in self.btns:
            i["bg"] = cfg.BUTTON
        btn['bg'] = cfg.SELECTED
        self.var = btn["text"]


class SelectDay(CWindow):
    def __init__(self, is_day = True):
        super().__init__()
        self.is_day = is_day
        self.title("Фильтр по дате")

        combo_frame = CFrame(self)
        combo_frame.pack()

        if self.is_day:
            self.d = CComboBox(combo_frame, [i for i in range(1, 32)])
            self.d.pack(side="left")

        self.m = CComboBox(combo_frame, months.values())
        self.m.pack(side="left")

        self.y = CComboBox(
            combo_frame,
            [i for i in range(2015, datetime.today().year + 1)]
            )
        self.y.pack(side="left")

        CSep(self).pack(fill="x", pady=15)

        btn_frame = CFrame(self)
        btn_frame.pack()

        btn_ok = CButton(btn_frame, text="Ок")
        btn_ok.cmd(lambda e: self.ok_cmd())
        btn_ok.pack(side="left", padx=(0, 15))

        btn_cancel = CButton(btn_frame, text="Отмена")
        btn_cancel.cmd(lambda e: self.cancel_cmd())
        btn_cancel.pack(side="left")

        cfg.ROOT.update_idletasks()

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def cancel_cmd(self):
        self.destroy()
        cfg.ROOT.focus_force()

    def ok_cmd(self):
        global day_value, month_value, d_btn, m_btn, y_btn

        btns = [self.m.var, self.y.var]
        if self.is_day:
            btns.insert(0, self.d.var)

        if all(i for i in btns):

            month = {v: k for k, v in months.items()}[self.m.var]

            if self.is_day:
                day_value = datetime(int(self.y.var), month, int(self.d.var))
                month_value = None
            else:
                month_value = datetime(int(self.y.var), month, 1)
                day_value = None

            cfg.THUMBNAILS.reload_thumbnails()
            self.destroy()
            cfg.ROOT.focus_force()


class Thumbnails(CFrame):
    def __init__(self, master):
        super().__init__(master)
        cfg.THUMBNAILS = self
        self.clmns = 1

        cfg.ROOT.update_idletasks()

        self.load_scrollable()
        self.load_thumbnails()

        cfg.ROOT.bind('<Configure>', self.decect_resize)
        self.resize_task = None

    def decect_resize(self, e):
        if self.resize_task:
            cfg.ROOT.after_cancel(self.resize_task)
        self.resize_task = cfg.ROOT.after(250, self.update_gui)

    def update_gui(self):
        old_w = cfg.config['ROOT_W']
        new_w = cfg.ROOT.winfo_width()

        if new_w != old_w:
            cfg.config['ROOT_W'] = new_w

            if self.clmns != clmns_count():
                w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
                cfg.config['ROOT_W'], cfg.config['ROOT_H'] = w, h
                cfg.ROOT.update_idletasks()
                self.reload_thumbnails()


    def load_scrollable(self):
        self.scroll_parrent = CFrame(self)
        self.scroll_parrent.pack(expand=1, fill=tkinter.BOTH)

        self.scrollable = tkmacosx.SFrame(
            self.scroll_parrent, bg=cfg.BG, scrollbarwidth=7)
        self.scrollable.pack(expand=1, fill=tkinter.BOTH)

    def load_thumbnails(self):
        global btn_day, btn_month

        self.thumbnails = CFrame(self.scrollable)

        if cfg.config["CURR_COLL"] == "last":
            txt = "Все коллекции"
        else:
            txt = cfg.config["CURR_COLL"]

        title = CLabel(self.thumbnails, text=txt)
        title.configure(font=('San Francisco Pro', 45, 'bold'))
        title.pack()

        subtitle = CLabel(self.thumbnails)
        subtitle.configure(font=('San Francisco Pro', 13, 'normal'))
        subtitle.pack(pady=(0, 15))

        btns_frame = CFrame(self.thumbnails)
        btns_frame.pack()

        btn_day = CButton(btns_frame, text = "Фильтр за день")
        btn_day["width"] = 13
        btn_day.pack(side="left")
        if day_value:
            btn_day["bg"] = cfg.SELECTED

        CSep(btns_frame).pack(fill="y", side="left", padx=15)

        btn_month = CButton(btns_frame, text = "Фильтр за месяц")
        btn_month["width"] = 13
        btn_month.pack(side="left")
        if month_value:
            btn_month["bg"] = cfg.SELECTED

        btn_day.cmd(lambda e: SelectDay())
        btn_month.cmd(lambda e: SelectDay(is_day=False))

        self.clmns = clmns_count()
        load_db = Dbase.conn.execute(create_query()).fetchall()
        thumbs = decode_thumbs(load_db)
        all_src = [src for _, src, _ in thumbs]
        thumbs: dict = create_thumbs_dict(thumbs)
        summary = len(load_db)

        if any((day_value, month_value)):
            if day_value:
                t = f"{day_value.day} {months_day[day_value.month]} {day_value.year}"
            elif month_value:
                t = f"{months[month_value.month]} {month_value.year}"

            subtitle["text"] = f"{t}, всего: {summary}"
            reset = CButton(self.thumbnails, text="Сброс")
            reset.pack(pady=(15, 0))
            reset.cmd(lambda e: self.reset_filter_cmd())
        else:
            subtitle["text"] = f"Всего: {summary}"

        for (coll, t), img_list in thumbs.items():

            if cfg.config["CURR_COLL"] == "last":
                title = CLabel(self.thumbnails, text=coll)
                title["font"] = ('San Francisco Pro', 26, 'bold')
                title.pack(anchor="w", pady=(30, 0))

            subtitle = CLabel(self.thumbnails, text=f"{t}, всего: {len(img_list)}")
            subtitle.configure(
                font=('San Francisco Pro', 13, 'normal'),
                )
            subtitle.pack(anchor="w")
            if cfg.config["CURR_COLL"] != "last":
                subtitle.pack(pady=(30, 0))

            img_row = CFrame(self.thumbnails)
            img_row.pack(fill = tkinter.X, expand=1, anchor=tkinter.W)

            for x, (img, src) in enumerate(img_list, 1):

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
                thumb.cmd(partial(self.img_viewer, src, all_src))

                ContextMenu(thumb, src, all_src)

                if x % self.clmns == 0:
                    img_row = CFrame(self.thumbnails)
                    img_row.pack(fill=tkinter.Y, expand=1, anchor=tkinter.W)

        if summary >= 150:
            more_btn = CButton(self.thumbnails, text="Показать еще")
            more_btn.cmd(lambda e: self.show_more(e))
            more_btn.pack(pady=(15, 0))

        self.thumbnails.pack(expand=1, fill=tkinter.BOTH)

    def img_viewer(self, src, all_src, e):
        ImgViewer(src, all_src)

    def reload_scrollable(self):
        global day_value, month_value

        day_value = None
        month_value = None

        self.scroll_parrent.destroy()
        self.load_scrollable()

    def reload_thumbnails(self):
        self.thumbnails.destroy()
        self.load_thumbnails()

    def show_more(self, e: tkinter.Event):
        cfg.LIMIT += 150
        self.reload_thumbnails()

    def reset_filter_cmd(e):
        global day_value, month_value

        day_value = None
        month_value = None

        cfg.THUMBNAILS.reload_thumbnails()
