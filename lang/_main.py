import json
import os

class LoadLang:
    with open(file="lang.json", mode="r", encoding="utf-8") as file:
        load_lang: dict = json.loads(s=file.read())


class Admin:
    def __init__(self):
        print("1 add new key")
        print("2 edit existing key")
        print("3 remove existing key")

        try:
            inp = int(input())
        except ValueError:
            inp = 4

        if inp in (1, 2):
            print("write key name")
            name = input()
            print("write rus value")
            ru = input()
            print("write en value")
            en = input()
            LoadLang.load_lang[name] = [ru, en]
            print("done")

        elif inp == 3:
            print("write key name")
            name = input()
            try:
                LoadLang.load_lang.pop(name)
            except KeyError:
                print("no key")
                return
            print("done")

        elif not inp:
            print("end")
            return

        else:
            print("white 1, 2 or 3")
            return

        with open(file="lang.json", mode="w", encoding="utf-8") as file:
            json.dump(obj=LoadLang.load_lang, fp=file, ensure_ascii=False, indent=4)


class TrashKeys:
    def __init__(self):
        exclude = ["_MACOSX", "cv2 backup", "env", "_pycache_"]
        parrent = os.path.dirname(os.path.dirname(__file__))
        pyfiles = []

        for root, dirs, files in os.walk(top=parrent, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file in files:
                if file.endswith(".py"):
                    pyfiles.append(os.path.join(root, file))

        ex = "lng"
        with open(file="lang.json", mode="r", encoding="utf-8") as file:
            data = json.loads(s=file.read())


        trash_keys_count = {i: 0 for i in data}

        for py in pyfiles:
            with open(file=py, mode="r") as py_f:
                py_text = py_f.read()

                for lng_key in data:

                    if f"{ex}.{lng_key}" in py_text:
                        trash_keys_count[lng_key] = +1

        trash_keys_count = [k for k, v in trash_keys_count.items() if v == 0]
        trash_keys_count.remove("name")

        print("unused lang keys: ", trash_keys_count)

if __name__ == '__main__': 
    TrashKeys()
    Admin()
