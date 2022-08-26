import traceback

import cv2
import numpy
import sqlalchemy
from DataBase.Database import Config, Thumbs, dBase
from PIL import Image, ImageTk


def LoadThumbs(currColl):
    """return list turples: (img, src)"""
    
    query = sqlalchemy.select(Config.value).where(Config.name=='size')
    size = int(dBase.conn.execute(query).first()[0])

    for i in [Thumbs.img150, Thumbs.img200, Thumbs.img250, Thumbs.img300]:
        if str(size) in str(i):
            img = i
        
    query = sqlalchemy.select(img, Thumbs.src).where(
        Thumbs.collection==currColl).order_by(
            -Thumbs.modified)
    res = dBase.conn.execute(query).fetchall()

    thumbs = list()

    for blob, src in res:
        try:
            nparr = numpy.frombuffer(blob, numpy.byte)
            image1 = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
                        
            # convert cv2 color to rgb
            imageRGB = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
            
            # load numpy array image
            image = Image.fromarray(imageRGB)
            photo = ImageTk.PhotoImage(image)

            thumbs.append((photo, src))

        except Exception:
            print(traceback.format_exc())

    return thumbs
