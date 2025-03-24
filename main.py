from Database import Database


def main():
    db = Database('test.db')
    db.add_user('Griffin', '12345')
    db.add_user('Sam', '234')
    db.add_user('Sam', '4567')
    db.delete_user('Nort')
    db.delete_user('Sam')
    print(db._view_all('Users'))


if __name__ == '__main__':
    main()
