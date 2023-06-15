from datetime import datetime, timedelta
import os
from dateutil.relativedelta import relativedelta
from calendar_notifications import path_to_obsidian as path

path_to_obsidian = os.path.join(path, 'Дни Рождения')


def read_last_str(path_to_file: str) -> str:
    """Читает последнюю строку в файле"""
    my_file = open(path_to_file, 'r', encoding='utf=8')
    last_str = my_file.readlines()[-1]
    my_file.close()
    return last_str


def read_first_str(path_to_file: str) -> str:
    """Читает перовую строку в файле"""
    my_file = open(path_to_file, 'r', encoding='utf=8')
    first_str = my_file.readlines()[0]
    my_file.close()
    return first_str


def del_and_wr_last_str(path_to_file: str, last_str: str):
    """ Удаляет последнюю строку в файле и вставляет нужную"""
    file_r = open(path_to_file, 'r', encoding='utf=8')
    data = file_r.readlines()[:-1]
    file_r.close()
    file_w = open(path_to_file, 'w', encoding='utf=8')
    for line in data:
        file_w.write(line)
    file_w.close()
    file_end = open(path_to_file, 'a', encoding='utf=8')
    file_end.write(last_str)
    file_end.close()


class CalendarNotifications:
    """Отправляет уведомления из подкаталога 'Дни Рождения' в каталоге Calendar боту и удаляет их"""

    def __init__(self):
        self.md_files_list = []  # Список со ссылками на файлы .md в директории обсидиан в которых подходящая
        # последняя строка
        self.notifications = dict()
        self.list_for_bot = []

    def generate_list_md(self, path):
        """Создаёт список с названиями файлов .md в директории"""
        for file in os.listdir(path):
            path_to_file = os.path.join(path, file)
            if path_to_file.endswith('.md'):
                if read_last_str(path_to_file).startswith('---'):
                    if read_first_str(path_to_file).startswith('---'):
                        self.md_files_list.append(path_to_file)

    def add_info_notifications(self):
        """
        Из файлов с уведомлениями достаёт информацию и кладёт в словарь, где ключ=путь до файла уведомления, значение =
        подсловарьсловарь, в котором ключ и значения взяты из файла уведомления
        """
        for path in self.md_files_list:
            file = open(path, 'r', encoding='utf8')
            data = file.readlines()[1:-1]
            file.close()
            tmp_parameters = dict()
            for parameters in data:
                tmp_parameters[parameters.split(':', 1)[0].strip()] = parameters.split(':', 1)[1].strip()
            self.notifications[path] = tmp_parameters

    def notification_time(self):
        """Находит уведомления о днях рождения и заносит записи за 31 день, 14 дней и день в день"""
        for file, parameters in self.notifications.items():
            date_notification = datetime.date(datetime.strptime(f"{parameters['date']}", '%Y-%m-%d'))
            if date_notification - timedelta(days=31) == datetime.date(datetime.now()):
                self.list_for_bot.append(f'Осталось 31 день до {parameters["title"]}')
            if date_notification <= datetime.date(datetime.now()):
                self.list_for_bot.append(f'Сегодня {parameters["title"]}')
                list_strs_name = file.split('.')
                list_strs_name[0] = f"{file.split('.')[0]}_"
                new_file = '.'.join(list_strs_name)
                file_n = open(new_file, 'w', encoding='utf8')
                file_n.write('---\n')
                for parameter_k, parameter_v in parameters.items():
                    if parameter_k == 'date':
                        old_date = datetime.strptime(parameter_v, '%Y-%m-%d')
                        new_date = old_date + relativedelta(years=+1)
                        file_n.write(f'{parameter_k}: {datetime.date(new_date)}\n')
                    else:
                        file_n.write(f'{parameter_k}: {parameter_v} \n')
                file_n.write('---\n')
                file_n.close()
                os.remove(file)


def start_bot_birthday_notifications():
    notifications = CalendarNotifications()
    notifications.generate_list_md(path_to_obsidian)
    notifications.add_info_notifications()
    notifications.notification_time()
    return notifications.list_for_bot


if __name__ == '__main__':
    start_bot_birthday_notifications()
