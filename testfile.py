import os
import tkinter
import cfg


p1 = os.listdir('/Volumes/Shares/Marketing/External/Фото_и_видео_Магазинов/Фото_магазинов')
p2 = os.listdir('/Volumes/Shares/Marketing/External/Фото_и_видео_Магазинов/Фото_магазинов/Retouch')


final = list()
for i in p1:
    final.append(i) if i not in p2 else False
    
    
for i in final:
    print(i)