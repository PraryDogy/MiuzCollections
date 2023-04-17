a = [[[1], [2], [3]], ["a", "b", "c"]]


b = [
    y
    for lists in a
    for x in lists
    for y in x
    ]

cc = {x for x in b}

print(type(cc))