import sqlite3

conn = sqlite3.connect ('site.db')
c = conn.cursor()

rs  = c.execute(
    '''
SELECT * FROM recipe
    '''

)

res = rs.fetchall()
print(res)

conn.commit()
conn.close()