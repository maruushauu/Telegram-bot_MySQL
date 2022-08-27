#import  sys
import telebot
import mysql.connector
#from mysql.connector import errorcode

bot = telebot.TeleBot("5440338532:AAFO3TFj7uyqPAUwb8Zh-flwfHIHf3L9sno")

# узнать id группы (группа должна быть публичной)
#-1001667908621
#print(bot.get_chat('@marymql').id)



#try:
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456789",
    port="3306",
    database="BOTT"
)

cursor = db.cursor()
# создадим таблицу для регистрации пользователей в users, заявки от пользователя храняться в  regs
#cursor.execute("CREATE TABLE regs (id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255),description VARCHAR(255), user_id INT(11))")

#cursor.execute("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255), telegram_user_id INT(11) UNIQUE)")

user_data = {}


class User:
    def __init__(self, first_name):
        self.first_name = first_name
        self.last_name = ''
        self.description = ''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, "Введите имя")
    bot.register_next_step_handler(msg, process_firstname_step)


def process_firstname_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)
        msg = bot.send_message(message.chat.id, "Введите фамилию")
        bot.register_next_step_handler(msg, process_lastname_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def process_lastname_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.last_name = message.text

        msg = bot.send_message(message.chat.id, "Как прошел день?")
        bot.register_next_step_handler(msg, process_description_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')

#message.from_user.first_name, message.from_user.last_name -- регистрация реального реального имени и фамилии из телеги( регистрация ника в аккаунте)
#проверим telegram_user_id чтобы избежать повторной регистрации
def process_description_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.description = message.text

        sql = "SELECT * FRON users WHERE telelgram_user_id={0}".format(user_id)
        cursor.execute(sql)
        existsUser = cursor.fetchone()
        print(existsUser)

        if(existsUser == None):
                sql = "INSERT INTO users (first_name, last_name , telegram_user_id) VALUES (%s, %s, %s)"
                val = (message.from_user.first_name, message.from_user.last_name, user_id)
                cursor.execute(sql, val)

        sql = "INSERT INTO regs (first_name, last_name,description , user_id) VALUES (%s, %s, %s, %s)"
        val = (user.first_name, user.last_name, user.description, user_id)
        cursor.execute(sql, val)

        db.commit()
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы!")
        bot.send_message(-1001667908621, user.first_name + ' ' + user.last_name)
    except Exception as e:
        bot.reply_to(message, 'oooops')


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.infinity_polling()
if __name__ == '__main__':
    bot.polling(none_stop=True)
