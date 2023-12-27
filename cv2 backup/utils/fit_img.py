from typing import Literal

import cv2


class FitImg:
    def fit_img(self, img: Literal["cv2 image"], w: int, h: int) -> Literal["cv2 image"]:
        imh, imw = img.shape[:2]

        if -3 < imw - imh < 3:
            imw, imh = imw, imw

        if w > h:
            if imw > imh:
                delta = imw/imh
                # neww, newh = int(h*delta), h
                neww, newh = w, int(w/delta)
            else: # img h > img w
                delta = imh/imw
                neww, newh = int(h/delta), h
        else:
            if imw > imh:
                delta = imw/imh
                neww, newh = w, int(w/delta)
            else: # h > w and h > w
                delta = imh/imw
                neww, newh = int(h/delta), h

        return cv2.resize(img, (neww, newh), interpolation=cv2.INTER_AREA)