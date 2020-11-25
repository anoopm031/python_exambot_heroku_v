import psycopg2
from psycopg2.extras import Json
from urllib.parse import urlparse
import logging
from sys import stdout

store_logger = logging.getLogger(__name__)
store_logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')
file_handler = logging.FileHandler('./logs/store.log')
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(stdout)
console_handler.setFormatter(formatter)
store_logger.addHandler(console_handler)
store_logger.addHandler(file_handler)


connected = False


while not connected:
    try:
        db_url = "postgres://postgres uri here"
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        store_logger.info('connecting to database...')
        connection = psycopg2.connect(user=username, password=password, host=hostname, database=database)

        cursor = connection.cursor()

        store_logger.info(connection.get_dsn_parameters())

        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        store_logger.info(f"You are connected to -  {version}")
        connected = True
    except:
        store_logger.exception('Failed to start connection')
        connected = False


def create_my_tables():
    try:
        print('Creating tables')
        store_logger.info('Initialising tables creations')
        create_user_table = """CREATE TABLE user_table(user_id BIGINT PRIMARY KEY, username VARCHAR(100),
        user_admin_tests TEXT[],user_attended_tests TEXT[]);"""
        create_test_table = """CREATE TABLE "Test"(test_id VARCHAR(100) PRIMARY KEY, user_id BIGINT,
        test_name VARCHAR(200), active BOOLEAN, active_till TIMESTAMP, test_binary BYTEA);"""
        create_attempt_table = """CREATE TABLE attempt(attempt_id VARCHAR(100) PRIMARY KEY, user_id BIGINT,
        username VARCHAR(100), test_id VARCHAR(100), start_time TIMESTAMP, end_time TIMESTAMP, response JSONB,
        correct_answers INT, wrong_answers INT, mark FLOAT, time_taken INT);"""
        create_state_table = """CREATE TABLE state_data(num INT PRIMARY KEY, user_dict_bin BYTEA,
        user_attempt_bin BYTEA, handler_bin BYTEA);
        INSERT INTO state_data(num) VALUES(1);"""
        create_tables_queries = [create_user_table, create_test_table, create_attempt_table, create_state_table]
        for query in create_tables_queries:
            cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        return 1
    except:
        store_logger.exception('create table error')
        return 0


# to create a user - returns user id
def create_user(user_id, username):
    try:
        store_logger.info(f'create user started {user_id}')
        cursor.execute("""INSERT INTO user_table(user_id,username) VALUES (%s, %s) RETURNING user_id;""", (user_id, username))
        connection.commit()
        user_id_retuned = cursor.fetchone()
        store_logger.debug(f'create user {user_id_retuned}')
        user_id_r = user_id_retuned[0]
        return user_id_r
    except:
        store_logger.exception('create user')


# to check whether user in is in db or not - returns user count
def check_user(user_id):
    try:
        store_logger.info(f'check user started {user_id}')
        cursor.execute("SELECT COUNT(user_id) FROM user_table WHERE user_id = %s;", (user_id,))
        user_count = cursor.fetchone()
        store_logger.debug(f'check user {user_count}')
        return user_count[0]
    except:
        store_logger.exception('check user')


# to get user details from db - returns a tuple with user details
def get_user(user_id):
    try:
        store_logger.info(f'get user started {user_id}')
        cursor.execute("SELECT * FROM user_table WHERE user_id = %s;", (user_id,))
        user_tuple = cursor.fetchone()
        store_logger.debug(f'get_user {user_tuple}')
        return user_tuple
    except:
        store_logger.exception('get user')


# to add a test details to db - returns test id
def add_test(test, binary_test):
    try:
        store_logger.info(f'add test started {test.test_id}')
        cursor.execute("""INSERT INTO "Test"(test_id, user_id, test_name, active,
        active_till, test_binary) VALUES(%s, %s, %s, %s, %s, %s) RETURNING test_id;""", (test.test_id,
                                                                                         test.test_admin, test.test_name, test.active,
                                                                                         test.end_date, binary_test))
        connection.commit()
        result = cursor.fetchone()
        store_logger.debug(f'add test {result}')
        return result[0]
    except:
        store_logger.exception('add test')
        return 0


def get_test_binary(test_id):
    try:
        store_logger.info(f'getting test binary for {test_id}')
        cursor.execute("""SELECT test_binary FROM "Test" WHERE test_id = %s;""", (test_id,))
        test_tuple_return = cursor.fetchone()
        if test_tuple_return is not None:
            print(f'test binary is retrieved tuple {test_tuple_return}')
            test_binary = test_tuple_return[0]
            return test_binary
        else:
            print(f'test binary is not retrieved tuple {test_tuple_return}')
            return 0
    except:
        store_logger.exception('get test binary error')
        return 0


# to get a test's details from db - returns a tuple with test details, just like attempt
def get_test(test_id):
    try:
        store_logger.info(f'get test started {test_id}')
        cursor.execute("""SELECT test_id, user_id, test_name, active,
        active_till FROM "Test" WHERE test_id = %s;""", (test_id,))
        test_return = cursor.fetchone()
        store_logger.debug(f'get test {test_return}')
        if test_return is not None:
            return test_return
        else:
            return 0
    except:
        store_logger.exception('get test')
        return 0


# to get the name of a test - returns test name
def get_test_name(test_id):
    try:
        store_logger.info(f'get test name started {test_id}')
        cursor.execute("""SELECT test_name FROM "Test" WHERE test_id = %s;""", (test_id,))
        test_name_tuple = cursor.fetchone()
        store_logger.debug(f'get test name {test_name_tuple}')
        if test_name_tuple is not None:
            return test_name_tuple[0]
        else:
            return 0
    except:
        store_logger.exception('get test name')
        return 0


# to check whether the selected user is an admin of test or not - returns an integer depending on true false or none
def is_user_admin(user_id, test_id):
    try:
        store_logger.info(f'is user admin started {user_id, test_id}')
        cursor.execute("""SELECT user_id FROM "Test" WHERE test_id = %s;""", (test_id,))
        returned_user_id = cursor.fetchone()
        store_logger.debug(f'is user admin {returned_user_id}')
        if returned_user_id is None:
            return 2  # test does not exist in db
        elif returned_user_id[0] == int(user_id):
            return 1
        else:
            return 0
    except:
        store_logger.exception('is user admin')
        return 0


# to add an attempt to the db - returns attempt id
def add_attempt(attempt):
    try:
        store_logger.info('add attempt started')
        cursor.execute("""INSERT INTO attempt(attempt_id, user_id, username, test_id, start_time,
        end_time, response, correct_answers, wrong_answers, mark, time_taken)VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING attempt_id;""",
                       (attempt.attempt_id, attempt.user_id, attempt.username, attempt.test_id, attempt.start_time,
                        attempt.end_time, Json(attempt.response), attempt.correct_ans, attempt.wrong_ans,
                        attempt.mark, attempt.time_taken))
        connection.commit()
        returned = cursor.fetchone()
        store_logger.debug(f'add attempt {returned}')
        return returned
    except:
        store_logger.exception('add attempt')
        return 0


# to get an attempt from db - returns a tuple
def get_attempt(attempt_id):
    try:
        store_logger.info(f'get attempt started {attempt_id}')
        cursor.execute("""SELECT * FROM attempt WHERE attempt_id = %s;""", (attempt_id,))
        attempt = cursor.fetchone()
        store_logger.debug(f'get attempt {attempt}')
        if attempt is not None:
            return attempt
        else:
            return 0
    except:
        store_logger.exception('get attempt')
        return 0


# to modify user admin tests in user table - returns user id
def modify_admin_tests(user_id, new_test):
    try:
        store_logger.info(f'modify admin test started {user_id}')
        cursor.execute("SELECT user_admin_tests FROM user_table WHERE user_id = %s;", (user_id,))
        current_admin_test = cursor.fetchone()
        store_logger.debug(f'admin test {current_admin_test}')
        if current_admin_test[0] is None:
            admin_tests = [new_test]
            cursor.execute("UPDATE user_table SET user_admin_tests = %s WHERE user_id = %s RETURNING user_id;",
                           (admin_tests, user_id))
        else:
            if new_test not in current_admin_test[0]:
                current_admin_test[0].append(new_test)
                cursor.execute("UPDATE user_table SET user_admin_tests = %s WHERE user_id = %s RETURNING user_id;",
                               (current_admin_test[0], user_id))
            else:
                store_logger.debug('test already added')
        connection.commit()
        result = cursor.fetchone()
        store_logger.debug(f'modify admin tests for user id {result}')
        if result is not None:
            return result[0]
        else:
            return 0
    except:
        store_logger.exception('modify admin tests')
        return 0


# to get user admin tests from user table - returns a list
def get_admin_tests(user_id):
    try:
        store_logger.info(f'get admin tests started {user_id}')
        cursor.execute("""SELECT user_admin_tests FROM user_table WHERE user_id = %s;""", (user_id, ))
        admin_tests_result = cursor.fetchone()
        store_logger.debug(f'get admin tests for user id {admin_tests_result}')
        if admin_tests_result is not None:
            return admin_tests_result[0]
        else:
            return 0
    except:
        store_logger.exception('get admin tests')
        return 0


# to modify user attended test in user table - returns user_id
def modify_attended_tests(user_id, new_test):
    try:
        store_logger.info(f'modify attended tests {user_id}')
        cursor.execute("SELECT user_attended_tests FROM user_table WHERE user_id = %s;", (user_id,))
        current_attended_test = cursor.fetchone()
        if current_attended_test[0] is None:
            attended_tests = [new_test]
            cursor.execute("UPDATE user_table SET user_attended_tests = %s WHERE user_id = %s RETURNING user_id;",
                           (attended_tests, user_id))
        else:
            if new_test not in current_attended_test[0]:
                current_attended_test[0].append(new_test)
                cursor.execute("UPDATE user_table SET user_attended_tests = %s WHERE user_id = %s RETURNING user_id",
                               (current_attended_test[0], user_id))
            else:
                store_logger.debug('test already added')
        connection.commit()
        result = cursor.fetchone()
        store_logger.debug(f'modify attended tests for user id {result}')
        if result is not None:
            return result[0]
        else:
            return 0
    except:
        store_logger.exception('modify attended tests')
        return 0


# to get attended tests for a user from user table - returns a list
def get_attended_tests(user_id):
    try:
        store_logger.info(f'get_attenpted test started {user_id}')
        cursor.execute("""SELECT user_attended_tests FROM user_table WHERE user_id = %s;""", (user_id, ))
        attended_tests_result = cursor.fetchone()
        store_logger.debug(f'get attended tests for user id {attended_tests_result}')
        if attended_tests_result is not None:
            return attended_tests_result[0]
        else:
            return 0
    except:
        store_logger.exception('get attended tests')
        return 0


# to get all the attempts for a test from attempt table - returns a list of tuples (coz fetchall is used)
def get_attempt_test(test_id):
    try:
        store_logger.info(f'get attempt test started {test_id}')
        cursor.execute("""SELECT username, start_time, time_taken, correct_answers, wrong_answers, mark
         FROM attempt WHERE test_id = %s;""", (test_id,))
        attempts_list_tuple = cursor.fetchall()
        store_logger.debug(f'get attempts for test_id {attempts_list_tuple}')
        if attempts_list_tuple is not None:
            return attempts_list_tuple
        else:
            return 0
    except:
        store_logger.exception(f'get attempt test')
        return 0


# used to get the attempts by the user for a specific test - returns a list of tuples
def get_user_test_attempt(user_id, test_id):
    try:
        store_logger.info(f'get user test attempt {user_id}')
        cursor.execute("""SELECT start_time, time_taken, correct_answers, wrong_answers, mark FROM attempt
        WHERE user_id = %s AND test_id = %s;""", (user_id, test_id))
        req_attempts_list = cursor.fetchall()
        store_logger.debug(f'get user test attempt {req_attempts_list}')
        if req_attempts_list is not None:
            return req_attempts_list
        else:
            return 0
    except:
        store_logger.exception('get user test attempt')
        return 0


# add username to attempt db - returns attempt_id if success
def set_attempt_username(attempt_id, username):
    try:
        store_logger.info('set_attempt username started')
        cursor.execute("""UPDATE attempt SET username = %s WHERE attempt_id = %s RETURNING attempt_id;""",
                       (username, attempt_id))
        returned_a_id = cursor.fetchone()
        print(returned_a_id)
        print(f'attempt username added {returned_a_id[0] == attempt_id}')
        if returned_a_id is not None:
            return returned_a_id[0]
        else:
            return 0
    except:
        store_logger.exception('set attempt username')
        return 0


def add_state_binary(user_dict_bin, user_attempt_bin, handler_bin):
    try:
        store_logger.info("Dumping state pickle to db")
        cursor.execute("""UPDATE state_data SET user_dict_bin = %s, user_attempt_bin = %s,
        handler_bin = %s WHERE num = 1 RETURNING num;""", (user_dict_bin, user_attempt_bin, handler_bin))
        connection.commit()
        returned_num = cursor.fetchone()
        print(f'add state binary success {returned_num[0]==1}')
        if returned_num is not None:
            return returned_num[0]
        else:
            return 0
    except Exception as exc:
        print('add state binary error', exc)
        store_logger.exception('add state binary failed')
        return 0


def get_state_binary():
    try:
        store_logger.info('Getting state binaries')
        cursor.execute("""SELECT user_dict_bin, user_attempt_bin, handler_bin FROM state_data WHERE num =1;""")
        state_bin_tuple = cursor.fetchone()
        if state_bin_tuple is not None:
            print('get state bin couple', state_bin_tuple, type(state_bin_tuple))
            return state_bin_tuple
        else:
            return 0
    except Exception as exc:
        print('get state binary error')
        return 0


def select_all():
    try:
        store_logger.warning('select all started')
        cursor.execute("SELECT * FROM \"user_table\";")
        users = cursor.fetchall()
        for user in users:
            user_id = user[0]
            username = user[1]
            store_logger.debug(f'user_id {user_id}\nusername {username}')
    except:
        store_logger.exception('select all')
        return 0


def close():
    try:
        if connection:
            store_logger.info('Closing postgres cursor and connection')
            cursor.close()
            connection.close()
            store_logger.info("PostgreSQL connection is closed")
            # closing database connection.
    except:
        store_logger.exception('close')
