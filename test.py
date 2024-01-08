from database import Dbase, ThumbsMd
import sqlalchemy



class Dublicater:
    def __init__(self):
        q = sqlalchemy.select(ThumbsMd)
        res = Dbase.conn.execute(q).fetchall()


        for (id, img, src, size, created, modified, collection) in res:
            q = (sqlalchemy.insert(ThumbsMd)
                .values({"img150": img,
                        "src": src,
                        "size": size,
                        "created": created,
                        "modified": modified,
                        "collection": collection}))
            
            Dbase.conn.execute(q)



class DublicateRemover:
    def __init__(self):
        q = sqlalchemy.select(ThumbsMd.id, ThumbsMd.src)
        res = Dbase.conn.execute(q).fetchall()
        res = {i[0]: i[1] for i in res}

        dublicates = {}
        for k, v in res.items():
            if not dublicates.get(v):
                dublicates[v] = [k]
            else:
                dublicates[v].append(k)

        dublicates = [row_id
                      for _, id_list in dublicates.items()
                      for row_id in id_list[1:]
                      if len(v) > 1]
        
        print(dublicates)

        if not dublicates:
            return

        values = [{"b_id": i} for i in dublicates]
        q = (sqlalchemy.delete(ThumbsMd)
             .filter(ThumbsMd.id==sqlalchemy.bindparam("b_id")))
        # Dbase.conn.execute(q, values)
