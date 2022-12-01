import sqlalchemy
import sqlalchemy.ext.declarative

class Dbase:
    """
    Checks database exists with DbChecker.

    *var conn: database connection
    *var base: declatative_base for models and actions
    """
    __engine = sqlalchemy.create_engine(
        'sqlite:////' + '/Users/Loshkarev/Desktop/test.db',
        connect_args={'check_same_thread':False,},
        echo= False
        )
    conn = __engine.connect()
    base = sqlalchemy.ext.declarative.declarative_base()


class person(Dbase.base):
    """
    Sqlalchemy model.

    *columns: img150, src, size, created, modified,
    collection
    """

    __tablename__ = 'thumbs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    first = sqlalchemy.Column(sqlalchemy.Integer)
    second = sqlalchemy.Column(sqlalchemy.Integer)


for i in range(0, 2):
    q = sqlalchemy.insert(person).values({'first': 4, 'second': 555})

