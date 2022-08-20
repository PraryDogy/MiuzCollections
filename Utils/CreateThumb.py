import cv2


class Create:
    def __init__(self, imgPath):
        '''
        create list called "resized" with 4 square thumbnails: 
        150, 200, 250, 300
        '''
        img =cv2.imread(imgPath)
        width, height = img.shape[1], img.shape[0]
        
        if height >= width:
            diff = int((height-width)/2)
            new_img = img[diff:height-diff, 0:width]

        else:
            diff = int((width-height)/2)
            new_img = img[0:height, diff:width-diff]       

        self.resized = list()
        
        for size in [(150, 150), (200, 200), (250, 250), (300, 300)]:
            newsize = cv2.resize(
                new_img, size, interpolation = cv2.INTER_AREA)
            encoded = cv2.imencode('.jpg', newsize)[1].tobytes()
            self.resized.append(encoded)    
        