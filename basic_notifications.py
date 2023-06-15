from datetime import datetime
import os

path_to_obsidian = os.path.abspath(r'C:\Users\DE\Obsidian\Obsidian')  # Указать путь до Obsidian


def read_last_str(path_to_file: str) -> str:
    """Читает последнюю строку в файле и удаляет '*'"""
    my_file = open(path_to_file, 'r', encoding='utf=8')
    last_str = my_file.readlines()[-1].replace('*', '')
    my_file.close()
    return last_str


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


class BasicNotifications:
    """
    Данный класс собирает все уведомления из последних строк файлов в общей директории обсидиана, проверяет их дату,
    если дата прошла - заменяет уведомление из последней строки на 'Уведомление отправлено' и собирает эти уведомления
    в список 'list_for_bot', затем возвращает его; если дата не прошла - пропускает действие.
    Последняя строка должна иметь вид:
     *Notifications:* 2023-06-06 90:39 Текст уведомления; 2023-06-06 10:39 Текст уведомления;
    """

    def __init__(self, path):
        self.path_to_obsidian = path
        self.md_files_list = []  # Список со ссылками на файлы .md в директории обсидиан в которых подходящая
        # последняя строка
        self.notifications = dict()
        self.list_for_bot = []

    def generate_list_md(self):
        """Создаёт список с названиями файлов .md в директории"""
        self.md_files_list = [os.path.join(self.path_to_obsidian, file) for file in os.listdir(self.path_to_obsidian) if
                              file.endswith('.md') if
                              read_last_str(os.path.join(self.path_to_obsidian, file)).startswith(
                                  'Notifications:')]

    def add_notifications(self):
        """Из файлов с уведомлениями достаёт последнюю строку"""
        for file in self.md_files_list:
            tmp_last_str = read_last_str(file).replace('Notifications:', '').split(';')
            last_str = [notification.strip() for notification in tmp_last_str]
            self.notifications[file] = last_str

    def notification_time(self):
        """Добавляет текст уведомлений в список, который передается в main для отправки в сообщения в телеграмм"""
        for file, notifications in self.notifications.items():
            for notification in notifications:
                if notification == '':
                    continue
                elif notification == 'Уведомление отправлено':
                    continue
                else:
                    try:
                        time_notification = datetime.strptime(
                            f'{notification.split(" ")[0]} {notification.split(" ")[1]}',
                            '%Y-%m-%d %H:%M')
                        if time_notification > datetime.now():
                            continue
                        else:
                            text_notification = f'{" ".join(notification.split(" ")[2:])}'
                            self.list_for_bot.append(text_notification)
                    except (ValueError, IndexError):
                        self.list_for_bot.append([
                            f'{str(datetime.now())} Ошибка в блоке try (неверно указан формат уведомления) file: {file}', ])

    def add_status_notification1(self):
        """Заменяет последнюю строку в файлах с уведомлениями"""
        for file, notifications in self.notifications.items():
            list_last_str = []
            for notification in notifications:
                if notification == '':
                    break
                elif notification == 'Уведомление отправлено':
                    continue
                else:
                    try:
                        time_notification = datetime.strptime(
                            f'{notification.split(" ")[0]} {notification.split(" ")[1]}',
                            '%Y-%m-%d %H:%M')
                        if time_notification > datetime.now():
                            list_last_str.append(notification)
                        else:
                            list_last_str.append('Уведомление отправлено')
                            continue
                    except (ValueError, IndexError):
                        break

            last_str = f"*Notifications:* {'; '.join(list_last_str)}"
            del_and_wr_last_str(path_to_file=file, last_str=last_str)


def start_bot_notifications():
    notifications = BasicNotifications(path_to_obsidian)
    notifications.generate_list_md()
    notifications.add_notifications()
    notifications.notification_time()
    notifications.add_status_notification1()
    return notifications.list_for_bot


if __name__ == '__main__':
    start_bot_notifications()
