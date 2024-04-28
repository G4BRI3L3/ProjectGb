import sqlite3

conn = sqlite3.connect ('site.db')
c = conn.cursor()

c.execute(
    '''
DELETE FROM recipe WHERE image_path = "uploads\es1.png"

    '''

)

conn.commit()
conn.close()