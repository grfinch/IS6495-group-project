# Gaven Finch

import sqlite3


# DataBase base class (inherit from this)
class DBbase:

    _conn = None
    _cursor = None

    def __init__(self, db_name):
        self._db_name = db_name
        self.connect()

    def connect(self):
        self._conn = sqlite3.connect(self._db_name)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._cursor = self._conn.cursor()

    def execute_script(self, sql_string):
        self._cursor.executescript(sql_string)

    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._conn

    def reset_database(self):
        raise NotImplementedError("Must implement from the derived class")

    def close_database(self):
        self._conn.close()
