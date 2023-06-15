import telebot
from multiprocessing import Process, Queue
import time
from basic_notifications import start_bot_notifications
from birthday_notification import start_bot_birthday_notifications
from calendar_notifications import start_bot_calendar_notifications
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TOKEN'))  # заменить на строку ниже
# bot = telebot.TeleBot('Токен вашего бота')

my_id = os.getenv('my_id')  # заменить на строку ниже
# my_id = os.getenv('Ваш id в телеграмме')


def add_basic_notifications(link_f):
    while True:
        time.sleep(30)
        notifications = start_bot_notifications()
        if len(notifications) != 0:
            link_f.put(notifications)


def add_calendar_notifications(link_f):
    while True:
        time.sleep(30)
        notifications = start_bot_calendar_notifications()
        if len(notifications) != 0:
            link_f.put(notifications)


def add_birthday_notifications(link_f):
    while True:
        time.sleep(40)
        notifications = start_bot_birthday_notifications()
        if len(notifications) != 0:
            link_f.put(notifications)


def send_message(link_f):
    time.sleep(15)
    while True:
        basic_notifications = link_f.get()
        if len(basic_notifications) != 0:
            for notification in basic_notifications:
                time.sleep(1)
                bot.send_message(my_id, notification)


def start_bot():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    link = Queue()
    p_add_basic_notifications = Process(target=add_basic_notifications, args=(link,))
    p_send_messages = Process(target=send_message, args=(link,))
    p_add_birthday_notifications = Process(target=add_birthday_notifications, args=(link,))
    p_add_calendar_notifications = Process(target=add_calendar_notifications, args=(link,))
    p_add_basic_notifications.start()
    p_send_messages.start()
    p_add_birthday_notifications.start()
    p_add_calendar_notifications.start()
    p_add_basic_notifications.join()
    p_send_messages.join()
    p_add_birthday_notifications.join()
    p_add_calendar_notifications.join()
