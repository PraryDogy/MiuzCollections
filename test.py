from utils.scaner_new import Scaner, ScanImages, ScanDirs, ScanerGlobs, UpdateDb
import sqlalchemy
from database import Dbase, DirsMd, ThumbsMd
from cfg import cnf
import os


ScanerGlobs.scaner_flag = True

a = UpdateDb()

print("new dirs", a.new_dirs.keys())
print("upd dirs", a.upd_dirs.keys())
print("del dirs", a.del_dirs.keys())


print("new", a.new_images.keys())
print("upd", a.upd_images.keys())
print("del", a.del_images.keys())

