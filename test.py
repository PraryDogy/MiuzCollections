# from utils.scaner import Scaner, ScanImages, ScanDirs, ScanerGlobs, UpdateDb
# import sqlalchemy
# from database import Dbase, DirsMd, ThumbsMd
# from cfg import cnf
# import os

from customtkinter import CTkProgressBar
import tkinter
import time
import threading

root = tkinter.Tk()
root.geometry("300x100")


var = tkinter.Variable(value=0)
progress = CTkProgressBar(master=root, width=170, variable=var)
progress.pack(expand=1)
progress.set(0)

def test():
    global var
    for i in range(10):
        new_value = var.get() + 0.1
        var.set(value=new_value)
        time.sleep(0.3)


def tsk():
    a = threading.Thread(target=test)
    a.start()


root.after(1000, tsk)
root.mainloop()