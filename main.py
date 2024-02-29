import telebot
import sqlite3

TOKEN = ""

bot = telebot.TeleBot(TOKEN)

schedule = {}

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
    cursor.execute("INSERT INTO users (chat_id, username) VALUES ('%d', '%s')" % (message.chat.id, message.chat.username))

    connect.commit()
    cursor.close()
    connect.close()

    main_menu(message)


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
        hw_tasks = ""
        for task in homework[subject]:
            hw_tasks += f"Tasks for {subject}: {homework[subject]['tasks']}, deadline:"
        bot.send_message(message.chat.id, hw_tasks)
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
    schedule = ""
    for key in exams.keys():
        schedule += f"{key}: {exams[key]['date']}, at time {exams[key]['time']}, type: {exams[key]['type']}\n"

    bot.send_message(message.chat.id, schedule)
    main_menu(message)


def average_grade_calculator(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton('Calculate the Average Grade'))

    bot.send_message(message.chat.id, 'Type in a grade or proceed to calculation', reply_markup=markup)
    bot.register_next_step_handler(message, average_grade_actions)


def average_grade_actions(message):
    sum = 0

    if message.text == 'Calculate the Average Grade':
        try:
            for grade in average_grade:
                sum += grade
            bot.send_message(message.chat.id, f'Your average grade is {round(sum/len(average_grade), 1)}')
            main_menu(message)
        except ZeroDivisionError:
            bot.send_message(message.chat.id, 'You have not input any grades. Please, try again')
            main_menu(message)
    else:
        average_grade.append(float(message.text))
        average_grade_calculator(message)


if __name__ == '__main__':
    pass

bot.infinity_polling()
