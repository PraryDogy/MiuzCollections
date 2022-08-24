import subprocess
import tkinter
import cfg
from Gallery.ImgGrid.Gui import Create as ImgGridGui
import cv2

def CreateThumb(imgPath):
    """Returns list with 4 square thumbnails: 150, 200, 250, 300"""
    
    img = cv2.imread(imgPath)
    width, height = img.shape[1], img.shape[0]
    
    if height >= width:
        diff = int((height-width)/2)
        new_img = img[diff:height-diff, 0:width]

    else:
        diff = int((width-height)/2)
        new_img = img[0:height, diff:width-diff]       

    resized = list()
    
    for size in [(150, 150), (200, 200), (250, 250), (300, 300)]:
        newsize = cv2.resize(
            new_img, size, interpolation = cv2.INTER_AREA)
        encoded = cv2.imencode('.jpg', newsize)[1].tobytes()
        resized.append(encoded)    
        
    return resized


def MyCopy(output):
    """Custom copy to clipboard with subprocess"""
    
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))


def MyPaste():
    """Custom paste from clipboard with subprocess"""
    
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


def ReloadGallery():
    """Destroy cfg.IMG_GRID frame with thumbmails,
    create new tkinter frame and put in it new thumbnails"""
    
    cfg.IMG_GRID.destroy()
    imgFrame = tkinter.Frame(cfg.UPFRAME, bg=cfg.BGCOLOR)
    imgFrame.pack(side='left', fill='both', expand=True)
    cfg.IMG_GRID = imgFrame
    
    ImgGridGui()
