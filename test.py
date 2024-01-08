from database import ThumbsMd, Dbase
import sqlalchemy




q = sqlalchemy.select(ThumbsMd.collection).distinct()
res = Dbase.conn.execute(q).fetchall()
res = (i[0] for i in res)

print(res)