"""
This fixture will create a brand new db for each function,
and run sql files to define all of the schemas, tables, relations, etc.
No data will be added however.

You shouldn't need to import any of these fixtures except the last one, client

If you need to add data to the empty db, do that in each test.

Once each function is completed, the db will be destroyed.
"""


import os
import secrets
import string
from collections.abc import Generator
from typing import Any, Tuple

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


@pytest.fixture(scope="session")
def pg_connection() -> Generator[Connection, Any, None]:
    """Create a connection to the db.

    We define this with scope session so that the connection doesn't
    have to be re-established for each test, which decreases performance.

    However, with the connection open,
    we drop and re-create the entire database with scope function
    to ensure a clean db for each test

    :return:
    """
    print("Creating connection to DB server")
    conn = create_engine(
        f"{settings.SQLALCHEMY_TESTING_DATABASE_URI}postgres",
    ).connect()
    conn.execute("commit")

    try:
        yield conn
    finally:
        print("Closing connection to DB server")
        conn.close()


@pytest.fixture(scope="function")
def init_pg_db(
    pg_connection: Connection,
) -> Generator[Tuple[Engine, sessionmaker], Any, None]:
    """Create and drop the database.

    This does not define the tables, etc. It only creates
    a blank db and returns that and a session to it.

    :return:
    """
    db_name = "sizzle_test_" + "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10)
    )
    pg_connection.execute("commit")
    pg_connection.execute(f'CREATE DATABASE "{db_name}"')

    print(f"Created test database {db_name}...")
    engine = create_engine(f"{settings.SQLALCHEMY_TESTING_DATABASE_URI}{db_name}")
    # Use connect_args parameter only with sqlite
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        yield engine, session
    finally:
        engine.dispose()
        pg_connection.execute("commit")
        pg_connection.execute(f'DROP DATABASE "{db_name}"')
        pg_connection.execute("commit")
        print(f"Deleted test database {db_name}...")


@pytest.fixture(scope="function")
def empty_pg_db(
    init_pg_db: Tuple[Engine, sessionmaker],
) -> Generator[Tuple[Connection, sessionmaker], Any, None]:
    """
    This gets the blank db and applies the sql files needed to recreate our
    production db structure. However, no data will be added.

    :param init_pg_db:
    :return:
    """
    (engine, session_testing) = init_pg_db
    connection = engine.connect()

    try:
        print(f"Base cwd is: {os.getcwd()}")
        with open("./tests/pg_db_setup/setup.sql", encoding="utf8") as file:
            query = text(file.read())
            connection.execute(query)

        # Make sure filenames are ordered properly in the directory
        # e.g. schemas that depend on other schemas are executed later, etc.
        files = [
            filename for filename in os.scandir("./tests/pg_db_setup/schemas") if filename.is_file()
        ]
        sorted_files = sorted(files, key=lambda f: f.name)

        for filename in sorted_files:
            print(f"Applying schema {filename.path}")
            with open(filename.path, encoding="utf8") as file:
                query = text(file.read())
                connection.execute(query)

        # Add any data that should be present in all tests
        with open("./tests/pg_db_setup/universal_data.sql", encoding="utf8") as file:
            query = text(file.read())
            connection.execute(query)

        yield connection, session_testing
    finally:
        connection.close()


@pytest.fixture(scope="function")
def db_session(
    empty_pg_db: Tuple[Connection, sessionmaker],
) -> Generator[Tuple[Connection, Session], Any, None]:
    """This will yield both a session and the connection.

    Typically the connection will be used to send raw SQL (e.g. inserting bulk records)
    and the session will be used for SQL Alchemy calls
    """
    session = None
    transaction = None
    (connection, session_testing) = empty_pg_db
    try:
        transaction = connection.begin()
        session = session_testing(bind=connection)
        yield connection, session  # use the session in tests.
    finally:
        if session is not None:
            session.close()
        if transaction is not None:
            transaction.rollback()
        connection.close()

