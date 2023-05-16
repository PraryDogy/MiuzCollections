import tkinter
from gui.widgets import *
import cfg
from test import CCalendar
from datetime import datetime


root = tkinter.Tk()
root["bg"] = cfg.BG

d = datetime.today()


class FilterWin(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        left = CFrame(self)
        left.pack(side="left", padx=(0, 15))

        first = CLabel(left, text="Начало")
        first.pack()

        one = CCalendar(left, d)
        one.pack()


FilterWin()
root.mainloop()