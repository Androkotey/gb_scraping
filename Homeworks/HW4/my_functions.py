from pymongo import MongoClient
from contextlib import contextmanager
from datetime import datetime
import requests


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


def data_insert(collection, data):
    """ Добавляет данные в коллекцию """

    news_before = collection.count_documents({})

    for doc in data:
        collection.update_one({'link': doc['link']},
                              {'$setOnInsert': {**doc}},
                              upsert=True)

    news_after = collection.count_documents({})
    difference = news_after - news_before
    if difference:
        print(f'В коллекцию добавлено {difference} записей')


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


# Функции для yandex
def get_timestamp_yandex(time):
    """ Комбинирует время новости и сегодняшнюю дату, так как не смог найти дату на странице с новостями """
    time = list(map(int, time.split(':')))
    timestamp = datetime.now().replace(hour=time[0], minute=time[1], second=0)
    return timestamp


def get_datetime_yandex(time):
    return time + ' ' + str(datetime.now().date())
