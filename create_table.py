import sqlite3 as sq

dbname="static/Users.db"
conn=sq.connect(dbname)
cur=conn.cursor()

cur.execute('CREATE TABLE Users(id INTEGER PRIMARY KEY AUTOINCREMENT,name STRING unique,color STRING,timer time)')

conn.commit()
cur.close()
conn.close()