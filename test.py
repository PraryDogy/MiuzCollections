from datetime import datetime


entry_text = "10.1.1991"
datetime_object = datetime.strptime(entry_text, '%d.%m.%Y')


print(datetime_object)