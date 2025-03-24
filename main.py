from Database import Database


def main():
    db = Database('test.db')
    print(db._view_all('Users'))
    db.add_user('Griffin', '12345')
    print(db._view_all('Users'))
    db.add_user('Sam', '234')
    print(db._view_all('Users'))
    db.add_user('Sam', '4567')
    print(db._view_all('Users'))
    db.delete_user('Nort')
    print(db._view_all('Users'))
    db.delete_user('Sam')
    print(db._view_all('Users'))

    db.write_test_answer("INFJ", "./db_tests/1.json")
    print(db._view_all('Users'))
    print(db._view_all('Test_result'))
    print(db._view_all('Answers'))

    db.write_test_answer("ENTP", "./db_tests/1.json")
    print(db._view_all('Users'))
    print(db._view_all('Test_result'))
    print(db._view_all('Answers'))

    db.write_test_answer("ISTJ", "./db_tests/2.json")
    print(db._view_all('Users'))
    print(db._view_all('Test_result'))
    print(db._view_all('Answers'))

    db.write_test_answer("INFJ")
    print(db._view_all('Users'))
    print(db._view_all('Test_result'))
    print(db._view_all('Answers'))

    db.delete_user('Griffin')
    print(db._view_all('Users'))
    print(db._view_all('Test_result'))
    print(db._view_all('Answers'))


if __name__ == '__main__':
    main()
