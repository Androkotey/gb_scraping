from lxml import html
import my_functions as my


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

        info = my.get_info_lenta(link, time)
        item_info['link'] = info[0]
        item_info['source'] = info[1]
        item_info['timestamp'] = info[2]
        item_info['datetime'] = info[3]
        item_info['title'] = title

        list_items.append(item_info)

    return list_items


@my.multiple_call(count=10, pause=60)
def main():
    data = get_data('https://lenta.ru/')  # получение информации о главных новостях

    with my.connect_to_mongodb_collection(database_name='hw4', collection_name='news', delete=False) as collection:
        my.data_insert(collection, data)  # добавление новостей в коллекцию


if __name__ == '__main__':
    main()
