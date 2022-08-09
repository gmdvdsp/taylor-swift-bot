import sqlite3

COMMA = ', '

conn = sqlite3.connect('database.db')
c = conn.cursor()

def create_table(name, columns):
    COMMA.join(columns)
    c.execute("""CREATE TABLE IF NOT EXISTS {} 
                ({}
                )""".format(name, COMMA.join(columns)))
    conn.commit()
            
def create_entry(table, columns):
    params = ('?' * len(columns))
    c.execute("""INSERT OR IGNORE INTO {} 
                VALUES ({})""".format(table, COMMA.join(params)), columns)
    conn.commit()

def update_entry(table, column, key, key_value, value):
    c.execute("""UPDATE OR IGNORE {}
                SET {} = ? 
                WHERE {} = ?""".format(table, column, key), (value, key_value))
    conn.commit()

def get_entry(table, column, row, row_value):
    ret = c.execute("""SELECT {}
                FROM {}
                WHERE {} = ?""".format(column, table, row), (row_value,))
    ret = ret.fetchone()
    return ret[0]

def get_random_entry(table, column):
    ret = c.execute("""SELECT {}
                    FROM {}
                    ORDER BY RANDOM()""".format(column, table))
    ret = ret.fetchone()
    return ret[0]

def get_all(table):
    ret = c.execute("""SELECT *
                    FROM {}""".format(table))
    ret = ret.fetchall()
    return ret

def delete_entry(table, row, row_value):
    c.execute("""DELETE FROM {}
                WHERE {} = ?""".format(table, row), (row_value,))
    conn.commit()

# Only for debugging, comment out when unneeded:
def delete_all(table):
    c.execute("""DELETE FROM {}""".format(table))
    conn.commit()
