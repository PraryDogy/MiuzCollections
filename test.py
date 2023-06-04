from datetime import datetime
from calendar import monthrange

d = datetime(2022, 2, 22)
day = monthrange(2022, 2)[1]


print(day)