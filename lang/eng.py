from ._main import LoadLang

class Eng:
    def __init__(self):
        for key, value in LoadLang.load_lang.items():
            setattr(self, key, value[1])
