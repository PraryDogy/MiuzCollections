import tkinter
from tkinter import ttk

import sqlalchemy
from PIL import ImageTk, Image

from database import Dbase, ThumbsMd
from utils.system import SysUtils


class Images:
    def __init__(self):
        q = sqlalchemy.select(ThumbsMd.img150).limit(20)
        res = [i[0] for i in Dbase.conn.execute(q).fetchall()]
        self.images = {
            x: SysUtils().crop_image(img=SysUtils().decode_image(img=i))
            for x, i in enumerate(res)}
