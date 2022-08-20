import urllib.request

from .Gui import Create as Gui


def Check():
    '''
    \ncheck internet connection
    \nreturn bool
    \nif False
    \nrun Gui with error message.
    '''
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        Gui()
        return False
