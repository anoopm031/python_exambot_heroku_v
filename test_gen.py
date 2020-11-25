import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup,\
    KeyboardButton, KeyboardButtonPollType, ReplyKeyboardRemove, InlineKeyboardButton
import time
import signal
import datetime as dt
import threading
from datetime import timedelta
import os
from sys import stdout
from flask import Flask, request
from classes import *
from add_tools import *
from user_class import *
import save_test
import store
import logging
from signal_h import GracefulKiller


test_gen_logger = logging.getLogger(__name__)
test_gen_logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')
file_handler = logging.FileHandler('./logs/test_gen.log')
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(stdout)
console_handler.setFormatter(formatter)
test_gen_logger.addHandler(console_handler)
test_gen_logger.addHandler(file_handler)

test_gen_logger.debug('Bot has started')

BOT_TOKEN = "bot_token"
server = Flask(__name__)

bot = telebot.TeleBot(token=BOT_TOKEN)

BOT_INTRO_MSG = 'Hi. This bot will help you create test or assignments'
ALL_TIME_COMMANDS = ['stop', 'cancel']
UNDO_COMMAND = ['undo']
welcome_message = "Welcome.📚 You can create tests or assignments with this bot. Please follow the instructions." \
                  "To start with, either send /new_test to create a test or /test_(test id here) to attempt a saved " \
                  "test\n\n Use /help command if you are a first time visitor of this bot."


ERROR_MESSAGE = 'Ooops!!!. Some error occured ‼'
CANCEL_CONF_MSG = "You have requested to cancel the creation of this test. send 'yes' to confirm and 'no'" \
                  " to continue making this test."
CANCEL_MSG = 'This test has been disregarded.'
VOID_COMMAND_MSG = 'This command is not valid at this point. Please read the last instrcutions once more.'
NO_SKIP_MSG = 'This step cannot be skipped. Please enter the required data to continue.'
HELP_PAGE_URL = 'You can use the following commands at appropriate times. Commands should always start with a / \n' \
                '/start - To start the bot \n' \
                '/help - To get help \n' \
                '/my_account - To see the details of all the tests created and/or attempted by you \n' \
                'Commands to use while creating a test\n' \
                '/new_test - To start creating a new test\n' \
                '/undo - To go back a step while creating a test \n' \
                '/skip - To skip a step while creating the test \n' \
                '/done - Send it when you are done creating the test \n' \
                '/cancel - To discard the test that is being created by you \n\n' \
                'Commands to use while attempting a test\n' \
                '/skipped - To see all the questions you skipped without answering\n' \
                '/marked - T0 see all the questions you marked while attempting\n' \
                '/qno (question number you want to see or attempt) - eg: /qno 5 \n' \
                '/stop - To stop the test you are attempting \n\n' \
                'Plese use this link to report any issues or for any suggestions.\n' \
                'https://forms.gle/YDPzoUxSHVKrLZsg6 \n\n' \
                'Test creation example video: https://youtu.be/RAUyG97eNis\n' \
                'Test attempting example video: https://youtu.be/U-ZEEzZlRVQ\n\n' \
                'Tip: You can directly click on these commands from message if it is shown in Blue color' \

TEST_SAVED_MSG = "Test saved successfully. ____test url here___"
STOP_MSG = 'Test has been stopped. This attempt is recorded. Evaluating your attempt.'
CANNOT_SEND_LOG_MSG = 'Ooops. I cannot send message also'

# user_list=[]

poll_markup=ReplyKeyboardMarkup(one_time_keyboard=True)
poll_markup.add(KeyboardButton('send me a poll', request_poll=KeyboardButtonPollType(type='quiz')))
hideBoard = ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard

ready_button_text = 'I am Ready'
ready_button_call = 'ready'
mark_button_text = 'Mark'
mark_button_call = 'mark'
marked_button_text = 'Marked ✅'
marked_button_call = 'unmark'
next_button_text = 'Next >>>'
next_button_call = 'next'
prev_button_text = '<<< Previous'
prev_button_call = 'prev'
admin_tests_text = 'Show my tests'
admin_tests_call = 'my_tests'
attended_test_text = 'My attempts'
attended_test_call = 'my_attempts'
admin_text = 'View all attempts of this test'
admin_call = 'admin_attempts'


mark_markup = InlineKeyboardMarkup()
mark_markup.add(InlineKeyboardButton(mark_button_text, callback_data=mark_button_call),
                InlineKeyboardButton(next_button_text, callback_data=next_button_call),
                InlineKeyboardButton(prev_button_text, callback_data=prev_button_call))

initial_mark_markup = InlineKeyboardMarkup()
initial_mark_markup.add(InlineKeyboardButton(mark_button_text, callback_data=mark_button_call),
                        InlineKeyboardButton(next_button_text, callback_data=next_button_call))
final_mark_markup = InlineKeyboardMarkup()
final_mark_markup.add(InlineKeyboardButton(mark_button_text, callback_data=mark_button_call),
                      InlineKeyboardButton(prev_button_text, callback_data=prev_button_call))


marked_markup = InlineKeyboardMarkup()
marked_markup.add(InlineKeyboardButton(marked_button_text, callback_data=marked_button_call),
                  InlineKeyboardButton(next_button_text, callback_data=next_button_call),
                  InlineKeyboardButton(prev_button_text, callback_data=prev_button_call))

initial_marked_markup = InlineKeyboardMarkup()
initial_marked_markup.add(InlineKeyboardButton(marked_button_text, callback_data=marked_button_call),
                          InlineKeyboardButton(next_button_text, callback_data=next_button_call))

final_marked_markup = InlineKeyboardMarkup()
final_marked_markup.add(InlineKeyboardButton(marked_button_text, callback_data=marked_button_call),
                        InlineKeyboardButton(prev_button_text, callback_data=prev_button_call))

ready_markup = InlineKeyboardMarkup()
ready_markup.add(InlineKeyboardButton(ready_button_text, callback_data=ready_button_call))

account_markup = InlineKeyboardMarkup()
account_markup.add(InlineKeyboardButton(admin_tests_text, callback_data=admin_tests_call),
                   InlineKeyboardButton(attended_test_text, callback_data=attended_test_call))


user_dict = {}          # user_id: user
poll_user_dict = {}       # poll id: user_id
user_attempt_dict = {}  # user_id: attempt.end_time

try:
    user_dict, user_attempt_dict, handler_loaded = save_test.load_back_user_dict()
    bot.next_step_backend.handlers = handler_loaded
    print('user dict loaded back')
    print(user_dict)
    print(user_attempt_dict)
    print(handler_loaded)
except Exception as exce:
    print('Error in loading req files', exce)


def time_checker():
    # user attempt dict
    active = True
    try:
        test_gen_logger.info('started in a daemon thread')
        while active:
            psuedo_user_attempt_dict = user_attempt_dict.copy()
            for user_id, end_time in psuedo_user_attempt_dict.items():
                if end_time <= dt.datetime.now():
                    _ = bot.send_message(user_id, 'Time over')
                    del user_attempt_dict[user_id]
                    stop_test(user_id)
            time.sleep(40)
    except Exception as error_in_thread:
        test_gen_logger.exception('time_checker')


time_thread = threading.Thread(target=time_checker, daemon=True)
time_thread.start()

killer = GracefulKiller()


def exit_checker(pid):
    loop = True
    while loop:
        time.sleep(5)
        if killer.kill_now:
            print('kill now', killer.kill_now)
            loop = False
            exit_stat = graceful_exit(pid)
            if exit_stat == 0:
                print('gracekill failed', exit_stat)


pid = os.getpid()
print('pid', pid)
exit_checker_thread = threading.Thread(target=exit_checker, daemon=True, args=(pid,))
exit_checker_thread.start()


def graceful_exit(pid):
    try:
        start_time = time.time()
        print('Trying user_dict_dump')
        save_test.dump_user_dict(user_dict, user_attempt_dict, bot.next_step_backend.handlers)
        print('Graceful exit can be done')
        end_time = time.time()
        time_taken = end_time - start_time
        print(time_taken, 'Seconds')
        store.close()
    except Exception as exc:
        print('Graceful exit failed')
        return 0
    finally:
        os.kill(pid, signal.SIGKILL)
        raise SystemError


def check_user(message):
    try:
        test_gen_logger.info(f'started {message.from_user.id}')
        user_id = message.from_user.id
        test_gen_logger.debug(user_id)
        username = message.from_user.first_name
        if message.from_user.last_name is not None:
            username += ' ' + message.from_user.last_name
        if len(username) > 99:
            username = username[0:100]
        if user_dict.get(user_id) is not None:
            return user_dict[user_id]

        elif store.check_user(user_id) == 1:
            test_gen_logger.debug('existing user')
            # change the code to check if the user is in the db and load
            user_db = store.get_user(user_id)
            user_dict[user_id] = User(user_db[0], user_db[1])
            return user_dict[user_id]
        else:
            test_gen_logger.debug('new user')
            user_dict[user_id] = User(message.from_user.id, username=username)
            # write user to database
            returned_uid = store.create_user(user_id, username)
            test_gen_logger.info(f'user created {returned_uid == user_id}')
            return user_dict[user_id]

    except Exception as exc:
        test_gen_logger.exception(f'check_user {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def poll_is_here(question, message):
    try:
        test_gen_logger.info(f'poll is here started {message.from_user.id}')
        question.poll_question = message.poll.question
        for option in message.poll.options:
            question.poll_options.append(option.text)
        question.correct_id = message.poll.correct_option_id
        question.correct_ans = question.poll_options[question.correct_id]
        return

    except Exception as exc:
        test_gen_logger.exception(f'poll is here {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def test_request_handler(message):
    try:
        test_gen_logger.info(f'test request handler started {message.from_user.id}')
        msg_words_list = list(message.text.split(' '))
        req_test_id = ' '.join(msg_words_list[1:])
        loaded_test = save_test.load_test_db(req_test_id)
        user_id = message.from_user.id
        user = user_dict[user_id]
        if loaded_test in [0, 1]:
            test_gen_logger.info('test_loading_error')
            _ = bot.send_message(message.from_user.id, 'Requested test could not be found')
            return 1
        else:
            test_gen_logger.info(f'loading success {loaded_test.test_id}')
            user.active_test = loaded_test
            send_test_details(message.from_user.id, loaded_test)
            return loaded_test.test_id
    except Exception as exc:
        test_gen_logger.exception(f'test_request_handler {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, 'Could not load the requested test')
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def test_view_handler(message):
    try:
        test_gen_logger.info(f'test view handler started {message.from_user.id}')
        msg_words_list = list(message.text.split('_'))
        req_test_id = ' '.join(msg_words_list[1:])
        test_gen_logger.debug(req_test_id)
        user_id = message.from_user.id
        admin_stat = store.is_user_admin(user_id, req_test_id)
        if admin_stat == 2:
            next_msg = 'Test does not exist in our Database'
            _ = bot.send_message(user_id, next_msg)
            test_gen_logger.info(next_msg)
            return
        elif admin_stat == 1:
            user = user_dict[user_id]
            test_name = store.get_test_name(req_test_id)
            if test_name == 0:
                _ = bot.send_message(user_id, 'Could not find the test on Database')
                return
            next_msg = f'Please use the following button to see all the recorded attempts of test \n{test_name}'
            call_back = admin_call + ' ' + req_test_id
            admin_markup = InlineKeyboardMarkup()
            admin_markup.add(InlineKeyboardButton(admin_text, callback_data=call_back))
            msg = bot.send_message(user_id, next_msg, reply_markup=admin_markup)
            user.active_admin_markup = msg
            return
        elif admin_stat == 0:
            next_msg = 'Could not find the test on database'
            _ = bot.send_message(user_id, next_msg)
            return
        else:
            message.text = '/view ' + req_test_id
            test_request_handler(message)
            return
    except Exception as exc:
        test_gen_logger.exception(f'test view handler {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def attempt_request_handler(message):
    try:
        test_gen_logger.info(f'attempt request handler {message.from_user.id}')
        user_id = message.from_user.id
        msg_words_list = list(message.text.split('_'))
        req_test_id = ' '.join(msg_words_list[1:])
        test_name = store.get_test_name(req_test_id)
        if test_name == 0:
            _ = bot.send_message(user_id, 'Could not find test on Database')
            return
        test_gen_logger.debug(req_test_id)
        user_test_attempts = store.get_user_test_attempt(user_id, req_test_id)
        if user_test_attempts == 0 or len(user_test_attempts) ==0:
            _ = bot.send_message(user_id, 'Could not find any attempt record. This could be an error from our end')
            return

        to_be_send = f'Details of your attempts for the test  {test_name} is given below. \n\n'
        attempt_no = 1
        for req_attempt in user_test_attempts:
            to_be_send = to_be_send + (str_check(attempt_no) + '. ' + 'Start time- ' + str_check(req_attempt[0])
                                       + '\n' + 'Time taken- ' + str_check(req_attempt[1]) + ' ' + 'Mins' + '\n' +
                                       'Correct answers- ' + str_check(req_attempt[2]) + '\n' + 'Wrong answers- ' +
                                       str_check(req_attempt[3]) + '\n' + 'Total mark- ' + str_check(req_attempt[4]) + '\n')
            attempt_no += 1

        _ = bot.send_message(user_id, to_be_send)
    except Exception as exc:
        test_gen_logger.exception(f'attempt viewer {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


'''
def confirm_cancel(message,test,func_name):
    if message.type=='text' and message.text in ['yes','Yes']:
        msg=bot.send_message(message.from_user.id,CANCEL_MSG)
    else:
        msg=bot.send_message(message.from_user.id,'You chose to continue with the test. Please continue '
                                                  'from where you left')
        bot.register_next_step_handler()
'''


def check_markup_attempt(message):
    try:
        test_gen_logger.info(f'checking markup attempt {message.from_user.id}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        if user.active_account_markup is not None:
            bot.delete_message(user_id, user.active_account_markup.message_id)
            user.active_account_markup = None
            return 0
        if user.active_admin_markup is not None:
            bot.delete_message(user_id, user.active_admin_markup.message_id)
            user.active_admin_markup = None
            return 0
        if user.active_markup_msg is not None:
            bot.delete_message(user_id, user.active_markup_msg.message_id)
            user.active_markup_msg = None
            return 0
        elif user.active_attempt_id is not None:
            next_msg = 'You are in the middle of attempting a test. Send /stop to stop the test'
            bot.send_message(user_id, next_msg)
            return 1
        else:
            return 0
    except Exception as exc:
        test_gen_logger.exception(f'check_markup_attempt {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, "Hehehe! Don't do that")
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def check_markup_for_no_cmnd(message):
    try:
        test_gen_logger.info(f'checking markup for no command {message.from_user.id}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        if user.active_markup_msg is not None:
            # user is about to start a test
            return 0
        if user.active_attempt_id is not None:
            next_msg = 'You are in the middle of attempting a test. Send /stop to stop the test'
            bot.send_message(message.from_user.id, next_msg)
            return 1
    except Exception as exc:
        test_gen_logger.exception(f'check markup for no command {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def send_evaluation(user_id):
    try:
        test_gen_logger.info(f'Send evaluation started {user_id}')
        user = user_dict[user_id]
        loaded_test = user.active_test
        attempt = user.attempt
        total_mark = 0
        correct_mark = loaded_test.correct_marks
        incorrect_mark = loaded_test.incorrect_marks
        max_marks = loaded_test.question_no * correct_mark
        total_correct = 0
        total_wrong = 0
        attended_questions = attempt.response.keys()
        for q_no in attended_questions:
            qstn = loaded_test.question_dict[q_no]
            if attempt.response[q_no] == qstn.correct_ans:
                total_mark += correct_mark
                total_correct += 1
            elif attempt.response[q_no] is None:
                pass
            elif attempt.response[q_no] != qstn.correct_id:
                total_mark += incorrect_mark
                total_wrong += 1
        attempt.mark = total_mark
        attempt.correct_ans = total_correct
        attempt.wrong_ans = total_wrong
        total_attended_q = total_correct + total_wrong
        eval_msg = f'{loaded_test.test_name}\n\n' \
                   f'Max mark : {max_marks}\n' \
                   f'Time taken : {attempt.time_taken} Minutes\n' \
                   f'You attempted {total_attended_q} out of {loaded_test.question_no} questions.\n' \
                   f'{total_correct} answers are correct and {total_wrong} answers are wrong\n\n' \
                   f'Your score is {total_mark} out of {max_marks}'
        _ = bot.send_message(user_id, eval_msg)
        test_gen_logger.debug(f'returned 0 {user_id}')
        return 0

    except Exception as exc:
        test_gen_logger.exception(f'evaluation {user_id}')
        try:
            bot.send_message(user_id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def time_in_minutes(time_delta):
    return int((time_delta.days*24*60) + (time_delta.seconds//60))


def stop_test(user_id):
    try:
        test_gen_logger.info(f'stopping test started {user_id}')
        user = user_dict[user_id]
        if user.active_attempt_id is not None:
            if user.active_poll is not None:
                bot.stop_poll(user_id, user.active_poll.message_id)
            if len(user.active_mark_skip_inlines) > 0:
                for msg in user.active_mark_skip_inlines:
                    bot.delete_message(user_id, msg.message_id)
            if user.active_poll_markup is not None:
                _ = bot.delete_message(user_id, user.active_poll_markup.message_id)
                user.active_poll_markup = None

            bot.send_message(user_id, STOP_MSG)
            attempt = user.attempt
            attempt.time_taken = time_in_minutes(dt.datetime.now() - attempt.start_time)
            send_evaluation(user_id)
            loaded_test = user.active_test
            # add attempt to db
            returned_id = store.add_attempt(attempt)
            test_gen_logger.info(f'attempt added  {attempt.attempt_id == returned_id}')
            # add test to attended tests
            returned_user_id = store.modify_attended_tests(user_id, loaded_test.test_id)
            test_gen_logger.info(f'attended_test added {returned_user_id == user_id}')
            if user_attempt_dict.get(user_id) is not None:
                del user_attempt_dict[user_id]
            user.active_mark_skip_inlines = []
            user.active_poll = None
            user.active_attempt_id = None
            user.active_markup_msg = None
            test_gen_logger.info(f'test stopped {user_id}')
            return 0
        else:
            next_msg = 'Send /start or /help to start'
            _ = bot.send_message(user_id, next_msg)
            test_gen_logger.info(f'No active test to stop {user_id}')
            return 0

    except Exception as exc:
        test_gen_logger.exception(f'stop_test {user_id}')
        user = user_dict[user_id]
        user.active_poll_markup = None
        user.active_mark_skip_inlines = []
        user.active_poll = None
        user.active_attempt_id = None
        user.active_markup_msg = None
        try:
            send_evaluation(user_id)
            bot.send_message(user_id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)
        finally:
            return 1


def create_skipped_inline(user_id, qstn_no_dict):
    try:
        test_gen_logger.info(f'create skipped inline started {user_id}')
        qns_inline_markup = InlineKeyboardMarkup()
        skipped_stat = False
        user = user_dict[user_id]
        attempt = user.attempt
        if len(qstn_no_dict) > 0:
            for value in qstn_no_dict.values():
                if attempt.response.get(value) is None:
                    qns_inline_markup.add(InlineKeyboardButton(value, callback_data=value))
                    skipped_stat = True
            if skipped_stat:
                return qns_inline_markup
            if not skipped_stat:
                return 1
        else:
            return 1
    except Exception as exc:
        test_gen_logger.exception('create skipped inline')


def create_marked_inline(qstn_no_dict):
    try:
        test_gen_logger.info('create marked inline started')
        qns_inline_markup = InlineKeyboardMarkup()
        if len(qstn_no_dict) > 0:
            for value in qstn_no_dict.values():
                qns_inline_markup.add(InlineKeyboardButton(value, callback_data=value))
            return qns_inline_markup
        else:
            return 1

    except Exception as exc:
        test_gen_logger.exception('create marked inline')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        test_gen_logger.info(f'send welcome started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        proceed_stat = check_markup_attempt(message)
        if proceed_stat == 1:
            return
        if message.text == '/start':
            _ =bot.send_message(message.from_user.id, welcome_message)

        elif message.text.startswith('/start'):
            test_request_handler(message)


    except Exception as exc:
        test_gen_logger.exception(f'send welcome {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['help'])
def help_handler(message):
    try:
        test_gen_logger.info(f'help handler started {message.from_user.id}')
        user_id = message.from_user.id
        _ = bot.send_message(user_id, HELP_PAGE_URL)
    except Exception as exc:
        test_gen_logger.exception(f'help handler {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['new_test'])
def new_test_welcome(message):
    try:
        test_gen_logger.info(f'new test welcome started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        proceed_stat = check_markup_attempt(message)
        if proceed_stat == 1:
            return
        test_gen_logger.debug(f'{user_id}:new_test')
        new_test_msg = "Good! Let's start creating your test. Enter your test name"
        msg = bot.send_message(message.from_user.id, new_test_msg)
        bot.register_next_step_handler(msg, test_name_process)
    except Exception as exc:
        test_gen_logger.exception(f'new test welcome {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['test'])
def test_keyword_catcher(message):
    try:
        test_gen_logger.info(f'test keyword catcher started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        proceed_stat = check_markup_attempt(message)
        if proceed_stat == 1:
            return
        if message.text == '/test':
            next_msg = "To attempt a test, send '/test (test_id)' or send /start or /help to start"
            _ = bot.send_message(message.from_user.id, next_msg)
        else:
            test_request_handler(message)
    except Exception as exc:
        test_gen_logger.exception(f'test keyword catcher {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['my_account'])
def account_details(message):
    try:
        test_gen_logger.info(f'account details started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        proceed_stat = check_markup_attempt(message)
        if proceed_stat == 1:
            return
        if message.text == '/my_account':
            next_msg = f'Hi {user.username}. Use the below buttons to find required details'
            msg = bot.send_message(user_id, next_msg, reply_markup=account_markup)
            user.active_account_markup = msg
        else:
            _ = bot.send_message(user_id, 'Send /help to get help')

    except Exception as exc:
        test_gen_logger.exception(f'account details started {message.from_user.id}')
        try:
            _ = bot.send_message(user_id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['stop', 'submit'])
def test_stopper(message):
    try:
        test_gen_logger.info(f'test stopper started {message.from_user.id}')
        if message.text in ['/stop', '/submit']:
            user_id = message.from_user.id
            user = check_user(message)
            stop_test_stat = stop_test(user_id)
        else:
            user_id = message.from_user.id
            bot.send_message(user_id, 'Not a valid command')

    except Exception as exc:
        test_gen_logger.exception(f'test stopper {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['marked'])
def display_marked(message):
    try:
        test_gen_logger.info(f'display marked started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        if user.active_attempt_id is not None:
            attempt = user.attempt
            if user.active_poll is not None:
                _ = bot.stop_poll(user_id, user.active_poll.message_id)
                attempt.skipped_dict[attempt.current_qstn_no] = attempt.current_qstn_no
                user.active_poll = None
            qns_markup = create_marked_inline(attempt.marked_dict)
            if qns_markup != 1:
                msg = bot.send_message(user_id, 'Here are the marked questions', reply_markup=qns_markup)
                user.active_mark_skip_inlines.append(msg)
            else:
                bot.send_message(user_id, 'There is no marked question to display')
        else:
            next_msg = 'Send /start or /help to get started'
            bot.send_message(user_id, next_msg)

    except Exception as exc:
        test_gen_logger.exception(f'display marked {message.from_user.id}')
        try:
            _ = bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['skipped'])
def display_skipped(message):
    try:
        test_gen_logger.info(f'display skipped started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        if user.active_attempt_id is not None:
            attempt = user.attempt
            if user.active_poll is not None:
                _ = bot.stop_poll(user_id,user.active_poll.message_id)
                attempt.skipped_dict[attempt.current_qstn_no] = attempt.current_qstn_no
                user.active_poll = None
            qns_markup = create_skipped_inline(user_id, attempt.skipped_dict)
            if qns_markup != 1:
                msg = bot.send_message(user_id, 'Here are the skipped questions', reply_markup=qns_markup)
                user.active_mark_skip_inlines.append(msg)
            else:
                bot.send_message(user_id, 'There is no skipped question to display')
        else:
            next_msg = 'Send /start or /help to get started'
            bot.send_message(user_id, next_msg)

    except Exception as exc:
        test_gen_logger.exception(f'display skipped {message.from_user.id}')
        try:
            _ = bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler(commands=['qno'])
def call_qstn(message):
    try:
        test_gen_logger.info(f'call qno started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        if user.active_attempt_id is not None:
            content = list(message.text.split(' '))
            if len(content) == 2 and content[-1].isnumeric():
                attempt = user.attempt
                if user.active_poll is not None:
                    _ = bot.stop_poll(user_id, user.active_poll.message_id)
                    attempt.skipped_dict[attempt.current_qstn_no] = attempt.current_qstn_no
                    user.active_poll = None
                set_qno(user_id, int(content[-1]))
            else:
                nxt_msg = "please follow the format '/qno (question number to jump to)'."
                _ = bot.send_message(user_id, nxt_msg)
                return

        else:
            next_msg = 'Send /start or /help to get started'
            bot.send_message(user_id, next_msg)

    except Exception as exc:
        test_gen_logger.exception(f'call qno {message.from_user.id}')
        try:
            _ = bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@bot.message_handler()
def any_text_catcher(message):
    try:
        test_gen_logger.info(f'any text catcher started {message.from_user.id}')
        user_id = message.from_user.id
        user = check_user(message)
        proceed_stat = check_markup_for_no_cmnd(message)
        if proceed_stat == 1:
            return
        elif proceed_stat == 0:
            msg = bot.send_message(user_id, "Click the 'I am Ready' Button to start the test "
                                            "or send start or any other commands")
            return

        if message.text == '/view':
            next_msg = "To attempt a test, send '/view_(test_id)' or send /start or /help to start"
            _ = bot.send_message(message.from_user.id, next_msg)
            return

        elif message.text == '/attempt':
            next_msg = "To attempt a test, send '/attempt_(test_id)' or send /start or /help to start"
            _ = bot.send_message(message.from_user.id, next_msg)
            return

        split_msg = message.text.split('_')
        if len(split_msg) > 1:
            if split_msg[0] == '/view':
                test_view_handler(message)
                return
            elif split_msg[0] == '/attempt':
                attempt_request_handler(message)
                return

        next_msg = 'Send /start or /help to start'
        _ = bot.send_message(message.from_user.id, next_msg)

    except Exception as exc:
        test_gen_logger.exception(f'any text catcher {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


'''test generation codes'''


def test_name_process(message):
    try:
        test_gen_logger.info(f'test name process started {message.from_user.id}, {message.content_type}')
        if message.content_type == 'text':
            text = message.text
            if iscommand(text):
                if isundo(text):
                    msg = bot.send_message(message.from_user.id, 'Type /start or /help to start')
                    return
                elif iscancel(text):
                    msg = bot.send_message(message.from_user.id, CANCEL_MSG)
                    # cancel the test
                    return
                elif isskip(text):
                    msg = bot.send_message(message.from_user.id, NO_SKIP_MSG)
                    bot.register_next_step_handler(msg, test_name_process)
                    return

                elif ishelp(text):
                    msg = bot.send_message(message.from_user.id, HELP_PAGE_URL)
                    bot.register_next_step_handler(msg, test_name_process)
                    return

                else:
                    msg = bot.send_message(message.from_user.id, VOID_COMMAND_MSG)
                    bot.register_next_step_handler(msg, test_name_process)
                    return

        # real part
        if message.content_type == 'text':
            if len(message.text) >= 200:
                msg = bot.send_message(message.from_user.id,'Text name cannot be longer than 200 '
                                                            'characters. Please try a shorter name')
                bot.register_next_step_handler(msg, test_name_process)
                return
            else:
                test_name = message.text
            user_id = message.from_user.id
            user = user_dict[user_id]
            next_msg = 'Good!. Now enter your test description if any or send /skip'
            test = Test(test_name, user_id)
            user.active_test = test
            msg = bot.send_message(message.from_user.id,next_msg)
            bot.register_next_step_handler(msg, test_desc_process)
        else:
            ask_again_msg = 'Please enter a valid test name ❕. It has to be an alphanumeric'
            msg = bot.send_message(message.from_user.id, ask_again_msg)
            bot.register_next_step_handler(msg, test_name_process)
    except Exception as exc:
        test_gen_logger.exception(f'test name process {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def test_desc_process(message):
    try:
        test_gen_logger.info(f'test desc process started {message.from_user.id}, {message.content_type}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        test = user.active_test
        # testing if command
        if message.content_type == 'text':
            text = message.text
            if iscommand(text):
                if isundo(text):
                    msg = bot.send_message(message.from_user.id, 'Enter your test or assignment name')
                    bot.register_next_step_handler(msg, test_name_process)
                    return
                elif iscancel(text):
                    msg = bot.send_message(message.from_user.id, CANCEL_MSG)
                    # cancel the test
                    return
                elif isskip(text):
                    # skip allowed
                    pass

                elif ishelp(text):
                    msg = bot.send_message(message.from_user.id, HELP_PAGE_URL)
                    bot.register_next_step_handler(msg, test_desc_process)
                    return

                else:
                    msg = bot.send_message(message.from_user.id, VOID_COMMAND_MSG)
                    bot.register_next_step_handler(msg, test_desc_process)
                    return


        if message.content_type == 'text':
            if message.text != '/skip':
                test_desc = message.text
                next_msg = 'Good!. Now upload your test image/logo 🎑 if any or send /skip'
                test.test_description = test_desc
                msg = bot.send_message(message.from_user.id, next_msg)
                bot.register_next_step_handler(msg, test_image_process)
            else:
                test.test_description = ' '
                next_msg = 'Good!. Now upload your test image/logo 🎑 if any or send /skip'
                msg = bot.send_message(message.from_user.id, next_msg)
                bot.register_next_step_handler(msg, test_image_process)
        else:
            ask_again_msg = 'Please enter a valid input'
            msg = bot.send_message(message.from_user.id, ask_again_msg)
            bot.register_next_step_handler(msg, test_desc_process)
    except Exception as exc:
        test_gen_logger.exception(f'test desc process {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def test_image_process(message):
    try:
        test_gen_logger.info(f'test image process started {message.from_user.id}, {message.content_type}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        test = user.active_test
        # testing if command
        if message.content_type == 'text':
            text = message.text
            if iscommand(text):
                if isundo(text):
                    msg = bot.send_message(message.from_user.id, 'Enter your test or assignment '
                                                                 'descreption here or enter /skip')
                    bot.register_next_step_handler(msg, test_desc_process)
                    return
                elif iscancel(text):
                    msg = bot.send_message(message.from_user.id, CANCEL_MSG)
                    # cancel the test
                    return
                elif isskip(text):
                    next_msg = "Good!. ⏱ Now enter your test time in minutes and let\'s start with questions." \
                               "Send /skip if you don't want to keep a time constrain."
                    test.test_image = None
                    msg = bot.send_message(message.from_user.id, next_msg)
                    bot.register_next_step_handler(msg, test_time_process)
                    return

                elif ishelp(text):
                    msg = bot.send_message(message.from_user.id, HELP_PAGE_URL)
                    bot.register_next_step_handler(msg, test_image_process)
                    return

                else:
                    msg = bot.send_message(message.from_user.id, VOID_COMMAND_MSG)
                    bot.register_next_step_handler(msg, test_image_process)
                    return



        if message.content_type=='photo':
            test_image = message.photo[0].file_id
            test.test_image = test_image
            test.test_image_descr = message.caption
            next_msg = "Good!. ⏱ Now enter your test time in minutes and let\'s start with questions." \
                       "Send /skip if you don't want to keep a time constrain."
            msg = bot.send_message(message.from_user.id, next_msg)
            bot.register_next_step_handler(msg, test_time_process)

        else:
            ask_again_msg = 'Please enter a valid input ❕'
            msg = bot.send_message(message.from_user.id, ask_again_msg)
            bot.register_next_step_handler(msg, test_image_process)

    except Exception as exc:
        test_gen_logger.exception(f'test image process {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def test_time_process(message):
    try:
        test_gen_logger.info(f'test time process started {message.from_user.id}, {message.content_type}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        test = user.active_test
        # testing if command
        if message.content_type == 'text':
            text = message.text
            if iscommand(text):
                if isundo(text):
                    msg = bot.send_message(message.from_user.id, 'Please send your test image or logo or enter /skip')
                    bot.register_next_step_handler(msg, test_image_process)
                    return
                elif iscancel(text):
                    msg = bot.send_message(message.from_user.id, CANCEL_MSG)
                    # cancel the test
                    return
                elif isskip(text):
                    next_msg = 'Good!. Now let\'s start with questions.' \
                               'Please send your question in the form of a poll.' \
                               ' You have an option to send an image 🎑 with a caption ' \
                               'to display before your question.'
                    msg = bot.send_message(message.from_user.id, next_msg, reply_markup=poll_markup)
                    bot.register_next_step_handler(msg, test_question_image_process)
                    return

                elif ishelp(text):
                    msg = bot.send_message(message.from_user.id, HELP_PAGE_URL)
                    bot.register_next_step_handler(msg, test_time_process)
                    return

                else:
                    msg = bot.send_message(message.from_user.id, VOID_COMMAND_MSG)
                    bot.register_next_step_handler(msg, test_time_process)
                    return


        if message.content_type == 'text':
            if message.text.isnumeric() and int(message.text) > 0:
                test_time = int(message.text)
                next_msg = 'Good!. Now let\'s start with questions.' \
                           'Please send your question in the form of a poll. ' \
                           'You have an option to send an image with a caption ' \
                           'to display before your question.'
                test.test_time = test_time
                msg = bot.send_message(message.from_user.id, next_msg, reply_markup=poll_markup)
                bot.register_next_step_handler(msg, test_question_image_process)
            else:
                ask_again_msg = 'Please enter a valid number ❕'
                msg = bot.send_message(message.from_user.id, ask_again_msg)
                bot.register_next_step_handler(msg, test_time_process)

        else:
            ask_again_msg = 'Please enter a valid number ❕'
            msg = bot.send_message(message.from_user.id, ask_again_msg)
            bot.register_next_step_handler(msg, test_time_process)
    except Exception as exc:
        test_gen_logger.exception(f'test time process {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def test_question_image_process(message):
    try:
        test_gen_logger.info(f'test question process started {message.from_user.id}, {message.content_type}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        test = user.active_test
        # testing if command
        if message.content_type == 'text':
            text = message.text
            if iscommand(text):
                if isundo(text):
                    if test.question_no == 0:
                        msg = bot.send_message(message.from_user.id, "Please enter the test time in minutes.",
                                               reply_markup=hideBoard)
                        bot.register_next_step_handler(msg, test_time_process)
                        return

                    else:
                        msg = bot.send_message(message.from_user.id, 'Last question has been completely erased, '
                                                                     'Including the image 🎑.if uploaded. Please '
                                                                     'send a poll or an image which has to be '
                                                                     'displayed before the question.', poll_markup)
                        test.question_list.pop()
                        test.question_no -= 1
                        bot.register_next_step_handler(msg, test_question_image_process)
                        return

                elif isdone(text):
                    if test.question_no == 0:
                        msg = bot.send_message(message.from_user.id, "Test cannot be saved with no questions. "
                                                                     "Use /cancel to cancel this test. Or please"
                                                                     " send an image 🎑 or a poll as per the previous "
                                                                     "instruction.")
                        bot.register_next_step_handler(msg, test_question_image_process)
                        return

                    else:
                        test.question_dict = {i+1:test.question_list[i] for i in range(0, len(test.question_list))}
                        '''saving the file using save_test.py'''
                        test_stored_path = f'./test_objs/{test.test_id}.pkl'
                        print(f'saving {test.test_id}')
                        '''
                        0- file_open_error
                        1-file saved successfully
                        else- saving error
                        '''
                        test_binary = save_test.test_to_binary(test)
                        if test_binary == 0:
                            print('Error in saving test')
                            next_msg = "Sorry! We could not save the file. Please try once more"
                            msg = bot.send_message(message.from_user.id, next_msg)
                            bot.register_next_step_handler(msg, test_question_image_process)
                        else:
                            next_msg = f'Test saved successfully. You\'ll recieve test url ' \
                                       f'and more details right away \n '
                            final_msg = f'{test.test_name}\n\n' \
                                        f'{test.test_description}\n\n' \
                                        f'{test.question_no} Questions\n' \
                                        f'Test time {check_test_time(test.test_time)}\n\n' \
                                        f't.me/Exam_edu_bot?start={test.test_id}'

                            db_save_status = store.add_test(test, test_binary)
                            print('saving test to db ', test.test_id == db_save_status)
                            db_admin_save = store.modify_admin_tests(user_id, test.test_id)
                            print('saving admin test', user_id == db_admin_save)
                            _ = bot.send_message(message.from_user.id, next_msg, reply_markup=hideBoard)
                            _ = bot.send_message(message.from_user.id, final_msg)
                            print('Test save success')

                        return

                elif iscancel(text):
                    msg = bot.send_message(message.from_user.id, CANCEL_MSG, reply_markup=hideBoard)
                    # cancel the test
                    return

                elif isskip(text):
                    msg = bot.send_message(message.from_user.id, NO_SKIP_MSG)
                    bot.register_next_step_handler(msg, test_question_image_process)
                    return

                elif ishelp(text):
                    msg = bot.send_message(message.from_user.id, HELP_PAGE_URL)
                    bot.register_next_step_handler(msg, test_question_image_process)
                    return

                else:
                    msg = bot.send_message(message.from_user.id, VOID_COMMAND_MSG)
                    bot.register_next_step_handler(msg, test_question_image_process)
                    return

        question = test.Question()
        if message.content_type == 'photo':
            next_msg = 'Good!. This image and caption will be displayed before the question.' \
                       ' Now please create a poll and send it to me.Please make sure to send the poll in quiz mode'
            question.q_image = message.photo[0].file_id
            question.q_image_decr = message.caption
            msg = bot.send_message(message.from_user.id, next_msg)
            bot.register_next_step_handler(msg, poll_process, question)
        elif message.content_type == 'text':
            next_msg = 'Good!. This message will be displayed before the question. ' \
                       'Now please create a poll and send it to me.Please make sure to send the poll in quiz mode'
            question.q_image_decr = message.text
            msg = bot.reply_to(message, next_msg)
            bot.register_next_step_handler(msg, poll_process, question)

        elif message.content_type == 'poll':
            if message.poll.type == 'quiz':
                next_msg = 'Good! Your question is created. To add new question, ' \
                           'send an image with a caption or a poll. Enter /done if you are done adding questions.'
                poll_is_here(question, message)
                test.question_no += 1
                test.question_list.append(question)
                msg = bot.send_message(message.from_user.id, next_msg, reply_markup=poll_markup)
                bot.register_next_step_handler(msg, test_question_image_process)

            else:
                quiz_needed_msg='We are not supporting Multiple answer polls now. Please send a quiz type poll.'
                msg = bot.send_message(message.from_user.id, quiz_needed_msg)
                bot.register_next_step_handler(msg, poll_process, test, question)

        else:
            ask_again_msg = 'Please send a valid input'
            msg = bot.send_message(message.from_user.id, ask_again_msg)
            bot.register_next_step_handler(msg, test_question_image_process)

    except Exception as exc:
        test_gen_logger.exception(f'test question process {message.from_user.id}')
        print(exc)
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def poll_process(message, question):
    try:
        test_gen_logger.info(f'poll process started {message.from_user.id}, {message.content_type}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        test = user.active_test
        # testing if command
        if message.content_type == 'text':
            text = message.text
            if iscommand(text):
                if isundo(text):
                    msg = bot.send_message(message.from_user.id, 'Please send your question as a quiz type poll or send an image '
                                                                 'with or without caption to display before this question',reply_markup=poll_markup)
                    bot.register_next_step_handler(msg, test_question_image_process)
                    return
                elif iscancel(text):
                    msg = bot.send_message(message.from_user.id, CANCEL_MSG, reply_markup=hideBoard)
                    # cancel the test
                    return
                elif isdone(text):
                    msg = bot.send_message(message.from_user.id, 'You cannot end the test creation in the middle of a question.'
                                                                'Please send a quiz type poll and then enter done or use /undo followed by '
                                                                '/done')
                    bot.register_next_step_handler(msg, poll_process, question)
                    return

                elif isskip(text):
                    msg = bot.send_message(message.from_user.id, NO_SKIP_MSG)
                    bot.register_next_step_handler(msg, poll_process, question)
                    return

                elif ishelp(text):
                    msg = bot.send_message(message.from_user.id, HELP_PAGE_URL)
                    bot.register_next_step_handler(msg, poll_process, question)
                    return

                else:
                    msg = bot.send_message(message.from_user.id, VOID_COMMAND_MSG)
                    bot.register_next_step_handler(msg, poll_process, question)
                    return


        if message.content_type=='poll':
            if message.poll.type == 'quiz':
                next_msg = 'Good! Your question is created. To add new question, send an image with a caption ' \
                           'or a poll. Enter /done if you are done adding questions.'
                poll_is_here(question, message)
                test.question_no += 1
                test.question_list.append(question)
                msg = bot.send_message(message.from_user.id, next_msg, reply_markup=poll_markup)
                bot.register_next_step_handler(msg, test_question_image_process)

            else:
                quiz_needed_msg = 'We are not supporting Multiple answer polls now. Please send a quiz type poll.'
                msg = bot.send_message(message.from_user.id, quiz_needed_msg)
                bot.register_next_step_handler(msg, poll_process, question)
        else:
            need_quiz_poll_msg = 'Please send a poll in quiz mode'
            msg = bot.send_message(message.from_user.id, need_quiz_poll_msg)
            bot.register_next_step_handler(msg, poll_process, question)

    except Exception as exc:
        test_gen_logger.exception(f'poll process {message.from_user.id}')
        try:
            bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


'''test generation and saving it as pickle ends here'''



'''test sending code or test attempting code'''


def check_test_time(test_time):
    try:
        if test_time is None:
            return 'No time limit'
        else:
            test_time = str(test_time) + ' Minutes'
            return test_time
    except:
        test_gen_logger.exception('check test time error')


def send_test_details(user_id, loaded_test):
    try:
        test_gen_logger.info(f'send_test_details started {user_id}')
        user = user_dict[user_id]
        attempt_msg = f"Welcome.\n{loaded_test.test_name}\n{loaded_test.test_description}\n{loaded_test.test_batch}" \
                      f"\n{loaded_test.test_topic}\nTest time = {check_test_time(loaded_test.test_time)}. \n \n" \
                      f"- Send /stop at anytime to stop the test\n. - Send /marked to see all the " \
                      f"marked questions.\n- Send /skipped to see all the questions you have skipped " \
                      f"without answering.\n- Use /qno (required question number here without bracket) eg: /qno 5 " \
                      f"(to jump to question number 5) to jump to a specific question number.\n\n" \
                      f"- Use /help command if you are a first time visitor of this bot or if you get stuck " \
                      f"or confused.\n\n" \
                      f"Once you click 'I AM READY', this will be recorded as an attempt"

        if loaded_test.test_image is not None:
            _ = bot.send_photo(user_id, loaded_test.test_image, caption=loaded_test.test_image_descr)
        _ = bot.send_message(user_id, attempt_msg)
        msg = bot.send_message(user_id, 'Are you ready?', reply_markup=ready_markup)
        user.active_markup_msg = msg
    except Exception as exc:
        test_gen_logger.exception(f'send test details {user_id}')
        try:
            bot.send_message(user_id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def create_attempt(call):
    try:
        test_gen_logger.info(f'create_attempt started {call.from_user.id}')
        user_id = call.from_user.id
        user = user_dict[user_id]
        loaded_test = user.active_test
        attempt = Test_atmpt(loaded_test.test_id, user_id, loaded_test.question_dict)
        attempt.start_time = dt.datetime.now()
        if loaded_test.test_time is not None:
            attempt.end_time = attempt.start_time + timedelta(minutes=loaded_test.test_time)
            user_attempt_dict[user_id] = attempt.end_time
        user.active_attempt_id = attempt.attempt_id
        user.attempt = attempt
        return 0
    except Exception as exc:
        test_gen_logger.exception(f'create attempt {call.from_user.id}')
        try:
            bot.send_message(call.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def count_down(call):
    try:
        test_gen_logger.info(f'count down started {call.from_user.id}')
        user_id = call.from_user.id
        user = user_dict[user_id]
        loaded_test = user.active_test
        msg = bot.send_message(user_id, 'Ready...')
        count_down_list = ['3️⃣....', '2️⃣ Get', '1️⃣ Set', '✅ Gooo.....']
        for text in count_down_list:
            msg = bot.edit_message_text(text, chat_id=user_id, message_id=msg.message_id)
            time.sleep(1)
        user.active_markup_msg = None
        next_msg = 'Great! Before we start, please enter your Name or Rollnumber.\n\n' \
                   'PS: There are no undo or skip options available after this step. ' \
                   'So please make sure you are typing the correct info.'
        ask_msg = bot.send_message(user_id, next_msg)
        bot.register_next_step_handler(ask_msg, process_username)
        return
    except Exception as exc:
        test_gen_logger.exception(f'Count down {call.from_user.id}')
        try:
            bot.send_message(call.from_user.id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def process_username(message):
    try:
        test_gen_logger.info(f'process username {message.from_user.id}, {message.content_type}')
        user_id = message.from_user.id
        user = user_dict[user_id]
        attempt = user.attempt
        if message.content_type == 'text':
            if message.text == '/stop':
                stop_test(user_id)
                print("Stopping test")
                return
            attempt.username = message.text[:99]
            print(attempt.username)
            _ = bot.send_message(user_id, 'Good. Here is the first question.')
            send_question(user_id)
        else:
            msg = bot.send_message(user_id, 'Please enter a valid input ❕')
            bot.register_next_step_handler(msg, process_username)
    except:
        test_gen_logger.exception('process_username')
        try:
            _ = bot.send_message(message.from_user.id, ERROR_MESSAGE)
        except:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def set_qno(user_id, qno):
    # qno has to be an int
    try:
        test_gen_logger.info(f'set question started {user_id}')
        user = user_dict[user_id]
        loaded_test = user.active_test
        if 0 < qno <= loaded_test.question_no:
            attempt = user.attempt
            if attempt.response.get(attempt.current_qstn_no, None) is None:
                attempt.skipped_dict[attempt.current_qstn_no] = attempt.current_qstn_no
                bot.edit_message_text('🔘 You have not selected any answer for this question', chat_id=user_id,
                                      message_id=user.active_poll_markup.message_id)
            else:
                bot.edit_message_text(f'📝 You have selected the answer {attempt.response.get(attempt.current_qstn_no, None)}'
                                      f' for this question', chat_id=user_id, message_id=user.active_poll_markup.message_id)
            if user.active_poll is not None:
                bot.stop_poll(user_id, user.active_poll.message_id)
            '''
            if user.active_poll_markup is not None:
                bot.delete_message(user_id, user.active_poll_markup.message_id)
            '''
            user.active_poll_markup = None
            attempt.current_qstn_no = qno
            send_question(user_id)
            return qno
        else:
            next_msg= f'Requested question is out of range. The number of questions in this test' \
                      f' is {loaded_test.question_no}'
            _ = bot.send_message(user_id, next_msg)

    except Exception as exc:
        test_gen_logger.exception(f'set qno {user_id}')
        try:
            bot.send_message(user_id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def is_q_marked(marked_dict, qno):
    if qno in marked_dict.values():
        return True
    else:
        return False


def send_question(user_id):
    try:
        test_gen_logger.info(f'send_question started {user_id}')
        user = user_dict[user_id]
        loaded_test = user.active_test
        attempt = user.attempt
        if loaded_test.test_time is not None:
            remaining_time = attempt.end_time - dt.datetime.now()
            test_gen_logger.debug(f'remaining_time {remaining_time}')
        if attempt.current_qstn_no <= loaded_test.question_no:
            qstn = attempt.qstn_dict[attempt.current_qstn_no]
            if qstn.q_image is not None:
                _ = bot.send_photo(user_id,qstn.q_image, caption=qstn.q_image_decr)
            elif qstn.q_image_decr is not None:
                _ = bot.send_message(user_id,qstn.q_image_decr)
            poll_question = f'[{attempt.current_qstn_no}/{loaded_test.question_no}] {qstn.poll_question}'
            poll_options = qstn.poll_options
            poll = bot.send_poll(user_id, poll_question, poll_options, type='regular', open_period= None)
            test_gen_logger.debug(f'send poll {poll.poll.id}')
            user.active_poll = poll
            poll_user_dict[poll.poll.id] = user_id
            if attempt.response.get(attempt.current_qstn_no, None) is not None:
                text = f"Your previous answer to this question was {attempt.response[attempt.current_qstn_no]}"
                _ = bot.send_message(user_id, text)
            next_text = 'Use the below buttons to mark the question or Navigate to next or Previous qstn'
            marked_dict = attempt.marked_dict
            current_qno = attempt.current_qstn_no
            if loaded_test.question_no != 1:
                if current_qno == 1:
                    if is_q_marked(marked_dict, current_qno):
                        poll_markup_msg = bot.send_message(user_id, next_text, reply_markup=initial_marked_markup)
                    else:
                        poll_markup_msg = bot.send_message(user_id, next_text, reply_markup=initial_mark_markup)
                elif attempt.current_qstn_no == loaded_test.question_no:
                    if is_q_marked(marked_dict, current_qno):
                        poll_markup_msg = bot.send_message(user_id, next_text, reply_markup=final_marked_markup)
                    else:
                        poll_markup_msg = bot.send_message(user_id, next_text, reply_markup=final_mark_markup)
                    _ = bot.send_message(user_id, "Send /stop to finish the test.\n-Send /marked to see all the "
                                                  "marked questions.\n-Send /skipped to see all the skipped questions."
                                                  "\n-Send /qno 'question number' to see a particular question. "
                                                  "eg: /qno 5")
                else:
                    if is_q_marked(marked_dict, current_qno):
                        poll_markup_msg = bot.send_message(user_id, next_text, reply_markup=marked_markup)
                    else:
                        poll_markup_msg = bot.send_message(user_id, next_text, reply_markup=mark_markup)
                user.active_poll_markup = poll_markup_msg

    except Exception as exc:
        test_gen_logger.exception(f'send_question {user_id}')
        try:
            bot.send_message(user_id, 'The test exists in our database, but it looks like owner might have cleared'
                                      'or deleted the chat history with the bot.')
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


def create_test_message(tests, initial_msg, command_line):
    try:
        test_gen_logger.info('create test message started')
        test_number = 1
        msg = initial_msg
        if len(tests) >= 1:
            test_gen_logger.debug('tests available')
            for test_id in tests:
                test = store.get_test(test_id)
                if test != 0:
                    test_gen_logger.debug('test exists in db')
                    test_name = test[2]
                    msg += str(test_number) + '. ' + test_name + '\n' + command_line + test_id + '\n'
                    test_number += 1
            return msg
        else:
            return 'No test to display'

    except Exception as exc:
        test_gen_logger.exception('create test message')


def str_check(text):
    if text is None:
        return 'NA'
    elif type(text) is str:
        return text
    elif str(text):
        return str(text)
    else:
        return 'NA'


@bot.callback_query_handler(func=lambda call: True)
def call_back_check(call):
    try:
        test_gen_logger.info(f'call_back_check started {call.from_user.id}')
        user_id = call.from_user.id
        user = user_dict[user_id]
        loaded_test = user.active_test
        callback = call.data
        test_gen_logger.debug(f'callback data = {callback}')
        if callback == ready_button_call:
            create_attempt(call)
            bot.delete_message(user_id, user.active_markup_msg.message_id)
            user.active_markup_msg = None
            count_down(call)
            #send_question(user_id)

        elif callback == mark_button_call:
            # nothing happens to poll. only editreplymarkup
            attempt = user.attempt
            attempt.marked_dict[attempt.current_qstn_no] = attempt.current_qstn_no
            if attempt.current_qstn_no == 1:
                poll_markup_msg = bot.edit_message_reply_markup(chat_id=user_id, message_id=user.active_poll_markup.message_id,
                                                                reply_markup=initial_marked_markup)
            elif attempt.current_qstn_no == loaded_test.question_no:
                poll_markup_msg = bot.edit_message_reply_markup(chat_id=user_id, message_id=user.active_poll_markup.message_id,
                                                                reply_markup=final_marked_markup)
            else:
                poll_markup_msg = bot.edit_message_reply_markup(chat_id=user_id, message_id=user.active_poll_markup.message_id,
                                                                reply_markup=marked_markup)
            user.active_poll_markup = poll_markup_msg

        elif callback == marked_button_call:
            # nothing happens to poll. only editreplymarkup
            attempt = user.attempt
            del attempt.marked_dict[attempt.current_qstn_no]
            if attempt.current_qstn_no == 1:
                poll_markup_msg = bot.edit_message_reply_markup(chat_id=user_id, message_id= user.active_poll_markup.message_id,
                                                                reply_markup=initial_mark_markup)
            elif attempt.current_qstn_no == loaded_test.question_no:
                poll_markup_msg = bot.edit_message_reply_markup(chat_id=user_id, message_id= user.active_poll_markup.message_id,
                                                                reply_markup=final_mark_markup)
            else:
                poll_markup_msg = bot.edit_message_reply_markup(chat_id=user_id, message_id= user.active_poll_markup.message_id,
                                                                reply_markup=mark_markup)
            user.active_poll_markup = poll_markup_msg

        elif callback == next_button_call:
            # poll stops. Reply_markup msg getting deleted. active poll pop, active poll markup pop
            attempt = user.attempt
            if attempt.response.get(attempt.current_qstn_no, None) is None:
                attempt.skipped_dict[attempt.current_qstn_no] = attempt.current_qstn_no
                bot.edit_message_text('🔘 You have not selected any answer for this question', chat_id=user_id,
                                      message_id=user.active_poll_markup.message_id)
            else:
                bot.edit_message_text(f'📝 You have selected the answer {attempt.response.get(attempt.current_qstn_no, None)}'
                                      f' for this question', chat_id=user_id, message_id=user.active_poll_markup.message_id)
            if user.active_poll is not None:
                bot.stop_poll(user_id, user.active_poll.message_id)
                user.active_poll = None
            # bot.delete_message(user_id, user.active_poll_markup.message_id)
            user.active_poll_markup = None
            attempt.current_qstn_no += 1
            send_question(user_id)

        elif callback == prev_button_call:
            # poll stops. Reply_markup msg getting deleted. active poll pop, active poll markup pop
            attempt = user.attempt
            if attempt.response.get(attempt.current_qstn_no, None) is None:
                attempt.skipped_dict[attempt.current_qstn_no] = attempt.current_qstn_no
                bot.edit_message_text('🔘 You have not selected any answer for this question', chat_id=user_id,
                                      message_id=user.active_poll_markup.message_id)
            else:
                bot.edit_message_text(f'📝 You have selected the answer {attempt.response.get(attempt.current_qstn_no, None)}'
                                      f' for this question', chat_id=user_id, message_id=user.active_poll_markup.message_id)

                # print('prev', attempt.skipped_dict)
            if user.active_poll is not None:
                bot.stop_poll(user_id, user.active_poll.message_id)
            # bot.delete_message(user_id, user.active_poll_markup.message_id)
            user.active_poll_markup = None
            attempt.current_qstn_no -= 1
            send_question(user_id)

        elif callback.isnumeric():
            set_qno(user_id, int(callback))

        elif callback == admin_tests_call:
            if user.active_account_markup is not None:
                bot.delete_message(user_id, user.active_account_markup.message_id)
                user.active_account_markup = None
            # and call db to get all the admin test etc.
            admin_tests = store.get_admin_tests(user_id)
            initial_msg = 'The tests you created are given below. Use /view command given under each' \
                          'test to see all the attempts of this test till now\n\n'
            admin_msg = create_test_message(admin_tests, initial_msg, '/view_')
            msg = bot.send_message(user_id, admin_msg)

        elif callback == attended_test_call:
            if user.active_account_markup is not None:
                bot.delete_message(user_id, user.active_account_markup.message_id)
                user.active_account_markup = None
            # and call db to get all the attended test etc.
            attended_tests = store.get_attended_tests(user_id)
            initial_msg = 'The tests you attempted are given below. Use /view command given under each' \
                          'test to see more details\n\n'
            attended_msg = create_test_message(attended_tests, initial_msg, '/attempt_')
            msg = bot.send_message(user_id, attended_msg)

        elif callback.startswith(admin_call):
            if user.active_admin_markup is not None:
                bot.delete_message(user_id, user.active_admin_markup.message_id)
                user.active_admin_markup = None
            split_call = callback.split(' ')
            req_test_id = ' '.join(split_call[1:])
            # and get all the attempts of the test from db and send it as a message
            test_name = store.get_test_name(req_test_id)
            print('test name: ', test_name)
            if test_name == 0:
                _ = bot.send_message(user_id, 'Could not find the test in the Database')
                print('Could not find the test name')
                return

            test_attempts = store.get_attempt_test(req_test_id)
            if test_attempts == 0 or len(test_attempts) == 0 or test_attempts is None:
                _ = bot.send_message(user_id, 'Could not find any attempt record.')
                print('no test found admin call callback')
                return

            to_be_send = f'Details of all the attempts for the test  {test_name} is given below. \n\n'
            attempt_no = 1
            for req_attempt in test_attempts:
                to_be_send = to_be_send + (str_check(attempt_no) + '. ' + 'Username- ' + str_check(req_attempt[0]) + '\n' +
                                           'Start time- ' + str_check(req_attempt[1]) + '\n' +
                                           'Time taken- ' + str_check(req_attempt[2]) + ' ' + 'Mins' + '\n' +
                                           'Correct answers- ' + str_check(req_attempt[3]) + '\n' + 'Wrong answers- ' +
                                           str_check(req_attempt[4]) + '\n' + 'Total mark- ' + str_check(req_attempt[5]) + '\n')
                attempt_no += 1
            print('total_attempts', attempt_no)
            _ = bot.send_message(user_id, to_be_send)

    except Exception as exc:
        test_gen_logger.exception('call back check')


@bot.poll_handler(func=lambda poll: True)
def get_ans(poll):
    try:
        test_gen_logger.info('get ans (poll) started')
        user_id = poll_user_dict[poll.id]
        del poll_user_dict[poll.id]
        user = user_dict[user_id]
        user.active_poll = None
        attempt = user.attempt
        qstn = attempt.qstn_dict[attempt.current_qstn_no]
        poll_ans_id = qstn.correct_id
        for option in poll.options:
            if option.voter_count == 1:
                attempt.response[attempt.current_qstn_no] = option.text
                # print('attempt recorded', option.text)
                if attempt.skipped_dict.get(attempt.current_qstn_no, None) is not None:
                    del attempt.skipped_dict[attempt.current_qstn_no]

        if all(option.voter_count == 0 for option in poll.options) and \
                attempt.response.get(attempt.current_qstn_no) is None:
            attempt.skipped_dict[attempt.current_qstn_no] = attempt.current_qstn_no

    except Exception as exc:
        test_gen_logger.exception('get ans(poll)')
        try:
            bot.send_message(user_id, ERROR_MESSAGE)
        except Exception as oops:
            test_gen_logger.exception(CANNOT_SEND_LOG_MSG)


@server.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://teleexambot.herokuapp.com/' + BOT_TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
