from difflib import SequenceMatcher
import cfg

name = "image123_crop.jpeg"
filenames = ["image123.jpeg", "image123 preview.jpeg", "image123_image12388", "image123 crop"]

for i in cfg.config["STOPWORDS"]:
    name = name.replace(i, "")

for i in filenames:
    a = SequenceMatcher(None, name, i).ratio()
    if a > 0.5:
        print(i, a)