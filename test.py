from lib2to3.pgen2.tokenize import TokenError
import re
import tkinter
from unicodedata import digit

import sqlalchemy
import tkmacosx
from PIL import Image, ImageTk

import cfg
from DataBase.Database import Config, Thumbs, dBase
from Utils.Styled import *
from Utils.Utils import *


root = tkinter.Tk()


fr = tkmacosx.SFrame(root, scrollbarwidth=10, autohidescrollbar=True)
fr.pack()

for i in range(0, 15):
    tkinter.Label(fr, text='kkk').pack()


root.mainloop()
