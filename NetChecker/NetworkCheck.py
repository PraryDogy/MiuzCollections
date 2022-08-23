import urllib.request
from DataBase.Database import AdminUtils

def Check():
    """Check internet connection. 
    Create empty database with empty tables if no connection.
    Returns bool."""
    try:
        urllib.request.urlopen('http://google.com')
    except:
        adm = AdminUtils()
        adm.Create()
        adm.FillConfig()