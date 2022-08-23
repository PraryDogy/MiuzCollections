import traceback

import cfg
import cv2
import numpy
import sqlalchemy
from DataBase.Database import Config, Thumbs, dBase
from PIL import Image, ImageTk


def LoadThumbs(currColl):
    '''
    return list turples
    (img, src)
    '''
    query = sqlalchemy.select(Config.value).where(Config.name=='size')
    size = int(dBase.conn.execute(query).first()[0])

    if size==150:
        img = Thumbs.img150
    if size==200:
        img = Thumbs.img200
    if size==250:
        img = Thumbs.img250
    if size==300:
        img = Thumbs.img300  

    getColls = sqlalchemy.select(Thumbs.collection)
    collsNames = dBase.conn.execute(getColls).fetchall()
    collsNames = set(i[0] for i in collsNames)
    try:
        currColl = [i for i in collsNames if currColl in i][0]
    except IndexError:
        print(traceback.format_exc())
        currColl = 'noCollection'

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
