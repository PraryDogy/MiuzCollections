# import requests
# from bs4 import BeautifulSoup

# lnk = "https://miuz.ru/catalog/rings/R37-4-T130613733/"
# r = requests.get(lnk)
# htmlContent = r.content
# soup = BeautifulSoup(htmlContent,'html.parser')

# elements = soup.find_all("div", class_="js-block-ruler js-coord")[0]
# elements = soup.find_all("data-zoom-image")



import os

filename = "E2028-KID-0069-Y"
disk = "/Volumes/Shares/Marketing/Photo"
retouch = "/Volumes/Shares/Marketing/Photo/Retouch"
win = "Z:\Marketing\Photo\Retouch"

# photo = "/Volumes/Shares/Marketing/Photo"
# photo2 = "/Volumes/Shares/Marketing/General/14.  ФОТО"
# design = "/Volumes/Shares/Marketing/Design"



for root, dir, files in os.walk(retouch):
    for file in files:
        if filename in file:
            print(os.path.join(root, file))