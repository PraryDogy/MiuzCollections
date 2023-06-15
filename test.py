from cfg import conf
import subprocess
import cv2


def smb_ip():
    df = subprocess.Popen(['df', conf.coll_folder], stdout=subprocess.PIPE)


def img_place(src):
    try:
        img_read = cv2.imread(src)
    except FileNotFoundError:
        pass


img_place(conf.coll_folder)