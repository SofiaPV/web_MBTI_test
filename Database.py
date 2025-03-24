import sqlite3, json


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
        self._cursor.execute("SELECT COUNT(*) FROM Users WHERE user_id=0")
        if self._cursor.fetchone()[0] == 0:
            self._cursor.execute("INSERT INTO Users (user_id, user_name, user_password) VALUES (?, ?, ?)",
                                 (0, 'AbstractUser', 'No'))

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
            self._cursor.execute("SELECT user_id FROM Users WHERE user_name = ?",
                                           (name,))
            user_id = self._cursor.fetchone()
            if not user_id:
                return False
            user_id = user_id[0]
            self._cursor.execute("""
                DELETE FROM Answers 
                WHERE result_id IN (SELECT result_id FROM Test_result WHERE user_id = ?)
            """, (user_id,))
            self._cursor.execute("UPDATE Test_result SET user_id = 0 WHERE user_id = ?",
                                 (user_id,))
            self._cursor.execute("DELETE FROM Users WHERE user_name = ?",
                                 (name,))
        except Exception as e:
            print(f'Произошла ошибка: {e}')
            return False
        self._conn.commit()
        return True

    def write_test_answer(self, result, filename=None):
        """
        writes MBTI type and answers on questions into tables
        :param result: str, MBTI type
        :param filename: a .json file {"answers": [1, ..., i], "test_id": i, "datetime": 1,
                         "user_id": 1}. If None, only result will be written.
        :return: True if successful, False otherwise
        """
        datetime, user_id = 0, 0
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                datetime, user_id = data['datetime'], data['user_id']
        try:
            self._cursor.execute("SELECT COUNT(*) FROM Users WHERE user_id = ?",
                                 (user_id,))
            if self._cursor.fetchone()[0] == 0:
                print(f"No user {user_id} in Users")
                return False
            self._cursor.execute("INSERT INTO Test_result (result, datetime, user_id) VALUES (?, ?, ?)",
                                 (result, datetime, user_id if filename else 0))
            self._conn.commit()
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            return False
        if filename:
            self._write_answers(self._cursor.lastrowid, filename)
        return True

    def _write_answers(self, result_id, filename):
        """
        writes answers into Answers table
        :param result_id: result_id of this test
        :param filename: a .json file {"answers": [1, ..., i], "test_id": i, "datetime": 1,
                         "user_id": 1}
        :return: True if successful, False otherwise
        """

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            test_id = data['test_id']
            try:
                for num, ans in enumerate(data['answers']):
                    self._cursor.execute("""
                        INSERT INTO Answers (result_id, test_id, number, answer) 
                        VALUES (?, ?, ?, ?)
                    """, (result_id, test_id, num+1, ans))
            except Exception as e:
                print(f'Неизвестная ошибка: {e}')
                return False
        self._conn.commit()
        return True

    def _view_all(self, name):
        self._cursor.execute(f"SELECT * FROM {name}")
        return self._cursor.fetchall()
