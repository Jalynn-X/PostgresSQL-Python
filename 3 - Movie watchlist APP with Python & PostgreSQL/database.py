import os
import psycopg2
import datetime

from dotenv import load_dotenv
load_dotenv()
# code after this line use .env, before this line dors not use

# three columns in the table
# title, release_date, watched

# create query
create_movie_table = """CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title TEXT,
    release_timestamp REAL
);"""
# we cannot expect the primary key autoincrement, we need to configure it

create_users_table = """CREATE TABLE IF NOT EXISTS users (
    user_name TEXT PRIMARY KEY    
);"""

create_watched_table = """CREATE TABLE IF NOT EXISTS watched (
    watcher_name TEXT,
    movie_id INTEGER,
    FOREIGN KEY(watcher_name) REFERENCES users(user_name),
    FOREIGN KEY(movie_id) REFERENCES movies(id)
);"""

create_index = """CREATE INDEX IF NOT EXISTS idx_movie_release 
ON movies(release_timestamp);
"""

# movies
# insert query
insert_movies = "INSERT INTO movies (title, release_timestamp) VALUES (%s, %s)"
# select query
select_all_movies = "SELECT * FROM movies;"
select_upcoming_movies = "SELECT * FROM movies WHERE release_timestamp > %s;"
select_watched_movies = """SELECT movies.* FROM movies 
JOIN watched ON watched.movie_id = movies.id
JOIN users ON watched.watcher_name = users.user_name
where users.user_name = %s;"""
select_searched_movies = """SELECT * FROM movies WHERE title like %s;"""

# users
insert_users = "INSERT INTO users (user_name) VALUES (%s);"

# watched
insert_watched_movies = "INSERT INTO watched (watcher_name, movie_id) VALUES (%s, %s);"

connection = psycopg2.connect(
    host=os.environ["DB_HOST"],
    database=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    port=os.environ["DB_PORT"]
)


def create_tables():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(create_movie_table)
            cursor.execute(create_users_table)
            cursor.execute(create_watched_table)
            cursor.execute(create_index)
# using with connection.cursor() as cursor will make the resources released when cursor is closed

def add_movie(title, release_timestamp):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(insert_movies, (title, release_timestamp))


def add_user(user_name):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(insert_users, (user_name,))


def get_movies(upcoming=False):
    with connection:
        with connection.cursor() as cursor:
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
        with connection.cursor() as cursor:
            cursor.execute(select_searched_movies, (f"%{keyword}%",))
            return cursor.fetchall()


def watch_movie(user_name, movie_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(insert_watched_movies, (user_name, movie_id))


def get_watched_movies(user_name):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(select_watched_movies, (user_name,))
            return cursor.fetchall()