import datetime
import os
from select import select
import sys

import sqlalchemy

import cfg
from admin import printAlive
from DataBase.Database import Thumbs, dBase
from Utils.Utils import CreateThumb

names = (
    Thumbs.src, Thumbs.size, Thumbs.created, Thumbs.modified, Thumbs.collection)
q = sqlalchemy.select(names)

res = dBase.conn.execute(q).fetchall()


print(res)