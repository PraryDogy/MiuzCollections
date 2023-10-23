name = "/Volumes/Shares/Marketing/Photo/_Collections/24 Estella/1 IMG/17.10.2023_E01-35701.jpg"
import os
e = name.split("/")[-1]
e = os.path.splitext(e)

print(e)