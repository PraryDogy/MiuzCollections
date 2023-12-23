from PIL import Image


class FitImg:
    def fit(self, img: Image, w: int, h: int):
        imw, imh = img.size

        if -3 < imw - imh < 3:
            imw, imh = imw, imw

        if imw > imh:
            side = max(w, h)
            delta = side/imw
            neww, newh = side, int(imh*delta)
        elif imh > imw:
            side = min(w, h)
            delta = side/imh
            neww, newh = int(imw*delta), side
        else:
            side = min(w, h)
            neww, newh = side, side

        return img.resize((neww, newh))