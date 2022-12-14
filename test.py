def init_global_variable():
    """initialize variable"""
    global GLOBALS_DICT
    GLOBALS_DICT = {}

def set_variable(name, value):
    """set variable"""
    try:
        GLOBALS_DICT[name] = value
        return True
    except KeyError:
        return False

def get_variable(name):
    """get variable"""
    try:
        return GLOBALS_DICT[name]
    except KeyError:
        return "Not Found"


class Test:
    def __init__(self) -> None:
        global all_src
        all_src = 1
