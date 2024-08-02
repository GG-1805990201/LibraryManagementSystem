import logging
import sqlite3


def create_tables():
    connection = sqlite3.connect('database.db')

    with open('/Users/DELL/PycharmProjects/LibraryManagementSystem/schema/schema.sql') as f:
        connection.executescript(f.read())
    print('Tables created successfully')


def get_db_connection():
    conn = sqlite3.connect('config/database.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == '__main__':
    create_tables()
