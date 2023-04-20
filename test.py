# from database import Dbase, Thumbs
# import sqlalchemy
# from datetime import datetime

# images = Dbase.conn.execute(
#     sqlalchemy.select(
#     Thumbs.src, Thumbs.created, Thumbs.modified, Thumbs.size
#     )
#     ).fetchall()

# images_ = {}

# for src, created, modified, size in images:
#     print(datetime.fromtimestamp(created).year)
#     images_.setdefault(
#         datetime.fromtimestamp(created).year, []
#         ).append(created)


# print(images_)