import calendar
import re
import tkinter
from datetime import datetime

from cfg import cnf

from .widgets import *

try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal

from utils import SysUtils

__all__ = ("CalendarWin",)
win = {"main": False, "entry": False}



class CalendarBase(CFrame, SysUtils):
    def __init__(self, master: tkinter.Frame, my_date: datetime):
        CFrame.__init__(self, master=master)

        self.my_date = my_date
        self.today = datetime.today().date()
        self.curr_btn = tkinter.Label
        self.btns = []

        if not self.my_date:
            self.my_date = self.today

        self.yy, self.mm, self.dd = tuple(self.my_date.timetuple())[:3]

        self.calendar = self.load_calendar()
        self.calendar.pack()

    def load_calendar(self) -> CFrame:
        parrent = CFrame(master=self)

        self.all_btns = []
        f = ("San Francisco Pro", 15, "bold")

        titles = CFrame(parrent)
        titles.pack(pady=5)

        prev_m = CButton(master=titles, text="<", width=0, font=f,
                         fg_color=cnf.bg_color)
        prev_m.pack(side="left")
        prev_m.cmd(lambda e: self.switch_month(lbl=prev_m))
        self.all_btns.append(prev_m)

        self.title = CLabel(master=titles, name=str(self.my_date.month),
                            width=13, font=f)
        self.title.pack(side="left")
        self.change_title()

        self.title.bind(sequence="<Enter>",
                        func=lambda e:
                        self.title.configure(fg=cnf.blue_color))
        self.title.bind(sequence="<Leave>",
                        func=lambda e:
                        self.title.configure(fg=cnf.fg_color))
        self.all_btns.append(self.title)

        next_m = CButton(master=titles, text=">", width=0, font=f,
                         fg_color=cnf.bg_color)
        next_m.pack(side="left")
        next_m.cmd(lambda e: self.switch_month(lbl=next_m))
        self.all_btns.append(next_m)

        row = CFrame(master=parrent)
        row.pack()

        for i in cnf.lng.calendar_days:
            lbl = CButton(master=row, text=i, width=40, height=40,
                          corner_radius=0)
            lbl.pack(side="left")
            self.all_btns.append(lbl)

        sep = CSep(master=parrent, bg=cnf.bg_color, height=2)
        sep.pack(fill="x")

        row = CFrame(master=parrent)
        row.pack()

        for i in range(1, 43):
            lbl = CButton(master=row, width=40, height=40, corner_radius=0)
            lbl.pack(side="left")

            if i % 7 == 0:
                row = CFrame(master=parrent)
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
            btn: CButton
            if day:
                btn.configure(text=day, fg_color=cnf.btn_color)
                btn.uncmd()
                btn.cmd(lambda e, btn=btn: self.switch_day(lbl=btn))
            else:
                btn.configure(text="", fg_color=cnf.bg_color)
            if btn.cget(attribute_name="text") == self.dd:
                btn.configure(fg_color=cnf.lgray_color)
                self.curr_btn = btn

    def change_title(self):
        t = f"{self.dd} {cnf.lng.months_case[str(self.mm)]} {self.yy}"
        self.title.configure(text=t)

    def set_my_date(self):
        try:
            self.my_date = datetime(self.yy, self.mm, self.dd).date()
        except ValueError:
            self.print_err()
            max_day = calendar.monthrange(self.yy, self.mm)[1]
            self.my_date = datetime(self.yy, self.mm, max_day).date()

        self.yy, self.mm, self.dd = tuple(self.my_date.timetuple())[:3]

    def switch_day(self, lbl: CButton):
        if lbl.cget(attribute_name="text"):
            self.curr_btn.configure(fg_color=cnf.btn_color)
            self.curr_btn = lbl
            self.curr_btn.configure(fg_color=cnf.lgray_color)
            self.dd = int(lbl.cget(attribute_name="text"))
            self.set_my_date()
            self.change_title()
            cnf.set_calendar_title()

    def switch_month(self, lbl: CButton):
        if lbl.cget(attribute_name="text") != "<":
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


class CCalendar(CalendarBase, SysUtils):
    def __init__(self, master: tkinter, my_date: datetime):
        CalendarBase.__init__(self, master=master, my_date=my_date)
        self.title.bind(sequence="<ButtonRelease-1>",
                        func=lambda e:
                        self.entry_win(master.winfo_toplevel())
                        )

    def entry_win(self, master: tkinter.Toplevel, e: tkinter.Event = None):
        w, h = 255, 120

        if win["entry"]:
            win["entry"].destroy()
            win["entry"] = False

        self.win_entry = CWindow()
        win["entry"] = self.win_entry

        self.win_entry.title(string=cnf.lng.enter_date)
        self.win_entry.minsize(width=w, height=h)
        self.win_entry.place_center(w=w, h=h, below_win=master)
        self.win_entry.protocol(name="WM_DELETE_WINDOW",
                                func=lambda: self.close_entry(parrent=master))
        self.win_entry.bind(sequence="<Escape>",
                            func=lambda e: self.close_entry(parrent=master))

        cust_l = CLabel(master=self.win_entry, text=cnf.lng.d_m_y)
        cust_l.pack(pady=(0, 5))

        var = tkinter.StringVar(value=f"{self.dd}.{self.mm}.{self.yy}")

        entry = CEntry(master=self.win_entry, textvariable=var,
                       width=150, justify="center")
        entry.pack()
        entry.focus_force()
        entry.icursor(index=10)
        entry.select_adjust(index=10)

        btns = CFrame(master=self.win_entry)
        btns.pack(pady=(15, 0))

        ok = CButton(master=btns, text=cnf.lng.ok)
        ok.pack(side="left", padx=(0, 15))
        ok.bind(sequence="<ButtonRelease-1>",
                command=lambda e: self.ok_entry(parrent=master))
        self.win_entry.bind(sequence="<Return>",
                            func=lambda e: self.ok_entry(parrent=master))
        t = var.get()
        self.cust_date = datetime.strptime(t, "%d.%m.%Y")

        cancel = CButton(master=btns, text=cnf.lng.cancel)
        cancel.pack(side="left")
        cancel.bind(sequence="<ButtonRelease-1>",
                    command=lambda e: self.close_entry(parrent=master))

        var.trace(mode="w", callback=lambda *args:
                  self.character_limit(parrent=master, var=var, btn=ok))

    def character_limit(self, parrent: tkinter.Toplevel,
                        var:tkinter.StringVar, btn: CButton):

        t = var.get()
        t_reg = re.match(r"\d{,2}\W\d{,2}\W\d{4}", t)

        if t_reg:
            t = re.sub("\W", ".", t_reg.group(0))
            var.set(value=t)

        try:
            self.cust_date = datetime.strptime(t, "%d.%m.%Y")
            btn.configure(text_color=cnf.fg_color)
            btn.bind(sequence="<ButtonRelease-1>",
                     command=lambda e: self.ok_entry(parrent=parrent))
            self.win_entry.bind(sequence="<Return>",
                                func=lambda e: self.ok_entry(parrent=parrent))

        except ValueError:
            # self.print_err()
            btn.configure(text_color=cnf.dgray_color)
            btn.unbind(sequence="<ButtonRelease-1>")
            self.win_entry.unbind(sequence="<Return>")

            if len(t) > 10:
                var.set(value=t[:10])

    def ok_entry(self, parrent: tkinter.Toplevel):
        self.yy, self.mm, self.dd = tuple(self.cust_date.timetuple())[:3]

        try:
            self.change_title()
            self.set_my_date()
            self.fill_days()
            cnf.set_calendar_title()
        except tkinter.TclError:
            self.print_err()

        self.close_entry(parrent=parrent)

    def close_entry(self, parrent: tkinter.Toplevel):
        win["entry"] = False
        self.win_entry.destroy()
        parrent.focus_force()


class CalendarWin(CWindow, SysUtils):
    def __init__(self):
        w, h = 635, 490

        for i in win.values():
            if i:
                i.destroy()
                i = False

        CWindow.__init__(self)
        win["main"] = self
        self.title(string=cnf.lng.filter)
        self.minsize(width=w, height=h)
        self.place_center(w=w, h=h)
        self.protocol(name="WM_DELETE_WINDOW", func=self.close_filter)
        self.bind(sequence="<Escape>", func=self.close_filter)
        self.bind(sequence="<Return>", func=self.ok_filter)

        f = ("San Francisco Pro", 17, "bold")
        self.reseted = False
        self.date_changed = False

        calendar_frames = CFrame(master=self)
        calendar_frames.pack()

        left_frame = CFrame(master=calendar_frames)
        left_frame.pack(side="left", padx=(0, 15))

        left_title = CLabel(master=left_frame, text=cnf.lng.start, font=f)
        left_title.pack()

        self.l_calendar = CCalendar(master=left_frame, my_date=cnf.date_start)
        self.l_calendar.pack()

        right_frame = CFrame(master=calendar_frames)
        right_frame.pack(side="left")

        right_title = CLabel(master=right_frame, text=cnf.lng.end, font=f)
        right_title.pack()

        self.r_calendar = CCalendar(master=right_frame, my_date=cnf.date_end)
        self.r_calendar.pack()

        if any((cnf.date_start, cnf.date_end)):
            cals_t = f"{cnf.named_start} - {cnf.named_end}"
        else:
            cals_t = cnf.lng.dates_not_sel
        self.cals_titles = CLabel(master=self, text=cals_t, font=f)
        self.cals_titles.pack()

        cals_reset = CButton(master=self, text=cnf.lng.reset_dates)
        cals_reset.pack(pady=(15, 0))
        cals_reset.cmd(self.cals_titles_reset)

        CSep(self).pack(fill="x", padx=150, pady=15)

        btns_frame = CFrame(master=self)
        btns_frame.pack(pady=(15, 0))

        ok_btn = CButton(master=btns_frame, text=cnf.lng.ok)
        ok_btn.pack(side="left", padx=15)
        ok_btn.cmd(self.ok_filter)

        cancel_btn = CButton(master=btns_frame, text=cnf.lng.cancel)
        cancel_btn.pack(side="left")
        cancel_btn.cmd(self.close_filter)

    def named_date(self, date: datetime) -> Literal["ex: 10 jan 1991"]:
        day = f"{date.day} "
        month = f"{cnf.lng.months_case[str(date.month)]} "
        year = f"{date.year}"
        return day + month + year

    def set_calendar_title(self):
        start = self.named_date(date=self.l_calendar.my_date)
        end = self.named_date(date=self.r_calendar.my_date)
        self.cals_titles.configure(text=f"{start} - {end}")
        self.date_changed = True

    def cals_titles_reset(self, e: tkinter.Event = None):
        for i in (self.l_calendar, self.r_calendar):
            i.clicked = False
            i.reset_cal()
        self.reseted = True
        self.date_changed = False
        self.cals_titles.configure(text=cnf.lng.dates_not_sel)

    def ok_filter(self, e: tkinter.Event = None):
        if self.date_changed:
            cnf.date_start = self.l_calendar.my_date
            cnf.date_end = self.r_calendar.my_date
            cnf.named_start = self.named_date(date=cnf.date_start)
            cnf.named_end = self.named_date(date=cnf.date_end)

        if self.reseted:
            cnf.date_start = None
            cnf.date_end = None

        self.destroy()
        cnf.root.focus_force()
        cnf.search_var.set("")
        cnf.reload_filters()
        cnf.reload_scroll()

        for i in win.values():
            i = False

    def close_filter(self, e: tkinter.Event = None):
        for i in win.values():
            if i:
                i.destroy()
                i = False
        self.destroy()
        cnf.root.focus_force()