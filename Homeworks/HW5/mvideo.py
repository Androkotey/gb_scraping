from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time

import my_functions as my
import re


def open_trends(driver, steps_down=3):
    """
    Нажимает на кнопку "В тренде"
    """

    time.sleep(5)
    for _ in range(steps_down):
        driver.find_element(By.CLASS_NAME, "popmechanic-desktop").send_keys(Keys.PAGE_DOWN)
    driver.find_element(By.CLASS_NAME, "popmechanic-desktop").send_keys(Keys.PAGE_UP)
    wait = WebDriverWait(driver, 10)
    try:
        button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "В тренде")]')))
        button.click()
    except TimeoutException:
        print("Не смог нажать на кнопку")
        exit()
    except ElementClickInterceptedException:
        print("Промазал")
        exit()
    time.sleep(1)


def get_data(driver):
    """
    Получает данные из карусели "В тренде"
    """

    carousel = driver.find_element(By.XPATH, '//*[@class="carusel ng-star-inserted"]')
    fields_to_get = ['name', 'price__main']

    products = []  # будет содержать два списка одинаковой длины
    for field in fields_to_get:
        product_field = carousel.find_elements(By.XPATH, f'.//*[contains(@class, "{field}")]')

        # Добавляет в список либо наименование, либо рубли
        products.append(list(map(
            lambda x: int(value) if (value := re.sub(r' (\d+) ₽', r'\1', x.text)).isdigit()
            else x.text,
            product_field
        )))

    return [{'name': name, 'price': price} for name, price in zip(*products)]


def main():
    my_driver = my.ConnectionToDriver(url='https://www.mvideo.ru/').driver
    open_trends(my_driver)
    data = get_data(my_driver)
    with my.connect_to_mongodb_collection(database_name='hw5', collection_name='goods', delete=False) as collection:
        my.data_insert(collection, data, index='name')
    my_driver.close()


if __name__ == '__main__':
    main()
