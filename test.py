import tkinter as tk

root= tk.Tk()

cal_f = tk.Frame(root)
cal_f.pack()

month = tk.Label(root, text="Month", bg="yellow")
year = tk.Label(root, text="Year", bg="yellow")

for x, i in enumerate(("<", "Month", ">", "<", "Year", ">")):
    arrow = tk.Label(root, text=i)
    arrow.pack(side="left")

r = 0
c = 0
for i in range(("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")):
    weekkd = tk.Label(cal_f, text=str(i))
    weekkd.grid(row=r, column=c)
    c += 1

r+= 1
c = 0
for i in range(1, 6*7+1):
    day = tk.Label(cal_f, text=str(i))
    day.grid(row=r, column=c)
    c += 1
    if c % 7 == 0:
        c = 0
        r += 1



root.mainloop()