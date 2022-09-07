import sqlalchemy
import cfg

engige = sqlalchemy.create_engine(f'sqlite:////{cfg.DB_DIR}/{cfg.DB_NAME}')
conn = engige.connect()


res = conn.execute('INSERT INTO config("name", "value") VALUES("last", "true")')