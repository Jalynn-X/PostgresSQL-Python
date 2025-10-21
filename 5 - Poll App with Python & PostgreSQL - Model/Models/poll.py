from psycopg2 import connect
import database
from connection_pool import get_connection
from Models.option import Option

class Poll:
    def __init__(self, title: str, owner: str, _id: int = None):
        # id = None means that it still waits for being created
        self.title = title
        self.owner = owner
        self.id = _id

    def __repr__(self):
        return f"Poll({self.title!r}, {self.owner!r}, {self.id!r})"
        # r means it will print as what it would look like for the string to be valid in python
        # Poll('title', 'owner', 'id')
        # __repr__ returns a string that can be used to recreate an object it represents

    def save(self):
        with get_connection() as connection:
            new_poll_id = database.create_poll(connection, self.title, self.owner)
            self.id = new_poll_id

    def add_option(self, option_text: str):
        Option(option_text, self.id).save()


    def options(self) -> list[Option]:
        with get_connection() as connection:
            options = database.get_poll_options(connection, self.id)
            return [Option(option[1], option[2], option[0]) for option in options]
            # option[1]: option_text TEXT,
            # option[2]: poll_id INTEGER
            # option[0]: id SERIAL PRIMARY KEY,

    @classmethod
    def get(cls, poll_id: int) -> "Poll":
        with get_connection() as connection:
            poll = database.get_poll(connection, poll_id)
            return cls(poll[1], poll[2], poll[0])

    @classmethod
    def all(cls) -> list["Poll"]:
        with get_connection() as connection:
            polls = database.get_polls(connection)
            return [cls(poll[1], poll[2], poll[0]) for poll in polls]

    @classmethod
    def latest(cls, poll_id: int) -> "Poll":
        with get_connection() as connection:
            poll = database.get_latest_poll(connection, poll_id)
            return cls(poll[1], poll[2], poll[0])

