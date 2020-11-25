import random_string_gen


class Test:
    def __init__(self, test_name, user_id):
        self.test_id = random_string_gen.new_uuid()
        self.test_name = test_name
        self.test_admin = user_id
        self.test_type = None
        self.test_time = None
        self.test_description = ' '
        self.test_batch = ' '
        self.test_topic = ' '
        self.test_image = None
        self.test_image_descr = ' '
        self.question_list = []      # [(q_no,question_object)] not using dict for poping last entry easily
                                     # for undo operations
        self.question_dict = {}
        self.question_no = 0
        self.total_qstns = 1
        self.max_marks = 0
        self.correct_marks = 1
        self.incorrect_marks = 0
        self.answer_key_link = None
        self.test_url = None
        self.file_name = None
        self.file_path = None
        self.max_allowed_atmpt = None
        self.created_date = None
        self.scheduled_date = None
        self.scheduled_time = None
        self.allowed_time = None
        self.end_date = None
        self.active = True

    class Question:
        def __init__(self):
            self.q_id = random_string_gen.new_uuid()
            self.q_image = None
            self.q_image_decr = None
            self.q_type = None     # can be multiple choice or single choice. MCQ not supported at the moment
            self.poll_question = None
            self.poll_options = []
            self.correct_id = None
            # self.poll_answers=None
            self.correct_ans = None
            self.write_state = True
            self.showed = False
            self.skipped = False
            self.is_ans_correct = None  # True-correct_ans, False-Wrong_ans, None- Didn't attempt
                                        # will be used while user attempting the exam and always
                                        # None in the pickled test




