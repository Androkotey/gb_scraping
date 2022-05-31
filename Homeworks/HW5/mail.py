from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import my_functions as my
from tokens import mail_login, mail_password

PATH_TO_CHROMEDRIVER = 'Y:\\My_Programs\\chromedriver_win32\\chromedriver.exe'
url = "https://account.mail.ru/login/"

login = mail_login
password = mail_password

STOP = 0

options = Options()
options.add_argument('start-maximized')
driver = webdriver.Chrome(service=Service(PATH_TO_CHROMEDRIVER), options=options)
driver.implicitly_wait(10)
wait = WebDriverWait(driver, 10)

driver.get(url)

login_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")))
login_field.send_keys(login)

enter = wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Ввести пароль")]')))
enter.click()

login_password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']")))
login_password.send_keys(password)

enter = wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Войти")]')))
enter.click()


def down(i):
    """
    Прокручивает страницу вниз
    """

    try:
        if i == 1:
            anchor = get_letters()
            anchor[len(anchor) // 2].send_keys(Keys.PAGE_UP)
            return
        anchor = get_letters()
        anchor[len(anchor) // 2].send_keys(Keys.PAGE_UP)
        anchor = get_letters()
        anchor[len(anchor) // 2].send_keys(Keys.PAGE_DOWN)
        anchor = get_letters()
        anchor[len(anchor) // 2].send_keys(Keys.PAGE_DOWN)
    except:
        return


def get_letters():
    """
    Получает список объектов, из которых потом можно достать ссылки на письма
    """
    time.sleep(0.2)
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'llc_normal')]")))
    letters = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc_normal')]")
    return letters


def add_links(letters, links_list):
    """
    Добавляет ссылки в список. STOP, чтобы вспомнить, что упёрлось в дно
    """

    global STOP
    cnt = 0
    for letter in letters:
        link = letter.get_attribute('href')
        if link not in links_list:
            links_list.append(link)
            cnt += 1
    print(f'Добавлено {cnt} писем')
    print(f'Всего {len(links_list)} писем')
    if cnt == 0:
        STOP += 1
    else:
        STOP = 0


def get_all_letter_links():
    """
    Возвращает список ссылок на все письма
    """

    time.sleep(5)
    links = []
    i = 0
    while STOP != 3:
        add_links(get_letters(), links)
        down(i)
        i += 1

    return links


def get_data(links):
    """
    Заходит в каждое письмо и собирает информацию (очень медлено)
    """

    letters = []
    for i, link in enumerate(links):
        driver.get(url=link)
        letter_info = {}

        time.sleep(1)
        letter_info['title'] = driver.find_element(By.CSS_SELECTOR, "h2[class='thread-subject']").text
        letter_info['from'] = driver.find_element(By.CSS_SELECTOR, "span[class='letter-contact']").text
        letter_info['date'] = driver.find_element(By.CSS_SELECTOR, "div[class='letter__date']").text
        letter_info['full_text'] = driver.find_element(By.CSS_SELECTOR, "div[class='letter__body']").text

        letters.append(letter_info)
        print(f"Обработано {i+1}/{len(links)}")

    return letters


links = get_all_letter_links()
data = get_data(links[:50])

with my.connect_to_mongodb_collection(database_name='hw5', collection_name='letters', delete=False) as collection:
    my.data_insert(collection, data)

driver.close()
