import os
from symbol import return_stmt

import psycopg2
import datetime
from dotenv import load_dotenv
from psycopg2.extras import execute_values
from typing import Tuple
from contextlib import contextmanager
load_dotenv()


Poll = Tuple[int, str, str]
Option = Tuple[int, str, int]
Vote = Tuple[str, int]

# create table queries
CREATE_POLLS = """CREATE TABLE IF NOT EXISTS polls (
    id SERIAL PRIMARY KEY, title TEXT, owner_name TEXT);"""

CREATE_OPTIONS = """CREATE TABLE IF NOT EXISTS options (
    id SERIAL PRIMARY KEY, option_text TEXT, poll_id INTEGER, FOREIGN KEY(poll_id) REFERENCES polls(id));"""

CREATE_VOTES = """CREATE TABLE IF NOT EXISTS votes (
    user_name TEXT, option_id INTEGER, vote_timestamp INTEGER, FOREIGN KEY (option_id) REFERENCES options(id));"""

# select queries
SELECT_ALL_POLLS = """SELECT * FROM polls;"""

SELECT_POLL = """SELECT * FROM polls where id = %s;"""

SELECT_POLL_OPTIONS = """SELECT * FROM options
    WHERE poll_id = %s;"""

SELECT_LATEST_POLL = """SELECT * FROM polls
    WHERE polls.id = (SELECT id FROM polls ORDER BY id DESC LIMIT 1);"""

SELECT_OPTION = """SELECT * FROM options where id = %s;"""

SELECT_VOTES_FOR_OPTION = """SELECT * FROM votes where option_id = %s;"""

# insert queries
INSERT_POLL = """INSERT INTO polls (title, owner) VALUES (%s, %s);"""

INSERT_OPTION_RETURNING_ID = """INSERT INTO options (option_text, poll_id) VALUES (%s, %s) RETURNING id;"""

INSERT_VOTE = """INSERT INTO votes (user_name, option_id, vote_timestamp) VALUES (%s, %s, %s);"""

# functions
@contextmanager
def get_cursor(connection):
    with connection:
        with connection.cursor() as cursor:
            yield cursor

def create_tables(connection):
    with get_cursor(connection) as cursor:
        cursor.execute(CREATE_POLLS)
        cursor.execute(CREATE_OPTIONS)
        cursor.execute(CREATE_VOTES)


# ---- Polls ----
def create_poll(connection, title: str, owner: str):
    with get_cursor(connection) as cursor:
        cursor.execute("INSERT INTO polls (title, owner_name) VALUES (%s, %s) RETURNING id;", (title, owner))
        poll_id = cursor.fetchone()[0]
        return poll_id

def get_polls(connection) -> list[Poll]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_ALL_POLLS)
        return cursor.fetchall()

def get_poll(connection, poll_id: int) -> Poll:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL, (poll_id,))
        return cursor.fetchone()
        # here returns the poll tuple instead of poll class

def get_latest_poll(connection) -> Poll:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_LATEST_POLL)
        return cursor.fetchone()

def get_poll_options(connection, poll_id: int) -> list[Option]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_POLL_OPTIONS, (poll_id,))
        return cursor.fetchall()

# ---- option ----
def get_option(connection, option_id: int) -> Option:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_OPTION, (option_id,))
        return cursor.fetchone()

def add_option(connection, option_text: str, poll_id: int):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_OPTION_RETURNING_ID, (option_text, poll_id))
        option_id = cursor.fetchone()[0]
        return option_id

# ---- vote ----
def get_votes_for_option(connection, option_id: int) -> list[Vote]:
    with get_cursor(connection) as cursor:
        cursor.execute(SELECT_VOTES_FOR_OPTION, (option_id,))
        return cursor.fetchall()

def add_poll_vote(connection, username: str, option_id: int, vote_timestamp):
    with get_cursor(connection) as cursor:
        cursor.execute(INSERT_VOTE, (username, option_id, vote_timestamp))



