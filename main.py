import telebot
import sqlite3

TOKEN = ""

bot = telebot.TeleBot(TOKEN)

schedule = {}

homework = []


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


if __name__ == '__main__':
    pass

bot.infinity_polling()
