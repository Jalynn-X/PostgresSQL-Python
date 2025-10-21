from psycopg2 import connect
import database
from connection_pool import get_connection
import datetime
import pytz

class Option:

    def __init__(self, option_text: str, poll_id: int, _id: int=None):
        self.option_text = option_text
        self.poll_id = poll_id
        self.id = _id

    def __repr__(self):
        return f"Option({self.option_text!r}, {self.poll_id!r}, {self.id!r})"

    def save(self):
        with get_connection() as connection:
            option_id = database.add_option(connection, self.option_text, self.poll_id)
            self.id = option_id

    @classmethod
    def get(cls, option_id: int) -> "Option":
        with get_connection() as connection:
            option = database.get_option(connection, option_id)
            return cls(option[1], option[2], option[0])

    def vote(self, user_name:str):
        with get_connection() as connection:
            current_datetime_utc = int(datetime.datetime.now(tz=pytz.utc).timestamp())
            database.add_poll_vote(connection, user_name, self.id, current_datetime_utc)

    @property
    def votes(self) -> list[database.Vote]:
        with get_connection() as connection:
            votes = database.get_votes_for_option(connection, self.id)
            return votes
    
