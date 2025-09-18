import sqlite3

connection = sqlite3.connect("data.db")
connection.row_factory = sqlite3.Row

def create_table():
    with connection:
        connection.execute("CREATE TABLE IF NOT EXISTS entries (content TEXT, date TEXT);")

def add_entry(entry_content, entry_date):
    with connection:
        connection.execute("INSERT INTO entries VALUES(?, ?);", (entry_content, entry_date))

# we want to avoid:
# connection.execute(f"INSERT INTO entries VALUES ('{entry_content}', '{entry_date}');")


def get_entry():
    """get entries list"""
    cursor = connection.execute("SELECT * FROM entries;")
    return cursor
# another option:
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM entries;")
# to get row: use cursor.fetchone(), or use cursor.fetchall()
# we don't need with connection in get_entry
# because there are no changes that need to be committed or rolled back