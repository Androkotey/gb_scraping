from lxml import html
import my_functions as my


def get_data(url):
    """ Возвращает список с собранной информацией по новостям"""

    dom = html.fromstring(my.my_request(url))

    # Проверяем в том числе, чтобы внутри нужного контейнера не было упоминаний про рекламу, потом возвращемся наверх
    items = dom.xpath("//div[contains(@class, 'mg-grid__item')]/*[not(contains(@class, 'advert'))]/..")
    list_items = []
    for item in items:
        item_info = dict()

        link = item.xpath(".//h2/a/@href")[0]
        title = item.xpath(".//h2/a/text()")[0]
        source = item.xpath(".//a[@class='mg-card__source-link']/text()")[0]
        time = item.xpath(".//span[@class='mg-card-source__time']/text()")[0]

        item_info['link'] = link
        item_info['title'] = title
        item_info['source'] = source
        item_info['timestamp'], item_info['datetime'] = my.get_date_yandex(time)

        list_items.append(item_info)

    return list_items


@my.multiple_call(count=10, pause=60)
def main():
    data = get_data('https://yandex.ru/news')  # получение информации о главных новостях
    with my.connect_to_mongodb_collection(database_name='hw4', collection_name='news', delete=False) as collection:
        my.data_insert(collection, data)  # добавление новостей в коллекцию


if __name__ == '__main__':
    main()
