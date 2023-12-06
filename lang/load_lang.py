import json


class LoadLang:
    with open(file="lang.json", mode="r", encoding="utf-8") as file:
        load_lang = json.loads(s=file.read())

    def admin():
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
            __class__.load_lang[name] = [ru, en]
            print("done")

        elif inp == 3:
            print("write key name")
            name = input()
            try:
                __class__.load_lang.pop(name)
            except KeyError:
                print("no key")
                return
            print("done")

        else:
            print("white 1, 2 or 3")

        with open(file="lang.json", mode="w", encoding="utf-8") as file:
            json.dump(obj=__class__.load_lang, fp=file, ensure_ascii=False, indent=4)


if __name__ == '__main__': 
    LoadLang.admin()