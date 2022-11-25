defs = {'a': 1, 'b': 2, 'c': 3, 'f': 6}
config = {'a': 666, 'b': 333, 'e':5}

test = {'a': 44, 'b': 333, 'c': 3, 'f': 6}


part1 = {k:v for k, v in config.items() if k in defs.keys()}
part2 = {k:v for k, v in defs.items() if k not in config.keys()}
new_config = {**part1, **part2}


print(new_config)
