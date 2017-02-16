import sqlite3
from shutil import copyfile

#Make a copy first
copyfile('wardpresc-data.db', 'wardpresc-data.db.old')

#Then alter the database
conn = sqlite3.connect('wardpresc-data.db')

conn.execute("ALTER TABLE patient ADD COLUMN active BOOLEAN;")

conn.commit()

conn.close()
