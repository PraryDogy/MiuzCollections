coll_folder = "/Volumes/Untitled/Тай 2019"
import os


def get_coll_name(src: str):
    coll = src.replace(coll_folder, "")
    coll = coll.strip(os.sep)
    splited = coll.split(os.sep)

    if len(splited) > 1:
        return coll.split(os.sep)[0]
    else:
        return coll_folder.strip(os.sep).split(os.sep)[-1]



for root, dirs, files in os.walk(coll_folder):
    for file in files:
        a = get_coll_name(os.path.join(root, file))
        print(a)