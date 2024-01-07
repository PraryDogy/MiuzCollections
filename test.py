import os


cll = "/Volumes/Untitled/_Collections 3"

colls = (os.path.join(cll, i)
         for i in os.listdir(cll)
         if os.path.isdir(os.path.join(cll, i))
         )


for i in colls:
    print(i)