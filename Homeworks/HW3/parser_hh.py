""" Немного изменённый код из 2-ой домашней работы """

from bs4 import BeautifulSoup as bs
import requests


def salary_extraction(vacancy_salary):
    salary_dict = {'min': None, 'max': None, 'cur': None}

    if vacancy_salary:
        raw_salary = vacancy_salary.getText().replace(' – ', ' ').replace(' ', '').split()
        if raw_salary[0] == 'до':
            # до 380 000 руб.
            salary_dict['max'] = int(raw_salary[1])
        elif raw_salary[0] == 'от':
            # от 50 000 руб.
            salary_dict['min'] = int(raw_salary[1])
        else:
            # 50 000 – 100 000 руб.
            salary_dict['min'] = int(raw_salary[0])
            salary_dict['max'] = int(raw_salary[1])
        salary_dict['cur'] = ''.join(raw_salary[2:])  # решение проблемы бел. руб.

    return salary_dict


def get_vacancies(text):
    main_url = 'https://spb.hh.ru/'
    page_link = '/search/vacancy'  # ссылка на первую страницу поиска

    params = {'search_field': ['name', 'company_name', 'description'], 'items_on_page': 20,
              'text': text}
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/101.0.4951.67 Safari/537.36'}

    vacancies = []
    while True:
        response = requests.get(main_url+page_link,
                                params=params,
                                headers=headers)
        html = response.text
        soup = bs(html, 'html.parser')
        vacancies_soup = soup.find_all('div', {'class': ['vacancy-serp-item-body__main-info']})

        for vacancy in vacancies_soup:

            vacancy_data = {'website': 'hh.ru'}

            vacancy_title = vacancy.find('a')
            vacancy_name = vacancy_title.getText()
            vacancy_link = vacancy_title['href'][: vacancy_title['href'].index('?')]
            vacancy_salary = salary_extraction(vacancy.find('span', {'class': ['bloko-header-section-3']}))
            try:
                vacancy_employer = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).getText().replace('\xa0', ' ')
                vacancy_address = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).getText().replace('\xa0', ' ')
            except AttributeError:
                continue

            vacancy_data['name'] = vacancy_name
            vacancy_data['link'] = vacancy_link
            vacancy_data['salary_min'] = vacancy_salary['min']
            vacancy_data['salary_max'] = vacancy_salary['max']
            vacancy_data['salary_currency'] = vacancy_salary['cur']
            vacancy_data['employer'] = vacancy_employer
            vacancy_data['address'] = vacancy_address

            vacancies.append(vacancy_data)

        next_page = soup.find('a', {'data-qa': 'pager-next'})
        if not next_page:
            break

        page_link = next_page['href']
    return vacancies


if __name__ == '__main__':
    print(len(get_vacancies('data scientist')))
