import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS create_recipe 
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     user_id VARCHAR(250) NOT NULL,
     recipe_id VARCHAR(250) NOT NULL,
     title VARCHAR(250) NOT NULL,
     ingredients TEXT NOT NULL,
     instructions TEXT NOT NULL,
     views INTEGER NOT NULL,
     timestamp VARCHAR(100) NOT NULL,
     date_created VARCHAR(100) NOT NULL)
    ''')

c.execute('''
    CREATE TABLE IF NOT EXISTS rate_recipe 
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     user_id VARCHAR(250) NOT NULL,
     recipe_id VARCHAR(250) NOT NULL,
     rating REAL NOT NULL,
     timestamp VARCHAR(100) NOT NULL,
     date_created VARCHAR(100) NOT NULL)
    ''')

conn.commit()
conn.close()
