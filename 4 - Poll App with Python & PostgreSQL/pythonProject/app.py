import os
import psycopg2
# from psycopg2.error import DivisionByZero
import database
from dotenv import load_dotenv
from psycopg2.errors import DivisionByZero

load_dotenv()

DATABASE_PROMPT = "Enter the Database URL value or leave empty"

MENU_PROMT = """---MENU---
1 - Create a new poll 
2 - List open polls
3 - Vote on a poll
4 - Show poll votes
5 - Select a random winner from a poll option
6 - Exit
Enter your choice:
"""

NEW_OPTION_PROMPT = "Enter new option text (or leave empty to stop adding options): "

def prompt_create_poll(connection):
    poll_name = input("Enter poll title: ")
    poll_owner = input("Enter poll owner: ")
    options = []
    while new_options := input(NEW_OPTION_PROMPT):
        options.append(new_options)
    database.create_poll(connection, poll_name, poll_owner, options)

def list_open_poll(connection):
    polls = database.get_polls(connection)
    for _id, title, owner_name in polls:
        print(f"{_id}: {title} (created by {owner_name})")

def prompt_vote_poll(connection):
    print("Here are all open polls:")
    list_open_poll(connection)
    poll_id = int(input("Enter the poll that you'd like to vote for: "))
    poll_options = database.get_poll_details(connection, poll_id)
    print_poll_options(poll_options)

    username = input("Enter user name: ")
    option_id = int(input("Enter option you'd like to vote for: "))
    database.add_poll_vote(connection, username, option_id)

def print_poll_options(options: list[database.PollWithOption]):
    for option in options:
        print(f"{option[3]}: {option[4]}")

def show_poll_votes(connection):
    print("Choose the id of poll from open rolls: ")
    list_open_poll(connection)
    poll_id = int(input("Enter the poll id: "))
    try:
        poll_and_votes = database.get_poll_and_vote_result(connection, poll_id)
    except DivisionByZero:
        print("No vote cast for this poll yet")
    else:
        for result in poll_and_votes:
            print(f"{result[1]} got {result[2]} votes ({result[3]:.2f}% of total)")
        # for _id, option_text, count, percentage in poll_and_votes:
        #     print(f"{option_text} got {count} votes ({percentage:.2f}% of total)")

def randommize_poll_winner(connection):
    print("Here are all opened polls: ")
    list_open_poll(connection)
    poll_id = int(input("Enter the poll id: "))
    poll_option = database.get_poll_details(connection, poll_id)
    print("Here are the options of the poll: ")
    print_poll_options(poll_option)
    option_id = int(input("Enter option id: "))
    winner = database.get_random_poll_vote(connection, option_id)
    print(f"The randomly selected winner is {winner[0]}.")

MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_poll,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randommize_poll_winner
}

def menu():
    DB_HOST = input("Enter the host: ")
    DB_NAME = input("Enter the database name: ")
    DB_USER = input("Enter the user name: ")
    DB_PASSWORD = input("Enter the password: ")
    DB_PORT = input("Enter the port: ")

    connection = psycopg2.connect(host=DB_HOST,
                                  database=DB_NAME,
                                  user=DB_USER,
                                  password=DB_PASSWORD,
                                  port=DB_PORT)
    # connection = database.connect()
    database.create_tables(connection)
    while (selection := input(MENU_PROMT)) != "6":
        try:
            MENU_OPTIONS[selection](connection)
        except KeyError:
            print("Invalid input selected. Try again.")

menu()








