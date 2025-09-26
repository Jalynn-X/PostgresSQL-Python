import datetime
import database

from dotenv import load_dotenv
# getting user data and interacting with database by passing / retrieving data from it
# data interactions are capsulated in the database.py file
# app.py is not gonna care what it is using in the database.py file (e.g. SQLite or PostgreSQL)

menu = """ Please selece one of the following options:
1 - Add a new movie
2 - View upcoming movies
3 - View all movies
4 - Watch a movie
5 - View watched movies
6 - Add user
7 - Search movies
8 - Exit

You selection:"""

welcome = "Welcome to the watchlist app"

print(welcome)
database.create_tables()

def promt_add_movie():
    title = input("movie title: ")
    release_date = input("Release date (dd-mm-YYYY): ")
    parsed_date = datetime.datetime.strptime(release_date, "%d-%m-%Y")
    timestamp = parsed_date.timestamp()
    database.add_movie(title, timestamp)

# write a print movie function so that it can be reused
# no need to write multiple times in the while loop
def print_movie_list(heading, movies):
    print(f"-- {heading} movies --")
    for movie_id, title, release_date in movies:
        movie_date = datetime.datetime.fromtimestamp(release_date)
        date_format = movie_date.strftime("%d/%m/%Y")
        print(f"{movie_id}: {title} (on {date_format})")
    print("--------------\n")

def prompt_watch_movie():
    user_name = input("Enter user name: ")
    movie_id = input("Movie ID: ")
    database.watch_movie(user_name, movie_id)

def prompt_add_user():
    user_name = input("Enter user name: ")
    database.add_user(user_name)

def prompt_search():
    keyword = input("Enter keyword to search movies: ")
    results = database.search_movie(keyword)
    print_movie_list("Searched", results)

while (user_input := input(menu)) != "8":
    if user_input == "1":
        promt_add_movie()
    elif user_input == "2":
        movies = database.get_movies(upcoming=True)
        print_movie_list("Upcoming", movies)
    elif user_input == "3":
        movies = database.get_movies(upcoming=False)
        print_movie_list("All", movies)
    elif user_input == "4":
        prompt_watch_movie()
    elif user_input == "5":
        user_name = input("Enter your username: ")
        watched_movies = database.get_watched_movies(user_name)
        print_movie_list(f"{user_name}'s", watched_movies)
    elif user_input == "6":
        prompt_add_user()
    elif user_input == "7":
        prompt_search()
    else:
        print("Invalid input try again")