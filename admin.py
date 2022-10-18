import database


def print_alive(name_func='', what_print=''):
    """Prints output:
    function name, sometext.
    Needs for debug

    Args:
        name_func (str): class.__name__,
        what_print (str): text.
    """

    # print(name_func, what_print)
    return


def clear_db():
    """
    Just clears database, create new one and fills created tables.
    """

    database.Utils().create()
    database.Utils().fill_config()
