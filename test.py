from datetime import datetime
import re

date1 = "10.01"
date2 = "10.01"

r1 = r"\d{,2}"
r2 = r"\d{,2}\.\d{,2}"
if any(
    (re.fullmatch(r1, date1), re.fullmatch(r2, date1))
    ):
    print(date1 + ".")