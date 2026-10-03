import sqlite3

connection = sqlite3.connect('danniye.db', check_same_thread=False)
cursor = connection.cursor()



cursor.execute('''
    CREATE TABLE portfolios (
        id INTEGER,
        uuid TEXT,
        name TEXT,
        bio TEXT,
        github TEXT,
        telegram TEXT,
        avatar TEXT,
        skills TEXT
       ) ''')

connection.commit()
connection.close()