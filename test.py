times = {1: 5, 2: 10, 3: 30, 4: 60}

t = 60


key = [k for k, v in times.items() if v == t][0]
key = times[key+1]

print(key)