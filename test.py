import requests
from bs4 import BeautifulSoup

lnk = "https://miuz.ru/catalog/rings/R37-4-T130613733/"
r = requests.get(lnk)
htmlContent = r.content
soup = BeautifulSoup(htmlContent,'html.parser')

# elements = soup.find_all("div", class_="js-block-ruler js-coord")[0]

elements = soup.find_all("data-zoom-image")

print(elements)