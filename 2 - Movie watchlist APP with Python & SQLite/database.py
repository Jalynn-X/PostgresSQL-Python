import sqlite3
import datetime
# three columns in the table
# title, release_date, watched

# create query
create_movie_table = """CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    title TEXT,
    release_timestamp REAL
);"""

create_users_table = """CREATE TABLE IF NOT EXISTS users (
    user_name TEXT PRIMARY KEY    
);"""

create_watched_table = """CREATE TABLE IF NOT EXISTS watched (
    watcher_name TEXT,
    movie_id INTEGER,
    FOREIGN KEY(watcher_name) REFERENCES users(username),
    FOREIGN KEY(movie_id) REFERENCES movies(id)
);"""

create_index = """CREATE INDEX IF NOT EXISTS idx_movie_release 
ON movies(release_timestamp);
"""

# movies
# insert query
insert_movies = "INSERT INTO movies (title, release_timestamp) VALUES (?, ?)"
# select query
select_all_movies = "SELECT * FROM movies;"
select_upcoming_movies = "SELECT * FROM movies WHERE release_timestamp > ?;"
select_watched_movies = """SELECT movies.* FROM movies 
JOIN watched ON watched.movie_id = movies.id
JOIN users ON watched.watcher_name = users.user_name
where users.user_name = ?;"""
select_searched_movies = """SELECT * FROM movies WHERE title like ?;"""

# users
insert_users = "INSERT INTO users (user_name) VALUES (?);"

# watched
insert_watched_movies = "INSERT INTO watched (watcher_name, movie_id) VALUES (?, ?);"


connection = sqlite3.connect("data.db")

def create_tables():
    with connection:
        connection.execute(create_movie_table)
        connection.execute(create_users_table)
        connection.execute(create_watched_table)
        connection.execute(create_index)

def add_movie(title, release_timestamp):
    with connection:
        connection.execute(insert_movies, (title, release_timestamp))

def add_user(user_name):
    with connection:
        connection.execute(insert_users, (user_name,))

def get_movies(upcoming=False):
    with connection:
        cursor = connection.cursor()
        if upcoming == False:
            cursor.execute(select_all_movies)
        else:
            today_timestamp = datetime.datetime.today().timestamp()
            cursor.execute(select_upcoming_movies, (today_timestamp,))
            # (timestamp) -- This is just the value itself, not a tuple
            # (timestamp,) -- A comma is required to create a single-element tuple
        return cursor.fetchall()
# OR:
# with connection:
#   cursor = connection.execute(select_all_movies)
#   return cursor

def search_movie(keyword):
    with connection:
        cursor = connection.execute(select_searched_movies, (f"%{keyword}%",))
        return cursor
        

def watch_movie(user_name, movie_id):
    with connection:
        connection.execute(insert_watched_movies, (user_name, movie_id))

def get_watched_movies(user_name):
    with connection:
        cursor = connection.execute(select_watched_movies, (user_name,))
        return cursor