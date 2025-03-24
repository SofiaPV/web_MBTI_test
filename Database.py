import sqlite3


class Database:
    def __init__(self, database_name):
        self._db_name = database_name
        self._conn = sqlite3.connect(database_name)
        self._cursor = self._conn.cursor()
        self.__create_tables()

    def __create_tables(self):
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_name TEXT NOT NULL,                     
                user_password TEXT NOT NULL 
            )
        """)

        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_result (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                result TEXT NOT NULL,   
                datetime INTEGER NOT NULL,                  
                user_id INTEGER NOT NULL 
            )
        """)

        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS Answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                result_id INTEGER NOT NULL,
                test_id INTEGER NOT NULL,                     
                number INTEGER NOT NULL,
                answer INTEGER NOT NULL
            )
        """)

        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test (
                test_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                test_name TEXT NOT NULL
            )
        """)

        self._conn.commit()  # saving results

    def add_user(self, name, password):
        """
        adds information about user into 'Users' table
        :param name: unique name
        :param password: hashed password
        :return: True if successful, False otherwise
        """

        self._cursor.execute("SELECT COUNT(*) FROM Users WHERE user_name = ?",
                             (name,))
        if self._cursor.fetchone()[0] > 0:
            return False
        try:
            self._cursor.execute("INSERT INTO Users (user_name, user_password) VALUES (?, ?)",
                                 (name, password))

        except Exception as e:
            print(f'Приозошла ошибка: {e}')
            return False
        self._conn.commit()
        return True

    def delete_user(self, name):
        """
        deletes user by specific name
        :param name: unique user name
        :return: True if successful, False otherwise
        """
        try:
            self._cursor.execute("DELETE FROM Users WHERE user_name = ?",
                                 (name,))
        except Exception as e:
            print(f'Произошла ошибка: {e}')
            return False
        self._conn.commit()
        return True

    def _view_all(self, name):
        self._cursor.execute(f"SELECT * FROM {name}")
        return self._cursor.fetchall()
