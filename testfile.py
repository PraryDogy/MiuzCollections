import re
import tkinter
import traceback
from datetime import datetime
from tkinter.ttk import Separator
from turtle import width

import cfg
import cv2
import numpy
import sqlalchemy
import tkmacosx
from database import Config, Dbase, Thumbs
from PIL import Image, ImageTk

class Globals:
    """
    Variables for current module
    """

    __getCurrColl = sqlalchemy.select(Config.value).where(
        Config.name=='currColl')
    currColl = Dbase.conn.execute(__getCurrColl).first()[0]

    # bind reset function for thumbnails frame: Images().Reset()
    images_reset = object


size = Dbase.conn.execute(
    sqlalchemy.select(Config.value).where(
        Config.name=='size')).first()[0]
size = int(size)
img = Thumbs.__dict__[f'img{size}']

res = Dbase.conn.execute(
    sqlalchemy.select(img, Thumbs.src, Thumbs.modified).where(
    Thumbs.collection==Globals.currColl).order_by(
    -Thumbs.modified)).fetchall()

thumbs = []
for blob, src, mod in res:

    try:
        nparr = numpy.frombuffer(blob, numpy.byte)
        image1 = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)

        # convert cv2 color to rgb
        imageRGB = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)

        # load numpy array image
        image = Image.fromarray(imageRGB)
        photo = ImageTk.PhotoImage(image)
        year = datetime.fromtimestamp(mod).year
        thumbs.append((photo, src, year))

    except Exception:
        print(traceback.format_exc())

for i in thumbs:
    print(i)