import store


def create_tables():
    try:
        result = store.create_my_tables()
        print('created tables', result == 1)
    except Exception as exc:
        print('Create table error',exc)
