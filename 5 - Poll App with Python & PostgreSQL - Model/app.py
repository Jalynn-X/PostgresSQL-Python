import os
import datetime
from random import choice

import psycopg2
import pytz

import database
from dotenv import load_dotenv
from connection_pool import get_connection
from Models.poll import Poll
from Models.option import Option

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

def prompt_create_poll():
    poll_name = input("Enter poll title: ")
    poll_owner = input("Enter poll owner: ")
    new_poll = Poll(poll_name, poll_owner)
    new_poll.save()
    while new_option := input(NEW_OPTION_PROMPT):
        new_poll.add_option(new_option)

def list_open_poll():
    polls = Poll.all()
    for poll in polls:
        print(f"{poll.id}: {poll.title} (created by {poll.owner})")
    # cannot use destructing like for _id, title, owner_name in polls:
    # because it is not a destructing thing

def prompt_vote_poll():
    print("Here are all open polls:")
    list_open_poll()
    poll_id = int(input("Enter the poll that you'd like to vote for: "))
    voted_poll = Poll.get(poll_id)
    poll_options = voted_poll.options()
    print_poll_options(poll_options)

    username = input("Enter user name: ")
    option_id = int(input("Enter option you'd like to vote for: "))
    voted_option = Option.get(option_id)
    voted_option.vote(username)


def print_poll_options(options: list[Option]):
    for option in options:
        print(f"{option.id}: {option.option_text}")
    # Note: here Option is not tuple in database.py but option class we imported

def show_poll_votes():
    print("Choose the id of poll from open rolls: ")
    list_open_poll()
    poll_id = int(input("Enter the poll id: "))
    poll = Poll.get(poll_id)
    options = poll.options()
    votes_per_option = [len(option.votes) for option in options]
    # notice: it is not option.votes but len()
    sum_votes = sum(votes_per_option)
    try:
        for option, votes in zip(options, votes_per_option):
            percentage = votes / sum_votes * 100
            print(f"{option.option_text} got {votes} votes ({percentage:.2f}% of total)")
    except ZeroDivisionError:
        print("No vote cast for this poll yet")
    vote_log = input("Do you want to see the vote log (y/n)?")
    if vote_log == "y":
        _print_votes_for_options(options)

def _print_votes_for_options(options: list[Option]):
    for option in options:
        print(f"--{option.option_text}--")
        votes = option.votes
        for vote in votes:
            utc_date = datetime.datetime.fromtimestamp(vote[2], datetime.UTC)
            local_date = utc_date.astimezone(pytz.timezone("Europe/London"))
            local_date_as_str = local_date.strftime("%Y-%m-%d %H:%M")
            print(f"\t -{vote[0]} on {local_date_as_str}")

def randommize_poll_winner():
    print("Here are all opened polls: ")
    list_open_poll()
    poll_id = int(input("Enter the poll id: "))
    poll = Poll.get(poll_id)
    poll_option = poll.options()
    print("Here are the options of the poll: ")
    print_poll_options(poll_option)
    option_id = int(input("Enter option id: "))
    option = Option.get(option_id)
    try:
        winner = choice(option.votes)
        print(f"The randomly selected winner is {winner[0]}.")
    except IndexError:
        print("There is no random winner because no one has voted for this option yet.")

MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_poll,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randommize_poll_winner
}

def menu():
    with get_connection() as connection:
        database.create_tables(connection)
        while (selection := input(MENU_PROMT)) != "6":
            try:
                MENU_OPTIONS[selection]()
            except KeyError:
                print("Invalid input selected. Try again.")

menu()








