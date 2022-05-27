from pymongo import MongoClient
from contextlib import contextmanager
from datetime import datetime, timedelta
import re
import requests


# Функции для mail
def get_date_mail(date):
    """ Возвращает дату в двух форматах """
    news_timespan = datetime.fromisoformat(date)
    news_datetime = news_timespan.strftime('%H:%M %Y-%m-%d')
    return news_timespan, news_datetime


# Функции для yandex
def get_date_yandex(time):
    """ Комбинирует время новости и сегодняшнюю дату (не смог найти дату на странице) """

    today = datetime.now()
    time = time.replace('вчера', str(today.day - 1))
    if len(time.split(' ')) > 2:
        day = int(time.split(' ')[0])
        today = today - timedelta(days=today.day - day)
        time = time[-5:]

    news_datetime = time + ' ' + str(today.date())
    time = list(map(int, time.split(':')))
    news_timestamp = today.replace(hour=time[0], minute=time[1], second=0)
    return news_timestamp, news_datetime


# Функции для lenta
def get_info_lenta(link, time):
    """ Возвращает кортеж из ссылки, источника и даты в двух форматах """

    date = get_date_lenta(link)
    dt = time + ' ' + date

    if link.startswith('/'):
        link = 'https://lenta.ru' + link
        source = 'https://lenta.ru'
        timestamp = datetime.strptime(time + ' ' + date, '%H:%M %Y/%m/%d')
    else:
        source = re.search(r"(https://\w+.\w+)", link)[0]
        timestamp = datetime.strptime(time + ' ' + date, '%H:%M %d/%m/%Y')

    return link, source, timestamp, dt


def get_date_lenta(link):
    """ Получает дату из ссылок двух видов """

    if link.startswith('/'):
        pattern = r"(?:\d[\d/]+\d)"
        return re.search(pattern, link)[0][:10]
    else:
        pattern = r"(?:\d[\d-]+\d)"
        return re.search(pattern, link)[0].replace('-', '/')


# Общие функции
def my_request(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/101.0.4951.67 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.ok and len(response.text) > 7000:
        return response.text
    else:
        print("Что-то не так")
        exit()


def data_insert(collection, data, index='title'):
    """ Добавляет данные в коллекцию """
    # Удалить дубликаты из монго (сначала добавлял по ссылке, но у Яндекса они динамические...):
    # db.news.find({}, {title:1}).sort({_id:1}).forEach(function(doc){db.news.remove({_id:{$gt:doc._id}, title:doc.title});})

    news_before = collection.count_documents({})

    for doc in data:
        collection.update_one({index: doc[index]},
                              {'$setOnInsert': {**doc}},
                              upsert=True)

    news_after = collection.count_documents({})
    difference = news_after - news_before
    if difference:
        print(f'В коллекцию добавлено {difference} записей')
    else:
        print('Нечего добавлять')


def multiple_call(count, pause):
    """ Декоратор вызывает функцию несколько раз с паузами """
    from time import sleep

    def my_decorator(func):
        def wrapped(*args, **kwargs):
            for i in range(count):
                func(*args, **kwargs)
                sleep(pause)

        return wrapped

    return my_decorator


@contextmanager
def connect_to_mongodb_collection(database_name, collection_name, delete=False):
    """ Открывает соединение, удаляет коллекцию после отработки, если необходимо, и закрывает соединение """

    client = MongoClient('127.0.0.1', 27017)
    db = client[database_name]
    collection = db[collection_name]

    yield collection

    count_documents = collection.count_documents({})
    if delete:
        db.drop_collection(collection_name)
        print(f"Удалена коллеция с {count_documents} документами")
    client.close()
