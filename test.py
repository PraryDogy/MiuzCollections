import os


collections = []

collfolder = "/Volumes/Shares/Marketing/Photo/_Collections"


for i in os.listdir(collfolder):
    collection = os.path.join(collfolder, i)
    if not os.path.isdir(collection):
        continue
    if i.startswith("_"):
        continue
    collections.append(collection)


steps = 0.5 / len(collections)


print(steps)


print(steps*len(collections))