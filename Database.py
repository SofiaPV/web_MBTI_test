import sqlite3, json
from user import User


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
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Users WHERE user_name = ?",
                             (name,))
        if cursor.fetchone()[0] > 0:
            return False
        try:
            cursor.execute("INSERT INTO Users (user_name, user_password) VALUES (?, ?)",
                                 (name, password))
            conn.commit()

        except Exception as e:
            print(f'Произошла ошибка: {e}')
            return False
        return True

    def delete_user(self, user_id):
        """
        deletes user by specific name
        :param user_id: unique id
        :return: True if successful, False otherwise
        """
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM Answers 
                WHERE result_id IN (SELECT result_id FROM Test_result WHERE user_id = ?)
            """, (user_id,))
            cursor.execute("UPDATE Test_result SET user_id = 0 WHERE user_id = ?",
                                 (user_id,))
            cursor.execute("DELETE FROM Users WHERE user_id = ?",
                                 (user_id,))
            conn.commit()
            
        except Exception as e:
            print(f'Произошла ошибка: {e}')
            return False
        return True

    def write_test_answer(self, result, file=None):
        """
        writes MBTI type and answers on questions into tables
        :param result: str, MBTI type
        :param file: a dict {"answers": [1, ..., i], "test_id": i, "datetime": 1,
                         "user_id": 1}. If None, only result will be written.
        :return: True if successful, False otherwise
        """
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        datetime, user_id = 0, 0
        if file:
            datetime, user_id = file['datetime'], file['user_id']
        try:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE user_id = ?",
                                 (user_id,))
            if cursor.fetchone()[0] == 0:
                print(f"No user {user_id} in Users")
                return False
            cursor.execute("INSERT INTO Test_result (result, datetime, user_id) VALUES (?, ?, ?)",
                                 (result, datetime, user_id if file else 0))
            conn.commit()
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            return False
        if file:
            self._write_answers(cursor.lastrowid, file)
        return True

    def _write_answers(self, result_id, file):
        """
        writes answers into Answers table
        :param result_id: result_id of this test
        :param file: a dict {"answers": [1, ..., i], "test_id": i, "datetime": 1,
                         "user_id": 1}
        :return: True if successful, False otherwise
        """

        test_id = file['test_id']
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        try:
            for num, ans in enumerate(file['answers']):
                cursor.execute("""
                    INSERT INTO Answers (result_id, test_id, number, answer) 
                    VALUES (?, ?, ?, ?)
                """, (result_id, test_id, num+1, ans))
        except Exception as e:
            print(f'Неизвестная ошибка: {e}')
            return False
        conn.commit()
        return True

    def _view_all(self, name):
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {name}")
        return cursor.fetchall()
    
    def get_statistics(self):
        """
        gets statistics of all users
        :return: statistics of all users
        """
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT result, COUNT(*) FROM Test_result 
            GROUP BY result
        """)
        return cursor.fetchall()
    
    def get_user_statistics(self, user_id):
        """
        gets statistics of user
        :param user_id: unique user id
        :return: statistics of user
        """
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT result, COUNT(*) FROM Test_result 
            WHERE user_id = ?
            GROUP BY result
        """, (user_id,))
        return cursor.fetchall()

    def get_latest_result(self, uid):
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        result = cursor.execute(
            "SELECT result FROM Test_result WHERE user_id = ? ORDER BY datetime DESC LIMIT 1",
            (uid,)
        ).fetchone()
        return result[0] if result else None

    def get_user_by_username(self, username):
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        result = cursor.execute(
            "SELECT user_id, user_name, user_password FROM users WHERE user_name = ?",
            (username,)
        ).fetchone()

        if result:
            return User(user_id=result[0],
                        username=result[1],
                        password_hash=result[2])
        return None

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self._db_name)
        cursor = conn.cursor()
        result = cursor.execute(
            "SELECT user_id, user_name, user_password FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if result:
            return User(user_id=result[0],
                        username=result[1],
                        password_hash=result[2])
        return None