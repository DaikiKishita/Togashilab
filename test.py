import sqlite3 as sq
dbname="static/Users.db"

def exesql(sql,tex):
    with sq.connect(dbname) as conn:
        cur = conn.cursor()
        if tex=="":
            result = cur.execute(sql)
            conn.commit()
            if result is None:
                return []
            return list(result)
        else:
            cur.execute(sql,tex)
            conn.commit()

names=exesql("select name,timer from Users","")
print(names)