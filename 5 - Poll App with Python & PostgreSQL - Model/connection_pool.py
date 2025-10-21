from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        user=input("Enter user: "),
        password=input("Enter password: "),
        host=input("Enter host: "),
        port=int(input("Enter port: ")),
        database=input("Enter database: ")
    )

@contextmanager
def get_connection():
    connection = pool.getconn()
    try:
        yield connection
    finally:
        pool.putconn(connection)

        # getconn(): checkout a connection from the pool.
        # putconn(conn): check the connection back in.