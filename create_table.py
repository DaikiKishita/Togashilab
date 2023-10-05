import sqlite3 as sq

dbname="static/Users.db"
conn=sq.connect(dbname)
cur=conn.cursor()

cur.execute('CREATE TABLE Monthliy(id INTEGER PRIMARY KEY AUTOINCREMENT,name STRING,maxtimer time,Year Integer,month Integer)')

conn.commit()
cur.close()
conn.close()