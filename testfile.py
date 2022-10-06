import sqlalchemy


engine = sqlalchemy.create_engine('sqlite:///Users/Loshkarev/Library/Application Support/Miuz Gallery/database2.6.1.db')
conn = engine.connect()


q = ""