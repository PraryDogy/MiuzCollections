import tkinter
from gui.widgets import *
import cfg
from test import CCalendar
from datetime import datetime


class FilterWin(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        f = ("San Francisco Pro", 17, "bold")

        self["bg"] = cfg.BG
        self.configure(padx=15)

        cal_frames = CFrame(self)
        cal_frames.pack()

        left = CFrame(cal_frames)
        left.pack(side="left", padx=(0, 15))

        first = CLabel(left, text="Начало")
        first["font"] = f
        first.pack()

        one = CCalendar(left, d)
        one.pack()

        right = CFrame(cal_frames)
        right.pack(side="left")

        second = CLabel(right, text="Конец")
        second["font"] = f
        second.pack()

        self.two = CCalendar(right, d)
        self.two.pack()

        self.oneday_btn = CButton(self, text="За один день")
        self.oneday_btn.pack(pady=(15, 0))
        self.oneday_btn.cmd(lambda e: self.oneday_cmd())
        self.oneday_value = False

        btns_frame = CFrame(self)
        btns_frame.pack(pady=(15, 0))

        ok_btn = CButton(btns_frame, text="Ок")
        ok_btn.pack(side="left", padx=15)
        ok_btn.cmd(lambda e: self.ok_cmd())

        cancel_btn = CButton(btns_frame, text="Отмена")
        cancel_btn.pack(side="left")
        cancel_btn.cmd(lambda e: self.cancel())

    def oneday_cmd(self):
        if not self.oneday_value:
            self.oneday_value = True
            self.oneday_btn["bg"] = cfg.SELECTED
            self.two.disable_calendar()

        else:
            self.oneday_value = False
            self.oneday_btn["bg"] = cfg.BUTTON
            self.two.enable_calendar()

    def ok_cmd(self):
        self.destroy()
        focus_last()

    def cancel(self):
        self.destroy()
        focus_last()

FilterWin()
cfg.ROOT.mainloop()