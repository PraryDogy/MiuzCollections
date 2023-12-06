from .load_lang import load_lang

class Rus:
    def __init__(self):
        for key, value in load_lang.items():
            setattr(self, key, value[0])
