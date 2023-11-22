a = [i for i in range(1, 5)]



b = [x
     for i in range(5)
     for x in a
     ]


print(b)