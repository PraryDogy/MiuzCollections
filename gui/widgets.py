from . import (Image, cfg, datetime, get_coll_name, on_exit, os, place_center,
               tkinter, sys, calendar, partial)

__all__ = (
    "CSep",
    "CButton",
    "CFrame",
    "CLabel",
    "CWindow",
    "CloseBtn",
    "AskExit",
    "SmbAlert",
    "ImageInfo",
    "MacMenu",
    "CCalendar",
    "focus_last",
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


def focus_last():
    for k, v in cfg.ROOT.children.items():
        if isinstance(v, CWindow):
            v.focus_force()
            return

    cfg.ROOT.focus_force()

class CSep(tkinter.Frame):
    def __init__(self, master: tkinter):
        tkinter.Frame.__init__(self, master, bg=cfg.BUTTON, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(
            bg=cfg.BUTTON, fg=cfg.FONT, width=11, height=1,
            font=("San Francisco Pro", 13, "normal"))

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)

    def press(self):
        self.configure(bg=cfg.SELECTED)
        cfg.ROOT.after(100, lambda: self.configure(bg=cfg.BUTTON))


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        tkinter.Frame.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BG)


class CLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(
            bg=cfg.BG,
            fg=cfg.FONT,
            font=("San Francisco Pro", 13, "normal"),
            )


class CWindow(tkinter.Toplevel):
    def __init__(self):
        tkinter.Toplevel.__init__(self)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: self.close_win())
        self.bind('<Command-w>', lambda e: self.close_win())
        self.bind('<Escape>', lambda e: self.close_win())

        if cfg.config["ASK_EXIT"] == 1:
            self.bind('<Command-q>', lambda e: AskExit())
        else:
            self.bind('<Command-q>', lambda e: on_exit())

        self.resizable(0,0)
        self.configure(bg=cfg.BG, padx=15, pady=15)

    def close_win(self):
        self.destroy()
        focus_last()


class CloseBtn(CButton):
    def __init__(self, master: tkinter.Widget, **kwargs):
        CButton.__init__(self, master, **kwargs)
        self.cmd(lambda e: self.destroy())


class AskExit(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.bind('<Return>', lambda e: on_exit())
        self.protocol("WM_DELETE_WINDOW", lambda: self.close_ask())
        self.bind('<Command-w>', lambda e: self.close_ask())
        self.bind('<Escape>', lambda e: self.close_ask())

        lbl = CLabel(self, text='Выйти?')
        lbl.pack()

        btns_frame = CFrame(self)
        btns_frame.pack()

        exit = CButton(self, text='Выйти')
        exit.cmd(lambda e: on_exit())

        cancel = CButton(self, text='Отмена')
        cancel.cmd(lambda e: self.close_ask())

        [i.configure(height=1, width=11) for i in (exit, cancel)]
        [i.pack(side=tkinter.LEFT, padx=5) for i in (exit, cancel)]

        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def close_ask(self):
        self.destroy()

    def exit_task(self):
        quit()


class SmbAlert(CWindow):
    def __init__(self):
        CWindow.__init__(self)

        txt = 'Нет подключения к сетевому диску Miuz.'
        title_lbl = CLabel(
            self, text=txt, font=('San Francisco Pro', 22, 'bold'))
        title_lbl.pack(pady=(0, 5), padx=20)

        txt2 =(
            'Рекомендации:'
            '\n- Проверьте подключение к интернету.'
            '\n- Откройте любую папку на сетевом диске,'
            '\n- Укажите правильный путь к коллекциям в настройках'
            '\n- Перезапустите приложение.'

            '\n\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        descr_lbl = CLabel(self, text=txt2, justify=tkinter.LEFT, )
        descr_lbl.pack(padx=15, pady=(0, 5))

        btn = CButton(self, text = "Закрыть")
        btn.cmd(lambda e: self.btn_cmd())
        btn.pack()

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def btn_cmd(self):
        self.destroy()
        focus_last()


class ImageInfo(CWindow):
    def __init__(self, src: str, win: tkinter.Toplevel):
        CWindow.__init__(self)
        self.win = win

        self.title("Инфо")
        self.geometry("400x110")
        self.minsize(400, 110)
        self.maxsize(800, 150)
        self.configure(padx=5, pady=5)
        self.resizable(1, 1)

        name = src.split(os.sep)[-1]
        filemod = datetime.fromtimestamp(os.path.getmtime(src))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
        w, h = Image.open(src).size
        filesize = round(os.path.getsize(src)/(1024*1024), 2)

        frame = CFrame(self)
        frame.pack(expand=True, fill="both")

        labels = {
            "Коллекция ": get_coll_name(src),
            "Имя файла ": name,
            "Дата изменения ": filemod,
            "Разрешение ": f"{w}x{h}",
            "Размер ": f"{filesize}мб",
            "Расположение ": src,
            }

        left_lbl = CLabel(
            frame,
            text = "\n".join(i for i in labels.keys()),
            justify = tkinter.RIGHT,
            anchor = tkinter.E,
            )
        left_lbl.pack(anchor=tkinter.CENTER, side=tkinter.LEFT)

        right_lbl = CLabel(
            frame,
            text = "\n".join(i for i in labels.values()),
            justify = tkinter.LEFT,
            anchor = tkinter.W,
            )
        right_lbl.pack(anchor=tkinter.CENTER, side=tkinter.LEFT)

        self.protocol("WM_DELETE_WINDOW", lambda: self.close_win())
        self.bind('<Command-w>', lambda e: self.close_win())
        self.bind('<Escape>', lambda e: self.close_win())

        cfg.ROOT.update_idletasks()

        x, y = self.win.winfo_x(), self.win.winfo_y()
        xx = x + self.win.winfo_width()//2 - self.winfo_width()//2
        yy = y + self.win.winfo_height()//2 - self.winfo_height()//2

        self.geometry(f'+{xx}+{yy}')

        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def close_win(self):
        self.destroy()
        focus_last()


class MacMenu(tkinter.Menu):
    def __init__(self):
        menubar = tkinter.Menu(cfg.ROOT)
        tkinter.Menu.__init__(self, menubar)

        if sys.version_info.minor < 10:
            cfg.ROOT.createcommand('tkAboutDialog', self.about_dialog)

        cfg.ROOT.configure(menu=menubar)

    def about_dialog(self):
        try:
            cfg.ROOT.tk.call('tk::mac::standardAboutPanel')
        except Exception:
            print("no dialog panel")


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

        self.all_btns = []
        f = ("San Francisco Pro", 15, "bold")

        titles = CFrame(parrent)
        titles["bg"] = cfg.BUTTON
        titles.pack()

        month_frame = CFrame(titles)
        month_frame["bg"] = cfg.BUTTON
        month_frame.pack(side="left", padx=(0, 15))

        prev = CButton(month_frame, text="<")
        prev.configure(width=2, font=f)
        prev.pack(side="left")
        prev.cmd(lambda e: self.switch_month(prev["text"], e))
        self.all_btns.append(prev)

        self.m_title = CLabel(
            month_frame,
            text=months[self.my_date.month],
            name=str(self.my_date.month)
            )
        self.m_title.configure(bg=cfg.BUTTON, width=6, font=f)
        self.m_title.pack(side="left")
        self.all_btns.append(self.m_title)

        next = CButton(month_frame, text=">")
        next.configure(width=2, font=f)
        next.pack(side="left")
        next.cmd(lambda e: self.switch_month(next["text"], e))
        self.all_btns.append(next)

        year_frame = CFrame(titles)
        year_frame["bg"] = cfg.BUTTON
        year_frame.pack(side="left")

        prev = CButton(year_frame, text="<")
        prev.configure(width=2, font=f)
        prev.pack(side="left")
        prev.cmd(lambda e: self.switch_year(prev["text"], e))
        self.all_btns.append(prev)

        self.y_title = CLabel(
            year_frame,
            text=self.my_date.year,
            name=str(self.my_date.month)
            )
        self.y_title.configure(bg=cfg.BUTTON, width=3, font=f)
        self.y_title.pack(side="left")
        self.all_btns.append(self.y_title)

        next = CButton(year_frame, text=">")
        next.configure(width=2, font=f)
        next.pack(side="left")
        next.cmd(lambda e: self.switch_year(next["text"], e))
        self.all_btns.append(next)

        row = CFrame(parrent)
        row.pack()

        for i in ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"):
            lbl = CButton(row, text = i)
            lbl.configure(width=4, height=2)
            lbl.pack(side="left")
            self.all_btns.append(lbl)

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
            self.all_btns.append(lbl)

        self.fill_days()

        return parrent

    def disable_calendar(self):
        for i in self.all_btns:
            i["fg"] = cfg.HOVERED

    def enable_calendar(self):
       for i in self.all_btns:
            i["fg"] = cfg.FONT

    def create_days(self):
        first_weekday = datetime.weekday(
            datetime(self.my_date.year, self.my_date.month, 1)
            )
        month_len = calendar.monthrange(
            self.my_date.year, self.my_date.month)[1] + 1

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

        try:
            self.my_date = datetime(self.my_date.year, m, self.my_date.day)
        except ValueError:
            day = calendar.monthrange(self.my_date.year, m)[1]
            self.my_date = datetime(self.my_date.year, m, day)
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

        try:
            self.my_date = datetime(y, self.my_date.month, self.my_date.day)
        except ValueError:
            day = calendar.monthrange(y, self.my_date.month)[1]
            self.my_date = datetime(y, self.my_date.month, day)

        self.y_title["text"] = y
        self.fill_days()
