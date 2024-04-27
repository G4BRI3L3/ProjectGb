import sqlite3

conn = sqlite3.connect ('site.db')
c = conn.cursor()

c.execute(
    '''
    ALTER TABLE recipe ADD COLUMN image_path TEXT;
    '''

)


conn.commit()
conn.close()