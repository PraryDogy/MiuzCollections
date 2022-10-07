medved = WhiteBear()
small_children = [i for i in medved.children if i.age < 16]
if len(small_children) >= 3:
    medved.give_beer(3)
    medved.patriot = True