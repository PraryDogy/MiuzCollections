from calendar import monthrange
from datetime import datetime
from functools import partial

import cfg
from gui.widgets import *

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


class CCalendar(CFrame):
    def __init__(self, master, my_date: datetime):

        super().__init__(master)
        self["bg"] = cfg.BUTTON

        self.my_date = my_date
        self.today = datetime.today().date()

        if not self.my_date:
            self.my_date = self.today

        self.calendar = self.load_calendar()
        self.calendar.pack(pady=(15, 0))

    def load_calendar(self):
        parrent = CFrame(self)
        parrent["bg"] = cfg.BUTTON

        f = ("San Francisco Pro", 15, "bold")

        titles = CFrame(parrent)
        titles["bg"] = cfg.BUTTON
        titles.pack()

        month_frame = CFrame(titles)
        month_frame["bg"] = cfg.BUTTON
        month_frame.pack(side="left")

        prev = CButton(month_frame, text="<")
        prev.configure(width=2, font=f)
        prev.pack(side="left")
        prev.cmd(lambda e: self.switch_month(prev["text"], e))

        self.m_title = CLabel(
            month_frame,
            text=months[self.my_date.month],
            name=str(self.my_date.month)
            )
        self.m_title.configure(bg=cfg.BUTTON, width=7, font=f)
        self.m_title.pack(side="left")

        next = CButton(month_frame, text=">")
        next.configure(width=2, font=f)
        next.pack(side="left")
        next.cmd(lambda e: self.switch_month(next["text"], e))

        fake = CLabel(titles, text="")
        fake["bg"] = cfg.BUTTON
        fake.pack(fill="x", side="left")

        year_frame = CFrame(titles)
        year_frame["bg"] = cfg.BUTTON
        year_frame.pack(side="left")

        prev = CButton(year_frame, text="<")
        prev.configure(width=2, font=f)
        prev.pack(side="left")
        prev.cmd(lambda e: self.switch_year(prev["text"], e))

        self.y_title = CLabel(
            year_frame,
            text=self.my_date.year,
            name=str(self.my_date.month)
            )
        self.y_title.configure(bg=cfg.BUTTON, width=7, font=f)
        self.y_title.pack(side="left")

        next = CButton(year_frame, text=">")
        next.configure(width=2, font=f)
        next.pack(side="left")
        next.cmd(lambda e: self.switch_year(next["text"], e))

        row = CFrame(parrent)
        row.pack()

        for i in ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"):
            lbl = CButton(row, text = i)
            lbl.configure(width=4, height=2)
            lbl.pack(side="left")

        row = CFrame(parrent)
        row.pack()

        self.btns = []

        for i in range(1, 42):
            lbl = CButton(row)
            lbl.configure(width=4, height=2)
            lbl.pack(side="left")
            lbl.cmd(partial(self.select_day, lbl))

            if i % 7 == 0:
                row = CFrame(parrent)
                row.pack(anchor="w")

            self.btns.append(lbl)

        self.fill_days()

        return parrent

    def create_days(self):
        first_weekday = datetime.weekday(
            datetime(self.my_date.year, self.my_date.month, 1)
            )
        month_len = monthrange(self.my_date.year, self.my_date.month)[1] + 1

        days = [None for i in range(first_weekday)]
        days.extend([i for i in range(1, month_len)])
        days.extend([None for i in range(42 - (len(days)))])

        return days

    def fill_days(self):
        days = self.create_days()

        for day, btn in zip(days, self.btns):
            if day:
                btn["text"] = day
            else:
                btn["text"] = ""
            btn["bg"] = cfg.BUTTON
            if btn["text"] == self.my_date.day:
                btn["bg"] = cfg.SELECTED

    def select_day(self, btn, e):
        if btn["text"]:
            for i in self.btns:
                i["bg"] = cfg.BUTTON
            btn["bg"] = cfg.SELECTED

            self.my_date = datetime(
                self.my_date.year,
                self.my_date.month,
                int(btn["text"])
                )

    def switch_month(self, txt, e):
        if txt != "<":
            m = self.my_date.month + 1
        else:
            m = self.my_date.month - 1

        m = 1 if m > 12 else m
        m = 12 if m < 1 else m

        self.my_date = datetime(self.my_date.year, m, self.my_date.day)
        self.m_title["text"] = months[m]
        self.fill_days()

    def switch_year(self, txt, e):
        if txt != "<":
            y = self.my_date.year + 1
        else:
            y = self.my_date.year - 1

        if y > self.today.year:
            y = 2015

        elif y < 2015:
            y = self.today.year

        self.my_date = datetime(y, self.my_date.month, self.my_date.day)

        self.y_title["text"] = y
        self.fill_days()


import tkinter
root = tkinter.Tk()
CCalendar(root, datetime(2023, 1, 1)).pack()

root.mainloop()
