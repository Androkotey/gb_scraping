import requests
from pymongo import MongoClient
from contextlib import contextmanager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver


def data_insert(collection, data, index='title'):
    """ Добавляет данные в коллекцию """

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


PATH_TO_CHROMEDRIVER = 'Y:\\My_Programs\\chromedriver_win32\\chromedriver.exe'


class ConnectionToDriver:

    def __init__(self, url, chr_drv=PATH_TO_CHROMEDRIVER):
        self._url = url
        self._s = Service(chr_drv)
        self._options = Options()
        self._options.add_argument('start-maximized')
        self.driver = webdriver.Chrome(service=self._s, options=self._options)
        self.driver.implicitly_wait(10)
        self.driver.get(url)

    def close(self):
        self.driver.close()


def my_request(url, cookies=None):
    #headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}
    response = requests.get(url, cookies=cookies)
    if response.ok:
        return response.text
    else:
        print(f"Что-то не так")
        print(f"code: {response.status_code}")
        print(f"headers: {response.headers}")
        exit()
