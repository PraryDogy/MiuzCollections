from utils.scandirs import ScanDirs, ScanImages, UpdateDb
import sqlalchemy
from database import Dbase, DirsMd, ThumbsMd


a = UpdateDb()

print(a.new_dirs)