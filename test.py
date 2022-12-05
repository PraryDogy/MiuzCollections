
# img_w, img_h = 3000, 2758
img_w, img_h = 150, 110
widget_w, widget_h = 1152, 929

maxwidth, maxheight = 1152, 929


if maxwidth > img_w or maxheight > img_h:
    print('smalla img')
    f1 = maxwidth / img_w
    f2 = maxheight / img_h
else:
    print('big img')
    f1 = maxwidth / img_w
    f2 = maxheight / img_h

f = min(f1, f2)  # resizing factor
dim = (int(img_w * f), int(img_h * f))


print(dim)