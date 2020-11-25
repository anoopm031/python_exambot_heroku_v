import dill
import logging
import os
from sys import stdout
from store import get_test_binary, get_state_binary, add_state_binary

save_test_logger = logging.getLogger(__name__)
save_test_logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')
file_handler = logging.FileHandler('./logs/save_test.log')
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(stdout)
console_handler.setFormatter(formatter)
save_test_logger.addHandler(console_handler)
save_test_logger.addHandler(file_handler)


def saving_test(test_path, test_obj):
    try:
        dir_path_iter = test_path.split('/')
        dir_path = '/'.join(dir_path_iter[:-1])
        print('dir path')
        if os.path.isdir(dir_path):
            print('test objs dir already exists')
        else:
            print('creating test_objs')
            try:
                os.mkdir(dir_path)
                print('folder created successfully')
            except FileExistsError as exc:
                print(exc)

        save_test_logger.info('Saving test...')
        try:
            save_test_logger.info('opening file')
            test_file = open(test_path, 'wb')
        except Exception as exc:
            save_test_logger.exception('Error opening file')
            return 0

        dill.dump(test_obj, test_file)
        save_test_logger.debug(f'file saved in {test_path}')
        test_file.close()
        return 1
    except Exception as exc:
        save_test_logger.exception('test save error')
        test_file.close()
        return exc


def load_test(req_test_id):
    try:
        save_test_logger.info('loading test...')
        try:
            save_test_logger.info('Opening file')
            test_file_path=f'./test_objs/{req_test_id}.pkl'
            test_file=open(test_file_path,'rb')
        except Exception as exc:
            save_test_logger.exception('loading test file opening error')
            return 0

        loaded_test = dill.load(test_file)
        test_file.close()
        return loaded_test
    except Exception as exc:
        print(exc)
        save_test_logger.exception('load test error')
        test_file.close()
        return 1


def test_to_binary(test_obj):
    test_id = test_obj.test_id
    try:
        dumped_test = dill.dumps(test_obj)
        print('Dumping successfull', dumped_test)
        return dumped_test
    except Exception as exc:
        print("Dumping Error", exc)
        return 0


def load_test_db(test_id):
    try:
        test_binary = get_test_binary(test_id)
        if test_binary == 0:
            print('Could not get test from db')
            return 0
        else:
            test = dill.loads(test_binary)
            print('test retrieved', test.test_id, test.test_name, test.question_dict)
            return test
    except Exception as exc:
        print('Error in save file load test db', exc)


def dump_user_dict(user_dict, user_attempt_dict, handler_dict):
    try:
        save_test_logger.info('opening file')
        user_dict_bin = dill.dumps(user_dict)
        user_attempt_bin = dill.dumps(user_attempt_dict)
        handler_bin = dill.dumps(handler_dict)
        state_save = add_state_binary(user_dict_bin, user_attempt_bin, handler_bin)
        if state_save == 0:
            print('add state binary did not succeed')
            return 0
        elif state_save == 1:
            print('add state binary success')
            return 1
    except Exception as exc:
        save_test_logger.exception('Error in dump_user_dict')
        print('Error in dumping user_dict', exc)
        return 0


def load_back_user_dict():
    try:
        save_test_logger.info('load back user dict')
        get_state_bins = get_state_binary()
        print('got load back user dict', get_state_bins)
        if get_state_bins != 0:
            if get_state_bins[0] is None:
                user_dict = {}
            else:
                user_dict = dill.loads(get_state_bins[0])

            if get_state_bins[1] is None:
                user_attempt = {}
            else:
                user_attempt = dill.loads(get_state_bins[1])
            if get_state_bins[2] is None:
                handler = {}
            else:
                handler = dill.loads(get_state_bins[2])
        else:
            user_dict = {}
            user_attempt = {}
            handler = {}

        return user_dict, user_attempt, handler
    except Exception as exc:
        save_test_logger.exception('Error in loading user_dict')
        print('Error in loading user_dict', exc)
        return 0


