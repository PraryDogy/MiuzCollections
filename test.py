from utils.scaner import Scaner, ScanImages, ScanDirs, ScanerGlobs, UpdateDb
import sqlalchemy
from database import Dbase, DirsMd, ThumbsMd
from cfg import cnf
import os


# ScanerGlobs.scaner_flag = True
# a = ScanImages()

# print("new dirs", a.new_dirs.keys())
# print("upd dirs", a.upd_dirs.keys())
# print("del dirs", a.del_dirs.keys())


# print("new img", a.new_images.keys())
# print("upd img", a.upd_images.keys())
# print("del img", a.del_images.keys())

# print(a.db_images)
# print(a.finder_images)