import calendar
import re
import tkinter
from datetime import datetime

from cfg import cnf

from .utils import *
from .widgets import *


class CCalendarEntry(CWindow):
    def entry_win(self, parrent: tkinter.Toplevel, e=None):
        self.win_entry = CWindow()
        self.win_entry.title(cnf.lng.enter_date)
        self.win_entry.minsize(255, 118)
        place_center(parrent, self.win_entry, 255, 118)
        self.win_entry.protocol(
            "WM_DELETE_WINDOW", lambda: self.close_entry(parrent)
            )
        self.win_entry.bind("<Escape>", lambda e: self.close_entry(parrent))

        cust_l = CLabel(self.win_entry, text=cnf.lng.d_m_y)
        cust_l.pack(pady=(0, 5))

        var = tkinter.StringVar(value=f"{self.dd}.{self.mm}.{self.yy}")
        entry = tkinter.Entry(
            self.win_entry,
            width=15,
            textvariable=var,
            bg=cnf.dgray_color,
            insertbackground="white",
            fg=cnf.fg_color,
            highlightthickness=0,
            justify="center",
            selectbackground=cnf.btn_color,
            border=1
            )
        entry.focus_force()
        entry.icursor(10)
        entry.selection_range(0, "end")
        entry.pack(ipady=2)

        btns = CFrame(self.win_entry)
        btns.pack(pady=(15, 0))

        ok = CButton(btns, text=cnf.lng.ok, fg=cnf.dgray_color)
        ok.pack(side="left", padx=(0, 15))

        cancel = CButton(btns, text=cnf.lng.cancel)
        cancel.pack(side="left")
        cancel.bind(
            "<ButtonRelease-1>",
            lambda e: self.close_entry(parrent))

        var.trace("w", lambda *args: self.character_limit(parrent, var, ok))
        cnf.root.update_idletasks()
        self.win_entry.grab_set_global()

    def character_limit(
            self, parrent: tkinter.Toplevel, var:tkinter.StringVar,
            ok: tkinter.Label
            ):

        t = var.get()
        t_reg = re.match(r"\d{,2}\W\d{,2}\W\d{4}", t)

        if t_reg:
            t = re.sub("\W", ".", t_reg.group(0))
            var.set(t)

        try:
            self.cust_date = datetime.strptime(t, "%d.%m.%Y")
            ok.configure(fg=cnf.fg_color)
            ok.bind(
                "<ButtonRelease-1>",
                lambda e: self.ok_entry(parrent)
                )
            self.win_entry.bind(
                "<Return>",
                lambda e: self.ok_entry(parrent)
                )

        except ValueError:
            ok.configure(fg=cnf.dgray_color)
            ok.unbind("<ButtonRelease-1>")
            self.win_entry.unbind("<Return>")

            if len(t) > 10:
                var.set(t[:10])

    def ok_entry(self, parrent: tkinter.Toplevel):
        self.yy, self.mm, self.dd = tuple(self.cust_date.timetuple())[:3]

        try:
            self.change_title()
            self.set_my_date()
            self.fill_days()
            cnf.set_calendar_title()
        except tkinter.TclError:
            print("enter custom date widgets calendar error title change")

        self.close_entry(parrent)

    def close_entry(self, parrent: tkinter.Toplevel):
        self.win_entry.grab_release()
        self.win_entry.destroy()
        parrent.focus_force()
        parrent.grab_set_global()


class CCalendar(CFrame, CCalendarEntry):
    def __init__(self, master: tkinter.Frame, my_date: datetime):
        super().__init__(master)

        self.my_date = my_date
        self.today = datetime.today().date()
        self.curr_btn = tkinter.Label
        self.btns = []

        if not self.my_date:
            self.my_date = self.today

        self.yy, self.mm, self.dd = tuple(self.my_date.timetuple())[:3]

        self.calendar = self.load_calendar(master)
        self.calendar.pack()

    def load_calendar(self, master: tkinter.Frame):
        parrent = CFrame(self)

        self.all_btns = []
        f = ("San Francisco Pro", 15, "bold")

        titles = CFrame(parrent)
        titles.pack(pady=5)

        prev_m = CButton(titles, text="<", width=6, font=f, bg=cnf.bg_color)
        prev_m.pack(side="left")
        prev_m.cmd(self.switch_month)
        self.all_btns.append(prev_m)

        self.title = CLabel(
            titles, name=str(self.my_date.month), width=13, font=f
            )
        self.change_title()
        self.title.pack(side="left")
        self.title.bind(
            "<ButtonRelease-1>",
            lambda e: self.entry_win(master.winfo_toplevel())
            )
        self.title.bind(
            "<Enter>",
            lambda e: self.title.configure(bg=cnf.blue_color)
            )
        self.title.bind(
            "<Leave>",
            lambda e: self.title.configure(bg=cnf.bg_color)
            )
        self.all_btns.append(self.title)

        next_m = CButton(titles, text=">", width=6, font=f, bg=cnf.bg_color)
        next_m.pack(side="left")
        next_m.cmd(self.switch_month)
        self.all_btns.append(next_m)

        row = CFrame(parrent)
        row.pack()

        for i in cnf.lng.calendar_days:
            lbl = CButton(row, text=i, width=4, height=2)
            lbl.pack(side="left")
            self.all_btns.append(lbl)

        sep = CSep(parrent, bg=cnf.bg_color, height=2)
        sep.pack(fill="x")

        row = CFrame(parrent)
        row.pack()

        for i in range(1, 43):
            lbl = CButton(row, width=4, height=2)
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
                btn.configure(text=day, bg=cnf.btn_color)
            else:
                btn.configure(text="", bg=cnf.bg_color)
            if btn.cget("text") == self.dd:
                btn.configure(bg=cnf.lgray_color)
                self.curr_btn = btn

    def change_title(self):
        mtitle_t = (
            f"{self.dd} "
            f"{cnf.lng.months_case[self.mm]} "
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
        if e.widget.cget("text"):
            self.curr_btn.configure(bg=cnf.btn_color)
            self.curr_btn = e.widget
            self.curr_btn.configure(bg=cnf.lgray_color)
            self.dd = int(e.widget.cget("text"))
            self.set_my_date()
            self.change_title()
            cnf.set_calendar_title()

    def switch_month(self, e=None):
        if e.widget.cget("text") != "<":
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
        cnf.set_calendar_title()

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
        self.title(cnf.lng.filter)
        self.minsize(633, 666)
        place_center(cnf.root, self, 633, 666)
        self.protocol("WM_DELETE_WINDOW", self.close_filter)
        self.bind("<Escape>", self.close_filter)
        self.bind("<Return>", self.ok_filter)

        f = ("San Francisco Pro", 17, "bold")
        self.reseted = False
        self.date_changed = False

        calendar_frames = CFrame(self)
        calendar_frames.pack()

        left_frame = CFrame(calendar_frames)
        left_frame.pack(side="left", padx=(0, 15))

        left_title = CLabel(left_frame, text=cnf.lng.start, font=f)
        left_title.pack()

        self.l_calendar = CCalendar(left_frame, cnf.start)
        self.l_calendar.pack()

        right_frame = CFrame(calendar_frames)
        right_frame.pack(side="left")

        right_title = CLabel(right_frame, text=cnf.lng.end, font=f)
        right_title.pack()

        self.r_calendar = CCalendar(right_frame, cnf.end)
        self.r_calendar.pack()

        if any((cnf.start, cnf.end)):
            cals_t = f"{cnf.named_start} - {cnf.named_end}"
        else:
            cals_t = cnf.lng.dates_not_sel
        self.cals_titles = CLabel(self, text=cals_t, font=f)
        self.cals_titles.pack()

        cals_reset = CButton(self, text=cnf.lng.reset)
        cals_reset.pack(pady=(15, 0))
        cals_reset.cmd(self.cals_titles_reset)

        CSep(self).pack(fill="x", padx=15, pady=15)

        grop_frame = CFrame(self)
        grop_frame.pack()

        self.product = CButton(grop_frame, text=cnf.lng.product)
        if cnf.product:
            self.product.configure(bg=cnf.lgray_color)
        self.product.pack(side="left")
        self.product.cmd(self.product_cmd)

        self.models = CButton(grop_frame, text=cnf.lng.models)
        if cnf.models:
            self.models.configure(bg=cnf.lgray_color)
        self.models.pack(side="left", padx=15)
        self.models.cmd(self.models_cmd)

        self.catalog = CButton(grop_frame, text=cnf.lng.catalog)
        if cnf.catalog:
            self.catalog.configure(bg=cnf.lgray_color)
        self.catalog.pack(side="left")
        self.catalog.cmd(self.catalog_cmd)

        if cnf.sort_modified:
            sort_btn_t = cnf.lng.date_changed
        else:
            sort_btn_t = cnf.lng.date_created

        self.btn_sort = CButton(self, text=sort_btn_t, width=13)
        self.btn_sort.pack(pady=(15, 0))
        self.btn_sort.cmd(self.sort_btn_cmd)

        marketing_lbl = CLabel(
            self, text="\n".join(cnf.lng.filter_descr),
            anchor="w", justify="left"
            )
        marketing_lbl.pack(anchor="w", pady=(15, 0))

        CSep(self).pack(fill="x", padx=150, pady=15)

        btns_frame = CFrame(self)
        btns_frame.pack(pady=(15, 0))

        ok_btn = CButton(btns_frame, text=cnf.lng.ok)
        ok_btn.pack(side="left", padx=15)
        ok_btn.cmd(self.ok_filter)

        cancel_btn = CButton(btns_frame, text=cnf.lng.cancel)
        cancel_btn.pack(side="left")
        cancel_btn.cmd(self.close_filter)

        cnf.set_calendar_title = self.set_calendar_title
        cnf.root.update_idletasks()
        self.grab_set_global()

    def named_date(self, date: datetime):
        day = f"{date.day} "
        month = f"{cnf.lng.months_case[date.month]} "
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
        self.cals_titles.configure(text=cnf.lng.dates_not_sel)

    def sort_btn_cmd(self, e):
        if self.btn_sort.cget("text") == cnf.lng.date_changed:
            self.btn_sort.configure(text=cnf.lng.date_created)
        else:
            self.btn_sort.configure(text=cnf.lng.date_changed)

    def product_cmd(self, e=None):
        if self.product.cget("bg") == cnf.lgray_color:
            self.product.configure(bg=cnf.btn_color)
        else:
            self.product.configure(bg=cnf.lgray_color)

    def catalog_cmd(self, e=None):
        if self.catalog.cget("bg") == cnf.lgray_color:
            self.catalog.configure(bg=cnf.btn_color)
        else:
            self.catalog.configure(bg=cnf.lgray_color)

    def models_cmd(self, e=None):
        if self.models.cget("bg") == cnf.lgray_color:
            self.models.configure(bg=cnf.btn_color)
        else:
            self.models.configure(bg=cnf.lgray_color)

    def ok_filter(self, e=None):
        if self.date_changed:
            cnf.start = self.l_calendar.my_date
            cnf.end = self.r_calendar.my_date
            cnf.named_start = self.named_date(cnf.start)
            cnf.named_end = self.named_date(cnf.end)

        if self.reseted:
            cnf.start = None
            cnf.end = None

        if self.product.cget("bg") == cnf.lgray_color:
            cnf.product = True
        else:
            cnf.product = False

        if self.models.cget("bg") == cnf.lgray_color:
            cnf.models = True
        else:
            cnf.models = False

        if self.catalog.cget("bg") == cnf.lgray_color:
            cnf.catalog = True
        else:
            cnf.catalog = False

        if not any((cnf.product, cnf.models, cnf.catalog)):
            cnf.product = True
            cnf.models = True
            cnf.catalog = True

        if self.btn_sort.cget("text") == cnf.lng.date_created:
            cnf.sort_modified = False
        else:
            cnf.sort_modified = True

        self.grab_release()
        self.destroy()
        cnf.root.focus_force()
        cnf.search_var.set("")
        cnf.reload_scroll()

    def close_filter(self, e=None):
        self.grab_release()
        self.destroy()
        cnf.root.focus_force()