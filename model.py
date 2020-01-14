import random
import feedparser
import dict_questions
from pymongo.mongo_client import MongoClient
from datetime import datetime

client = MongoClient()
db = client.get_database("Teachild")
db.drop_collection('Parent')
db.drop_collection('Child')
db.drop_collection('Task')
parent_collection = db.get_collection('Parent')
child_collection = db.get_collection('Child')
task_collection = db.get_collection('Task')

'''
#0-39
dict_questions.dict_questions_math_level1
#0-29
dict_questions.dict_questions_math_level2
'''
NUMBER_Q_IN_TASK = 2


def make_task_for_level(dictt: dict) -> dict:
    l = []
    for i in range(1, NUMBER_Q_IN_TASK + 1):
        l.append(str(i))

    return dict(zip(l, random.choices(dictt, k=NUMBER_Q_IN_TASK)))


def send_task(level) -> dict:
    if int(level) == 0:
        return make_task_for_level(dict_questions.dict_questions_math_level1)
    if int(level) == 1:
        return make_task_for_level(dict_questions.dict_questions_math_level2)


def check_answer(name_img_q: str, answer) -> bool:
    return int(name_img_q.split('=')[1].split('.')[0]) == int(answer)


def add_parent_to_db(update, chat_id):
    p = {
        'parent_id': chat_id,
        'name': update.message.from_user['first_name'],
        'children_ids': [],  # a list of children id's
        'children_names': []
    }

    response = parent_collection.replace_one({'parent_id': chat_id}, p, upsert=True)


def add_child_to_db(name, p_id, chat_id):
    c = {
        'child_id': chat_id,
        'name': name,
        'parent_id': p_id,
        'tasks': [],  # a list of dictionaries
        'current_task': 0
    }
    response = child_collection.replace_one({'child_id': chat_id}, c, upsert=True)


def add_task_to_db(c_id, p_id, level, dictionary):
    t = {
        'child_id': int(c_id),
        'parent_id': p_id,
        'level': int(level),
        'status': False,
        'date': datetime.now(),
        'question_dict': dictionary,
        'start': False,
        'current_question': 1
    }
    # response = task_collection.insert_one(t)
    add_task_to_child(int(c_id), t)


def get_date_task_send(task_id):
    task = db.collection.find({'_id': task_id})
    d = feedparser.parse(task['date'])
    return d.strftime("%d/%m/%Y %H:%M:%S")


def child_name_to_parent(chat_id, child_name):
    parent_collection.update({'parent_id': chat_id}, {'$push': {'children_names': child_name}})


def child_id_to_parent(parent_id, child_id):
    parent_collection.update({'parent_id': int(parent_id)}, {'$push': {'children_ids': child_id}})


def add_task_to_child(chat_id, task):
    child_collection.update({'child_id': chat_id}, {'$push': {'tasks': task}})


def get_list_child_id(chat_id_parent):
    return parent_collection.find({'parent_id': chat_id_parent})[0]['children_ids']


def get_list_child_name(chat_id_parent):
    return parent_collection.find({'parent_id': chat_id_parent})[0]['children_names']


def is_parent(chat_id):
    return True if parent_collection.find({'parent_id': chat_id}).count() > 0 else False


def get_current_task(child_id):
    return child_collection.find({'child_id': child_id})[0]['current_task']


def get_task_level(child_id):
    current_task = get_current_task(child_id)
    return child_collection.find({'child_id': child_id})[0]['tasks'][current_task]['level']


def get_question(child_id, num_ques):
    current_task = get_current_task(child_id)
    return child_collection.find({'child_id': child_id})[0]['tasks'][current_task]['question_dict'][
        str(num_ques)]  # list with pic and status


def get_current_ques(child_id):
    return child_collection.find({'child_id': child_id})[0]['tasks'][get_current_task(child_id)]['current_question']


def create_task_in_db(parent_id, child_id, level):
    dictionary = send_task(level)
    add_task_to_db(child_id, parent_id, level, dictionary)


def set_task_start_to_true(child_id):
    current_task = get_current_task(child_id)
    temp = list(child_collection.find({'child_id': child_id}))[0]
    temp['tasks'][current_task]['start'] = True
    child_collection.replace_one({'child_id': child_id}, temp, upsert=True)


def set_current_question(chat_id, num):
    temp = list(child_collection.find({'child_id': chat_id}))[0]
    temp['tasks'][get_current_task(chat_id)]['current_question'] = num
    child_collection.replace_one({'child_id': chat_id}, temp, upsert=True)


def set_task_status_true(chat_id):
    temp = list(child_collection.find({'child_id': chat_id}))[0]
    temp['tasks'][get_current_task(chat_id)]['status'] = True
    child_collection.replace_one({'child_id': chat_id}, temp, upsert=True)


def ready_tasks(chat_id):
    return len(
        child_collection.find({'child_id': chat_id})[0]['tasks'])  # add check: if all status are true(no tasks undone)


def set_ques_status_to_true(chat_id, current_ques):
    temp = list(child_collection.find({'child_id': chat_id}))[0]
    temp['tasks'][get_current_task(chat_id)]['question_dict'][str(current_ques)][1] = True
    child_collection.replace_one({'child_id': chat_id}, temp, upsert=True)


def get_num_of_level():
    return int(2)


def name_task(name_image):
    return ' '.join(name_image.split(' ')[2:7])


def get_report(chat_id, context, child_id):
    child = child_collection.find({'child_id': int(child_id)})[0]
    data_now = datetime.now()
    data_now_str = data_now.strftime("%d/%m/%Y %H:%M:%S")
    name_file = r'DB\reports\\' + f"{child['name']} {child['child_id']}.txt"
    with open(name_file, 'w') as report_file:
        report_file.write(f"{child['name']} report {data_now_str}\n")
        report_file.write('------------------------------------------------------------------------\n')
        for task in child['tasks']:
            report_file.write(
                f'date - {task["date"].strftime("%d/%m/%Y %H:%M:%S")}, level - {task["level"]}, subject - math:\n')
            if task["status"]:
                report_file.write("Completed your task\n")
                for key, value in task["question_dict"].items():
                    answer_status = name_task((value[0]))
                    if value[1]:
                        answer_status += '  answer correctly\n'
                    else:
                        answer_status += '  answer wrongly\n'
                    report_file.write(answer_status)
            else:
                if task["start"]:
                    report_file.write("Didn't finish task\n")
                else:
                    report_file.write("Didn't start task\n")
            report_file.write('------------------------------------------------------------------------\n')
    context.bot.send_document(chat_id=chat_id, document=open(name_file, 'rb'))
