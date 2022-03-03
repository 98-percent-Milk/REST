import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute("""
        CREATE TABLE stats
        (id INTEGER PRIMARY KEY ASC,
        num_employees INTEGER NOT NULL,
        popular_field VARCHAR(50) NOT NULL,
        unpopular_field VARCHAR(50) NOT NULL,
        desp_employer VARCHAR(100) NOT NULL,
        least_desp_employer VARCHAR(50) NOT NULL,
        last_updated VARCHAR(100) NOT NULL)
        """)

conn.commit()
conn.close()
