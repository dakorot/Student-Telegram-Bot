import threading
import time
import telebot
import sqlite3
import schedule

TOKEN = ""

bot = telebot.TeleBot(TOKEN)

lections_schedule = {
    'Monday': [
        {'name': 'Mathematics', 'time': '8:30'},
        {'name': 'Physics', 'time': '10:15'}
    ],
    'Tuesday': [
        {'name': 'Mathematics', 'time': '8:30'},
        {'name': 'Physics', 'time': '12:00'}
    ],
    'Wednesday': [
        {'name': 'Programming', 'time': '10:15'},
        {'name': 'Physics', 'time': '12:00'}
    ],
    'Thursday': [
        {'name': 'Programming', 'time': '12:00'},
        {'name': 'Programming', 'time': '15:30'}
    ],
    'Friday': [
        {'name': 'Physics', 'time': '8:30'},
        {'name': 'Mathematics', 'time': '10:15'}
    ],
}

homework = {
        'Mathematics': {
            'tasks': '', 'deadline': ''
        },
        'Physics': {
            'tasks': '', 'deadline': ''
        },
        'Programming': {
            'tasks': '', 'deadline': ''
        }
    }

exams = {
    'Mathematics': {
        'date': '', 'time': 'to be updated', 'type': 'exam'
    },
    'Physics': {
        'date': '', 'time': 'to be updated', 'type': 'exam'
    },
    'Programming': {
        'date': '', 'time': 'to be updated', 'type': "student's record"
    }
}

subject = None
average_grade = []


@bot.message_handler(commands=['start'])
def start_chat(message):
    bot.send_message(message.chat.id, "Hi!")

    connect = sqlite3.connect('users_db.sql')
    cursor = connect.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (chat_id int, username varchar(25))")
    connect.commit()
    cursor.close()
    connect.close()

    register_user(message)
    main_menu(message)


def register_user(message):
    connect = sqlite3.connect('users_db.sql')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    if (message.chat.id, message.chat.username) not in users:
        cursor.execute("INSERT INTO users (chat_id, username) VALUES ('%d', '%s')" % (message.chat.id, message.chat.username))

    connect.commit()
    cursor.close()
    connect.close()


def main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton('Homework'))
    markup.add(telebot.types.KeyboardButton('Examination Schedule'))
    markup.add(telebot.types.KeyboardButton('Average Grade Calculator'))

    bot.send_message(message.chat.id, 'What do you need?', reply_markup=markup)
    bot.register_next_step_handler(message, actions_management)


def actions_management(message):
    if message.text == 'Homework':
        choose_subject(message)
    elif message.text == 'Examination Schedule':
        exams_schedule(message)
    elif message.text == 'Average Grade Calculator':
        average_grade_calculator(message)
    else:
        main_menu(message)


def choose_subject(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton('Mathematics'))
    markup.add(telebot.types.KeyboardButton('Physics'))
    markup.add(telebot.types.KeyboardButton('Programming'))

    bot.send_message(message.chat.id, 'Choose a subject', reply_markup=markup)
    bot.register_next_step_handler(message, subject_choice)


def subject_choice(message):
    global subject
    if message.text == 'Mathematics':
        subject = 'Mathematics'
        homework_actions(message)
    elif message.text == 'Physics':
        subject = 'Physics'
        homework_actions(message)
    elif message.text == 'Programming':
        subject = 'Programming'
        homework_actions(message)


def homework_actions(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton('See Homework'))
    markup.add(telebot.types.KeyboardButton('Add Homework'))
    markup.add(telebot.types.KeyboardButton('Remove Homework'))
    markup.add(telebot.types.KeyboardButton('Return to Main Menu'))

    bot.send_message(message.chat.id, 'What would you like to do?', reply_markup=markup)
    bot.register_next_step_handler(message, register_homework_action)


def register_homework_action(message):
    if message.text == 'See Homework':
        bot.send_message(message.chat.id, f"Tasks for {subject}: {homework[subject]['tasks']}, deadline:")
        homework_actions(message)
    elif message.text == 'Add Homework':
        bot.send_message(message.chat.id, f'Write the {subject} tasks you want to add')
        bot.register_next_step_handler(message, add_homework)
    elif message.text == 'Remove Homework':
        delete_homework(message)
    elif message.text == 'Return to Main Menu':
        main_menu(message)


def add_homework(message):
    homework[subject]['tasks'] = message.text.split()

    bot.send_message(message.chat.id, 'Write the deadline')
    bot.register_next_step_handler(message, add_hw_deadline)


def add_hw_deadline(message):
    homework[subject]['deadline'] = message.text.split()
    homework_actions(message)


def delete_homework(message):
    homework[subject]['tasks'] = ''
    homework[subject]['deadline'] = ''
    bot.send_message(message.chat.id, f'{subject} homework has been deleted successfully.')
    homework_actions(message)


def exams_schedule(message):
    exams_sched = ""
    for key in exams.keys():
        exams_sched += f"{key}: {exams[key]['date']}, at time {exams[key]['time']}, type: {exams[key]['type']}\n"

    bot.send_message(message.chat.id, exams_sched)
    main_menu(message)


def average_grade_calculator(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton('Calculate the Average Grade'))

    bot.send_message(message.chat.id, 'Type in a grade or proceed to calculation', reply_markup=markup)
    bot.register_next_step_handler(message, average_grade_actions)


def average_grade_actions(message):
    sum_grades = 0

    if message.text == 'Calculate the Average Grade':
        try:
            for grade in average_grade:
                sum_grades += grade
            bot.send_message(message.chat.id, f'Your average grade is {round(sum_grades/len(average_grade), 1)}')
            main_menu(message)
        except ZeroDivisionError:
            bot.send_message(message.chat.id, 'You have not input any grades. Please, try again')
            main_menu(message)
    else:
        average_grade.append(float(message.text))
        average_grade_calculator(message)


def send_schedule_notifications(chat_id):
    current_weekday = time.strftime('%A')
    current_time = time.strftime('%H:%M')
    lectures_today = lections_schedule[current_weekday]

    for lecture in lectures_today:
        lecture_time = lecture['time']
        notification_time = int(lecture_time[:2]) * 60 + int(lecture_time[3:]) - 5
        notification_time_hours = notification_time // 60
        notification_time_minutes = notification_time % 60

        if current_time == f'{notification_time_hours:02d}:{notification_time_minutes:02d}':
            bot.send_message(chat_id=chat_id, text=f"{lecture['name']} starts in 5 minutes!")


def get_users():
    connect = sqlite3.connect('users_db.sql')
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    chat_data = []

    for user in users:
        chat_data.append(user[0])

    return chat_data


if __name__ == '__main__':
    def schedule_job():
        chat_ids = get_users()
        for chat in chat_ids:
            send_schedule_notifications(chat)

    def run_schedule():
        schedule.every(105).minutes.do(schedule_job)
        while True:
            schedule.run_pending()
            time.sleep(1)

    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()

bot.infinity_polling()
