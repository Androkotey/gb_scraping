from lxml import html
import my_functions as my


def get_links(url):
    """ Собирает ссылки на новости """
    dom = html.fromstring(my.my_request(url))

    links_1 = "//a[contains(@class, 'js-topnews__item')]/@href"  # ссылки на топ-новости с картинками
    links_2 = "//li//a[not(contains(@href, 'foto-dnya'))]/@href"  # ссылки на все новости без картинок
    links_3 = "//a[@class='newsitem__title link-holder']/@href"  # ссылки на остальные новости с картинками

    links = dom.xpath('|'.join([links_1, links_2, links_3]))
    return set(links)


def get_info(url):
    """ Извлекает данные с одной страницы """
    dom = html.fromstring(my.my_request(url))

    # защита от прямых ссылок на источник и от diafilm
    if not url.startswith('https://news.mail.ru/') or 'diafilm' in url:
        return

    item_info = dict()

    link = url
    source = dom.xpath("//a[contains(@class,'breadcrumbs__link')]/span[@class='link__text']/../@href")[0]
    title = dom.xpath("//h1[@class='hdr__inner']/text()")[0]
    date = dom.xpath("//span[@datetime]/@datetime")[0]

    item_info['link'] = link
    item_info['source'] = source
    item_info['title'] = title
    item_info['timestamp'], item_info['datetime'] = my.get_date_mail(date)

    return item_info


def get_data(links):
    """ Обходит список ссылок и возвращает список с собранной информацией """

    list_news = []
    for link in links:
        info = get_info(link)
        if info:
            list_news.append(info)
    return list_news


@my.multiple_call(count=10, pause=60)
def main():
    links = get_links('https://news.mail.ru/')
    data = get_data(links)

    with my.connect_to_mongodb_collection(database_name='hw4', collection_name='news', delete=False) as collection:
        my.data_insert(collection, data)


if __name__ == "__main__":
    main()
