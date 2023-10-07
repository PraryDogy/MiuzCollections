import calendar
import tkinter
from datetime import datetime

from cfg import conf
from .utils import *

from .globals import Globals
from .widgets import *


class CCalendarEntry(CWindow):
    def cust_date_win(self, e=None):
        self.win_cust = CWindow()
        self.win_cust.title(conf.lang.cust_title)
        self.win_cust.protocol("WM_DELETE_WINDOW", self.cust_can_cmd)
        self.win_cust.bind('<Escape>', self.cust_can_cmd)
        self.bind('<Command-q>', on_exit)

        cust_l = CLabel(self.win_cust, text=conf.lang.cust_l)
        cust_l.pack(pady=(0, 5))

        var_t = f"{self.dd}.{self.mm}.{self.yy}"
        var = tkinter.StringVar(value=var_t)
        self.cust_ent = tkinter.Entry(
            self.win_cust,
            width=15,
            textvariable=var,
            bg=conf.ent_color,
            insertbackground="white",
            fg=conf.fg_color,
            highlightthickness=0,
            justify="center",
            selectbackground=conf.btn_color,
            border=1
            )
        self.cust_ent.pack(ipady=2)
        var.trace("w", lambda *args: self.character_limit(var))
        self.cust_ent.icursor(10)
        self.cust_ent.selection_range(0, "end")

        btns = CFrame(self.win_cust)
        btns.pack(pady=(15, 0))

        self.ok = CButton(btns, text=conf.lang.ok)
        self.ok.configure(fg=conf.hov_color)
        self.ok.pack(side="left", padx=(0, 15))

        self.cancel = CButton(btns, text=conf.lang.cancel)
        self.cancel.pack(side="left")
        self.cancel.bind("<ButtonRelease-1>", self.cust_can_cmd)

        conf.root.update_idletasks()

        under_win = self.winfo_toplevel()
        x, y = under_win.winfo_x(), under_win.winfo_y()
        xx = x + under_win.winfo_width()//2 - self.win_cust.winfo_width()//2
        yy = y + under_win.winfo_height()//2 - self.win_cust.winfo_height()//2
        self.win_cust.geometry(f'+{xx}+{yy}')

        self.win_cust.deiconify()
        self.win_cust.wait_visibility()
        self.win_cust.grab_set_global()
        self.cust_ent.focus_force()

    def character_limit(self, e:tkinter.StringVar):
        t = e.get()
        try:
            self.cust_date = datetime.strptime(t, '%d.%m.%Y')
            self.ok.configure(fg=conf.fg_color)
            self.ok.bind("<ButtonRelease-1>", self.cust_ok_cmd)
            self.win_cust.bind("<Return>", self.cust_ok_cmd)
        except ValueError:
            self.ok.configure(fg=conf.hov_color)
            self.ok.unbind("<ButtonRelease-1>")
            self.win_cust.unbind("<Return>")

            if len(t) > 10:
                e.set(t[:10])

    def cust_ok_cmd(self, e=None):
        self.yy, self.mm, self.dd = tuple(self.cust_date.timetuple())[:3]

        try:
            self.change_title()
            self.set_my_date()
            self.fill_days()
            Globals.set_calendar_title()
        except tkinter.TclError:
            print("enter custom date widgets calendar error title change")

        self.win_cust.destroy()
        focus_last_win()

    def cust_can_cmd(self, e=None):
        self.unbind_all("<ButtonRelease-1>")
        self.win_cust.destroy()
        focus_last_win()


class CCalendar(CFrame, CCalendarEntry):
    def __init__(self, master, my_date: datetime):
        super().__init__(master)

        self.my_date = my_date
        self.today = datetime.today().date()
        self.curr_btn = tkinter.Label
        self.btns = []

        if not self.my_date:
            self.my_date = self.today

        self.yy, self.mm, self.dd = tuple(self.my_date.timetuple())[:3]

        self.calendar = self.load_calendar()
        self.calendar.pack()

    def load_calendar(self):
        parrent = CFrame(self)

        self.all_btns = []
        f = ("San Francisco Pro", 15, "bold")

        titles = CFrame(parrent)
        titles.pack(pady=5)

        prev_m = CButton(titles, text="<")
        prev_m.configure(width=6, font=f, bg=conf.bg_color)
        prev_m.pack(side="left")
        prev_m.cmd(self.switch_month)
        self.all_btns.append(prev_m)

        self.title = CLabel(
            titles,
            name=str(self.my_date.month)
            )
        self.title.configure(width=13, font=f)
        self.change_title()
        self.title.pack(side="left")
        self.title.bind("<ButtonRelease-1>", self.cust_date_win)
        self.all_btns.append(self.title)

        next_m = CButton(titles, text=">")
        next_m.configure(width=6, font=f, bg=conf.bg_color)
        next_m.pack(side="left")
        next_m.cmd(self.switch_month)
        self.all_btns.append(next_m)

        row = CFrame(parrent)
        row.pack()

        for i in conf.lang.calendar_days:
            lbl = CButton(row, text = i)
            lbl.configure(width=4, height=2)
            lbl.pack(side="left")
            self.all_btns.append(lbl)

        sep = CSep(parrent)
        sep.configure(bg=conf.bg_color, height=2)
        sep.pack(fill="x")

        row = CFrame(parrent)
        row.pack()

        for i in range(1, 43):
            lbl = CButton(row)
            lbl.configure(width=4, height=2)
            lbl.pack(side="left")
            lbl.cmd(self.switch_day)

            if i % 7 == 0:
                row = CFrame(parrent)
                row.pack(anchor="w")

            self.btns.append(lbl)
            self.all_btns.append(lbl)

        self.fill_days()

        return parrent

    def create_days(self):
        first_weekday = datetime.weekday(datetime(self.yy, self.mm, 1))
        month_len = calendar.monthrange(self.yy, self.mm)[1] + 1

        days = [None for i in range(first_weekday)]
        days.extend([i for i in range(1, month_len)])
        days.extend([None for i in range(42 - len(days))])

        return days

    def fill_days(self):
        for day, btn in zip(self.create_days(), self.btns):
            if day:
                btn.configure(text=day, bg=conf.btn_color)
            else:
                btn.configure(text="", bg=conf.bg_color)
            if btn["text"] == self.dd:
                btn.configure(bg=conf.sel_color)
                self.curr_btn = btn

    def change_title(self):
        mtitle_t = (
            f"{self.dd} "
            f"{conf.lang.months_p[self.mm]} "
            f"{self.yy}"
            )
        self.title.configure(text=mtitle_t)

    def set_my_date(self):
        try:
            self.my_date = datetime(self.yy, self.mm, self.dd).date()
        except ValueError:
            max_day = calendar.monthrange(self.yy, self.mm)[1]
            self.my_date = datetime(self.yy, self.mm, max_day).date()

        self.yy, self.mm, self.dd = tuple(self.my_date.timetuple())[:3]

    def switch_day(self, e=None):
        if e.widget["text"]:
            self.curr_btn.configure(bg=conf.btn_color)
            self.curr_btn = e.widget
            self.curr_btn.configure(bg=conf.sel_color)
            self.dd = int(e.widget["text"])
            self.set_my_date()
            self.change_title()
            Globals.set_calendar_title()

    def switch_month(self, e=None):
        if e.widget["text"] != "<":
            self.mm += 1
        else:
            self.mm -= 1

        if self.mm > 12:
            self.mm = 1
            self.yy += 1
        elif self.mm <1:
            self.mm = 12
            self.yy -= 1

        self.set_my_date()
        self.change_title()
        self.fill_days()
        Globals.set_calendar_title()

    def reset_cal(self):
        self.dd = self.today.day
        self.mm = self.today.month
        self.yy = self.today.year

        self.set_my_date()
        self.change_title()
        self.fill_days()


class Filter(CWindow):
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

        self.l_calendar = CCalendar(left_frame, Globals.start)
        self.l_calendar.pack()

        right_frame = CFrame(calendar_frames)
        right_frame.pack(side="left")

        right_title = CLabel(right_frame, text=conf.lang.filter_end)
        right_title["font"] = f
        right_title.pack()

        self.r_calendar = CCalendar(right_frame, Globals.end)
        self.r_calendar.pack()

        if any((Globals.start, Globals.end)):
            cals_t = f"{Globals.named_start} - {Globals.named_end}"
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
        Globals.set_calendar_title = self.set_calendar_title

    def named_date(self, date: datetime):
        day = f"{date.day} "
        month = f"{conf.lang.months_p[date.month]} "
        year = f"{date.year}"
        return day + month + year

    def set_calendar_title(self):
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
            Globals.start = self.l_calendar.my_date
            Globals.end = self.r_calendar.my_date
            Globals.named_start = self.named_date(Globals.start)
            Globals.named_end = self.named_date(Globals.end)

        if self.reseted:
            Globals.start = None
            Globals.end = None

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
        conf.root.focus_force()
        Globals.reload_thumbs()

    def cancel(self):
        self.destroy()
        conf.root.focus_force()