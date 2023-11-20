from typing import Literal
import cv2
from gui.utils import *
from cfg import cnf
import os


def get_coll_name(src: Literal["file path"]) -> Literal["collection name"]:
    coll = src.replace(cnf.coll_folder, "").strip(os.sep).split(os.sep)

    if len(coll) > 1:
        return coll[0]
    else:
        return cnf.coll_folder.strip(os.sep).split(os.sep)[-1]


a = "/Users/Loshkarev/Downloads/This_Is_A_Tiffany_Ring_2021_Digital_Catalog_INTL.pdf"
print(get_coll_name(a))