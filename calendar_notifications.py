from datetime import datetime
import os
from basic_notifications import path_to_obsidian as basic_path

path_to_obsidian = os.path.join(basic_path, 'Calendar')


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
    """
    Отправляет уведомления из подкаталогов в каталоге Calendar(кроме 'Дни Рождения') боту и удаляет их
    """

    def __init__(self):
        self.md_files_list = []  # Список со ссылками на файлы .md в директории обсидиан в которых подходящая
        # последняя строка
        self.notifications = dict()
        self.list_for_bot = []

    def generate_list_md(self, path):
        """Создаёт список с названиями файлов .md в директории"""
        for directory in os.listdir(path):
            if directory == 'Дни Рождения':
                continue
            root_path_to_file = os.path.join(path, directory)
            if root_path_to_file.endswith('.md'):
                if read_last_str(root_path_to_file).startswith('---'):
                    if read_first_str(root_path_to_file).startswith('---'):
                        self.md_files_list.append(root_path_to_file)
            if os.path.isdir(os.path.join(path, directory)):
                for file in os.listdir(os.path.join(path, directory)):
                    path_to_file = os.path.join(path, directory, file)
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
        """
        Находит уведомления, если дата не настала, но уведомление помечено выполненным, то удаляет уведомление;
        если дата уведомлениям наступила, то отправляет название уведомления в "self.list_for_bot" и удаляет уведомление
        """
        for file, parameters in self.notifications.items():
            if 'date' in parameters.keys() and 'startTime' in parameters.keys() and 'daysOfWeek' not in parameters.keys():
                # Одноразовое не на весь день
                date_notification = datetime.strptime(f"{parameters['date']} {parameters['startTime']}",
                                                      '%Y-%m-%d %H:%M')
                if date_notification > datetime.now():
                    if parameters['completed'] != 'false' and parameters['completed'] != 'null':
                        os.remove(file)
                else:
                    self.list_for_bot.append(parameters['title'])
                    os.remove(file)
            if 'date' in parameters.keys() and 'startTime' not in parameters.keys() and 'daysOfWeek' not in parameters.keys():
                # Одноразовое на весь день
                date_notification = datetime.strptime(f"{parameters['date']}", '%Y-%m-%d')
                if date_notification > datetime.now():
                    if parameters['completed'] != 'false' and parameters['completed'] != 'null':
                        os.remove(file)
                else:
                    self.list_for_bot.append(parameters['title'])
                    os.remove(file)


def start_bot_calendar_notifications():
    notifications = CalendarNotifications()
    notifications.generate_list_md(path_to_obsidian)
    notifications.add_info_notifications()
    notifications.notification_time()
    return notifications.list_for_bot


if __name__ == '__main__':
    start_bot_calendar_notifications()
