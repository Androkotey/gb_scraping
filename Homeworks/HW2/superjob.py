from pprint import pprint

from bs4 import BeautifulSoup as bs
import pandas as pd
import requests


def link_extraction(link, main_url):
    if link.startswith('https://'):
        return link
    return main_url + link


def pseudo_space_handling(raw_salary):
    pseudo_space_indexes = []
    for i, letters in enumerate(zip(raw_salary[:-2], raw_salary[1:-1], raw_salary[2:])):
        x, y, z = letters
        if y == ' ' and x.isdigit() and z.isdigit():
            pseudo_space_indexes.append(i)
    temp = list(raw_salary)
    for ind in pseudo_space_indexes:
        temp[ind + 1] = '.'
    raw_salary = ''.join(temp).replace('.', '')
    return raw_salary


def salary_extraction(vacancy_salary):
    salary_dict = {'min': None, 'max': None, 'cur': None}

    if vacancy_salary.getText() != 'По договорённости':
        raw_salary = pseudo_space_handling(vacancy_salary.getText().replace('\xa0', ' ')).replace(' — ', ' ').replace('вахта 45 дней', 'месяц').split()
        if len(raw_salary) == 2:
            salary_dict['min'] = int(raw_salary[0])
            salary_dict['max'] = int(raw_salary[0])
            salary_dict['cur'] = raw_salary[1]
        else:
            if raw_salary[0] == 'до':
                salary_dict['max'] = int(raw_salary[1])
            elif raw_salary[0] == 'от':
                salary_dict['min'] = int(raw_salary[1])
            else:
                salary_dict['min'] = int(raw_salary[0])
                salary_dict['max'] = int(raw_salary[1])
            salary_dict['cur'] = raw_salary[2].split('/')[0]
        return salary_dict
    return salary_dict


main_url = 'https://www.superjob.ru'

params = {'noGeo': '1', 'keywords': input('Введите вакансию для поиска: ')}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}
page_link = '/vacancy/search'
vacancies = []
i = 0

while True:
    params['page'] = i
    response = requests.get(main_url + page_link,
                            params=params,
                            headers=headers)
    html = response.text
    soup = bs(html, 'html.parser')
    vacancies_soup = soup.find_all('div', {'class': ['f-test-search-result-item']})

    if not vacancies_soup:
        break

    print(f'Page {i} is being processed...')
    for vacancy in vacancies_soup:
        cond_for_continue_1 = 'Откликнуться' not in vacancy.getText()
        if cond_for_continue_1:
            continue

        vacancy_data = {'website': 'superjob.ru'}
        vacancy_title = vacancy.find('a')
        vacancy_name = vacancy_title.getText()

        cond_for_continue_2 = vacancy_name == ''
        if cond_for_continue_2:
            continue  # пропуск рекламной вакансии (Дикси)

        vacancy_link = link_extraction(vacancy_title['href'], main_url)
        vacancy_salary = salary_extraction(vacancy.find('span', {'class': ['f-test-text-company-item-salary']}))
        try:
            vacancy_employer = vacancy.find('span', {'class': 'f-test-text-vacancy-item-company-name'}).getText().replace('\xa0', ' ')
            vacancy_address = vacancy.find('span', {'class': 'f-test-text-company-item-location'}).getText().replace('\xa0', ' ').split(' • ')[1]
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

    print(f'Page {i} done')
    i += 1

vacancies_data = pd.DataFrame(data=vacancies)
prefix = '_'.join(params['keywords'].split())
vacancies_data.to_csv(f'sj_vacancies_{prefix}.csv', index=False)
