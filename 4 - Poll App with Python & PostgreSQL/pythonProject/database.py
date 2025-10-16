import os
from symbol import return_stmt

import psycopg2
import datetime
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from typing import Tuple
load_dotenv()


Poll = Tuple[int, str, str]
Vote = Tuple[str, int]
PollWithOption = Tuple[int, str, str, int, str, int]
PollResults = Tuple[int, str, int, float]

def connect():
    connection = psycopg2.connect(host=os.environ["DB_HOST"],
                              database=os.environ["DB_NAME"],
                              user=os.environ["DB_USER"],
                              password=os.environ["DB_PASSWORD"],
                              port=os.environ["DB_PORT"])
    return connection

# create table queries
CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls (
    id SERIAL PRIMARY KEY, title TEXT, owner_name TEXT);"""

CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options (
    id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER, FOREIGN KEY(poll_id) REFERENCES polls(id));"""

CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes (
    user_name TEXT, option_id INTEGER, FOREIGN KEY (option_id) REFERENCES options(id));"""

# select queries
SELECT_ALL_POLLS = """SELECT * FROM polls;"""

SELECT_POLL_WITH_OPTIONS = """SELECT polls.*, options.* FROM polls
    JOIN options ON polls.id = options.poll_id 
    WHERE polls.id = %s;"""

SELECT_LATEST_POLL = """SELECT * FROM polls
    JOINT options ON polls.id = options.poll_id 
    WHERE polls.id = (SELECT id FROM polls ORDER BY id DESC LIMIT 1);"""
# with latest_id as (SELECT id FROM polls ORDER BY id DESC LIMIT 1)
# SELECT * FROM polls JOINT options ON polls.id = options.poll_id where polls.id = latest_id;

SELECT_RANDOM_VOTE = """SELECT * FROM votes WHERE option_id = %s ORDER BY RANDOM() LIMIT 1;"""
# ORDER BY RANDOM() gonna shuffle the rows

SELECT_POLL_VOTE_DETAIL = """
SELECT 
    options.id, 
    options.option_text, 
    COUNT(votes.option_id) AS vote_count, 
    COUNT(votes.option_id) / SUM(COUNT(votes.option_id)) OVER() * 100 AS vote_percentage
FROM options
LEFT JOIN votes ON options.id = votes.option_id
WHERE options.poll_id = %s
GROUP BY options.id;
"""
# the window funtion OVER() will ignore the group by and sum all
# the window funcion has access to everything in the from cause
# if with grouping, aggregation, and having filter, window function is after them
# the rows seen by the window funtion are the group rows instead of the original table rows from FROM/WHERE

SELECT_HIGH_VOTE = """
SELECT DISTINCT ON (options.poll_id) poll_id, option_id, options.option_text, 
COUNT(votes.option_id) as vote_count
FROM options
LEFT JOIN votes ON options.id = votes.option_id
GROUP BY options.id
ORDER BY poll_id, vote_count DESC; 
"""
# the DISTINCT ON allows to keep the first row of the returned result, after grouping and order
# unique on PostgreSQL
# DISTINCT a, b, c will consider unique combination of a, b, c

# insert queries
INSERT_POLL = """INSERT INTO polls (title, owner) VALUES (%s, %s);"""

INSERT_OPTION = """INSERT INTO options (option_text, poll_id) VALUES (%s, %s);"""

INSERT_VOTE = """INSERT INTO votes (user_name, option_id) VALUES (%s, %s);"""

# INSERT_POLL = """INSERT INTO polls (title, owner_name) VALUES (%s, %s);"""

# functions
def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_POLLS)
            cursor.execute(CREATE_OPTIONS)
            cursor.execute(CREATE_VOTES)

def get_polls(connection) -> list[Poll]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_POLLS)
            return cursor.fetchall()

def get_poll_details(connection, poll_id: int) -> list[PollWithOption]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_WITH_OPTIONS, (poll_id,))
            return cursor.fetchall()
# the type hint will tell the function that the parameter is in integer type
# it is not going to be an error but a warning

def get_latest_poll(connection, poll_id: int) -> list[PollWithOption]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_LATEST_POLL)
            return cursor.fetchall()

def get_poll_and_vote_result(connection, poll_id: int) -> list(PollResults):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_POLL_VOTE_DETAIL, (poll_id,))
            return cursor.fetchall()

def get_random_poll_vote(connection, option_id: int) -> Vote:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_RANDOM_VOTE, (option_id,))
            return cursor.fetchone()
# get a vote instead of a list, so it can write Vote instead of list[Vote]

def create_poll(connection, title: str, owner: str, options: list[str]):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO polls (title, owner_name) VALUES (%s, %s) RETURNING id;", (title, owner))
            # this will insert into the poll table but only available to this transaction
            # you will have access to this data produced with this connection
            # it is possible to select id from polls
            # if without the RETURNING keyword, we can use select query to get the last id
            # cursor.execute(INSERT_POLL, (title, owner))
            # cursor.execute("SELECT id FROM polls ORDER BY id DESC LIMIT 1;")
            poll_id = cursor.fetchone()[0]
            option_values = [(option_text, poll_id) for option_text in options]
            # options is input by users and is a list of all values
            # to be inserted into table, each value should be insert as a row

            #execute_values(cursor, INSERT_OPTION, option_values)
            # using the execute_values to take in each of the tuple in the list and pass into the query and run with cursor
            for option_value in option_values:
                cursor.execute(INSERT_OPTION, (option_value, poll_id))


def add_poll_vote(connection, username: str, option_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_VOTE, (username, option_id))



