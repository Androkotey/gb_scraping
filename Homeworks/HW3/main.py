from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from contextlib import contextmanager

# мои модули
from parser_hh import get_vacancies
from mongo_queries import salary_filter


# Будем хранить ссылки на вакансии в множестве
PRIMARY_KEYS = set()
# заменить проверку на
# if collection.find_one('link', doc['link']):
#     print('Документ существует в базе')
# Но лучше сделать update_one с параметром upsert=True


def pprint_cursor_object(cursor):
    for doc in cursor:
        pprint(doc)


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


def add_data_to_collection(collection, data):
    """ Добавляет вакансии в коллекцию """

    for doc in data:
        try:
            if doc['link'] in PRIMARY_KEYS:
                raise DuplicateKeyError('err')
            PRIMARY_KEYS.add(doc['link'])
            collection.insert_one(doc)
        except DuplicateKeyError:
            print(f'Вакансия {doc["name"]} в {doc["address"]} уже существует в базе')


def get_sample(collection, num=1):
    """ Выбирает несколько записей из коллекции и убирает поля _id (чтобы честно по ссылке проверять дубликаты)"""

    return collection.aggregate([{'$sample': {'size': num}}, {'$project': {"_id": 0}}])


def main():
    with connect_to_mongodb_collection(database_name='hw3_database',
                                       collection_name='vacancies',
                                       delete=True) as vacancies:
        list_of_vacancies = get_vacancies(text='data scientist')  # получили вакансии от парсера
        add_data_to_collection(vacancies, list_of_vacancies)  # добавили вакансии в базу
        sample = get_sample(vacancies, 4)  # получили набор из случайных вакансий
        add_data_to_collection(vacancies, sample)  # попытались добавить набор в коллекцию
        pprint_cursor_object(salary_filter(vacancies, 500000))  # фильтруем и выводим вакансии


if __name__ == '__main__':
    main()
