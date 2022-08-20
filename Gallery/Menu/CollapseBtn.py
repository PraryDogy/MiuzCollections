import sqlalchemy
from DataBase.Database import Config, dBase
from Utils.Manage import Geometry

def CollapseMenu(currBtn, firstClmn, between, secClmn):
    getMenuClmn = sqlalchemy.select(Config.value).where(
        Config.name=='menuClmn')
    dbMenuClmn = int(dBase.conn.execute(getMenuClmn).first()[0])
    newClmn = 1 if dbMenuClmn==2 else 2
    
    updateRow = sqlalchemy.update(Config).values(value=str(newClmn)).where(
        Config.name=='menuClmn')
    dBase.conn.execute(updateRow)
    
    if newClmn==1:
        currBtn.config(text='▶')
        
        firstClmn.pack(side='top')
        between.config(width=0)
        between.pack(side='top')
        secClmn.pack(side='top')
        
    else:
        currBtn.config(text='◀')
        
        firstClmn.pack(side='left')
        between.config(width=10)
        between.pack(side='left')
        secClmn.pack(side='left')

    Geometry()
