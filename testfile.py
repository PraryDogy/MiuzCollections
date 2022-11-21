import cfg
import os
import datetime

years = [str(y) for y in range(2018, datetime.datetime.now().year + 1)]
y_dirs = [os.path.join('/Users/Loshkarev/Desktop/test', y) for y in years]
y_dirs = [i for i in y_dirs if os.path.exists(i)]

print(y_dirs)