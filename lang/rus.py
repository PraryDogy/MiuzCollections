from .load_lang import LoadLang

class Rus:
    def __init__(self):
        for key, value in LoadLang.load_lang.items():
            setattr(self, key, value[0])
