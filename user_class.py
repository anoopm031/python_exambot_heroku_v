import random_string_gen


class User:
    def __init__(self, chat_id, username=None):
        self.user_id = chat_id
        self.username = username
        self.attempt = None
        self.active_test = None
        self.active_attempt_id = None
        self.active_markup_msg = None
        self.active_account_markup = None
        self.active_admin_markup = None
        self.active_poll = None
        self.active_poll_markup = None
        self.active_mark_skip_inlines = []
        self.user_admin_test = []
        self.user_attended_test = []


class Test_atmpt:
    def __init__(self, test_id, user_id, qstns_dict):
        self.attempt_id = random_string_gen.new_uuid()
        self.test_id = test_id
        self.user_id = user_id
        self.username = None
        self.qstn_dict = qstns_dict
        self.marked_dict = {}          # qno:qno
        self.skipped_dict = {}        # qno:qno
        self.response = {}
        self.current_qstn_no = 1
        self.attempt_dtime = None
        self.start_time = None
        self.end_time = None
        self.correct_ans = 0
        self.wrong_ans = 0
        self.mark = 0
        self.time_taken = None