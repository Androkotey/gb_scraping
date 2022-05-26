import re
from lxml import html
from datetime import datetime

import my_functions as my
from my_functions import multiple_call  # декоратор помогает многократно с паузами вызывать функцию


def get_info(link, time):
    """ Возвращает кортеж из ссылки, источника и даты в двух форматах """

    date = get_date(link)
    dt = time + ' ' + date

    if link.startswith('/'):
        link = 'https://lenta.ru' + link
        source = 'https://lenta.ru'
        timestamp = datetime.strptime(time + ' ' + date, '%H:%M %Y/%m/%d')
    else:
        source = re.search(r"(https://\w+.\w+)", link)[0]
        timestamp = datetime.strptime(time + ' ' + date, '%H:%M %d/%m/%Y')

    return link, source, timestamp, dt


def get_date(link):
    """ Получает дату из ссылок двух видов """

    if link.startswith('/'):
        pattern = r"(?:\d[\d/]+\d)"
        return re.search(pattern, link)[0][:10]
    else:
        pattern = r"(?:\d[\d-]+\d)"
        return re.search(pattern, link)[0].replace('-', '/')


def get_data(url):
    """ Возвращает список с собранной информацией по новостям """
    dom = html.fromstring(my.my_request(url))

    items = dom.xpath("//a[contains(@class, '_topnews')]")

    list_items = []
    for item in items:
        item_info = dict()

        link = item.xpath("./@href")[0]
        title = item.xpath(".//*[contains(@class, 'title') and not (contains(@class, 'titles'))]/text()")[0]
        time = item.xpath(".//time[contains(@class, 'date')]/text()")[0]

        info = get_info(link, time)
        item_info['link'] = info[0]
        item_info['source'] = info[1]
        item_info['timestamp'] = info[2]
        item_info['datetime'] = info[3]
        item_info['title'] = title

        list_items.append(item_info)

    return list_items


@multiple_call(count=10, pause=60)
def main():
    data = get_data('https://lenta.ru/')  # получение информации о главных новостях

    with my.connect_to_mongodb_collection(database_name='hw4', collection_name='news', delete=False) as collection:
        my.data_insert(collection, data)  # добавление новостей в коллекцию


if __name__ == '__main__':
    main()
