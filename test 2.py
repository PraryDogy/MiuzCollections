import sqlalchemy
import cfg

engige = sqlalchemy.create_engine(f'sqlite:////{cfg.DB_DIR}/{cfg.DB_NAME}')
conn = engige.connect()


res = conn.execute('INSERT INTO config("name", "value") VALUES("last", "true")')



class Glob:
    a = 100

    def ppp(self):
        print('bbb')



Glob().ppp()


print(Glob.a)