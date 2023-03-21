import undetected_chromedriver
import csv
import pickle
import time
from datetime import datetime
from auth_info import LOGIN, PASSWORD
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

t_date = datetime.now().strftime('%d_%m_%Y')

driver = undetected_chromedriver.Chrome()


def get_url():
    try:
        url = 'https://krisha.kz'
        driver.get(url=url)
    except TimeoutException as exception:
        print('ERROR 404')
        driver.quit()


def auth(login=LOGIN, password=PASSWORD):
    try:
        driver.find_element(By.CLASS_NAME, "cabinet-link-item").click()
        driver.implicitly_wait(10)
        login_input = driver.find_element(By.ID, "login")
        login_input.clear()
        login_input.send_keys(login)
        driver.implicitly_wait(10)
        login_input.send_keys(Keys.ENTER)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)
        driver.implicitly_wait(10)
        password_input.send_keys(Keys.ENTER)
        driver.find_element(By.CLASS_NAME, "logo-container").click()
        driver.implicitly_wait(10)
    except NoSuchElementException as exception:
        print("AUTH - Can't find element")
        get_url()


def get_links():
    current_day = t_date.split("_")[0]
    links_list = []

    try:
        driver.implicitly_wait(5)
        driver.get('https://krisha.kz/prodazha/kvartiry/astana/')
        driver.implicitly_wait(10)
        # find_button = driver.find_element(By.CLASS_NAME, "search-btn-main")
        # driver.implicitly_wait(10)
        # find_button.click()
        # driver.implicitly_wait(10)
        day = driver.find_element(By.CLASS_NAME, 'card-stats').text.split("\n")[1].split(" ")[0]
        count = 0
        # while int(day) ==int(current_day):
        while count <= 1:
            count += 1

            advertisements_list = driver.find_elements(By.CLASS_NAME, "a-card__inc")

            for advertisement in advertisements_list:
                seller = driver.find_element(By.CLASS_NAME, "a-card__owner-label").text
                print(seller)

                if seller == 'Хозяин недвижимости':

                    link = advertisement.find_element(By.CLASS_NAME, "a-card__image").get_attribute("href")

                    links_list.append(link)

            driver.find_element(By.CLASS_NAME, "paginator__btn--next").click()
            day = driver.find_element(By.CLASS_NAME, 'card-stats').text.split("\n")[1].split(" ")[0]

    except NoSuchElementException as exception:
        print("GET LINKS - Can't find element")

    finally:
        if links_list is not None:
            return links_list


def get_data():
    links_list = get_links()
    get_url()
    result = []

    for link in links_list:
        try:
            driver.get(url=str(link))
            pickle.dump(driver.get_cookies(), open(f"{t_date}_cookies", "wb"))

            for cookie in pickle.load(open(f"{t_date}_cookies", "rb")):
                driver.add_cookie(cookie)

            driver.refresh()
            # if link == links_list[0]:
            #     driver.find_element(By.CLASS_NAME, "kr-btn--gray-gradient").click()

            time.sleep(3)

            location = driver.find_element(By.XPATH, "/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[3]/span").text
            price = driver.find_element(By.CLASS_NAME, "offer__price").text
            # average_price_quarter_meter = driver.find_element(By.CLASS_NAME, "white-blue-price")
            href = str(link)

            time.sleep(1)

            driver.find_element(By.CLASS_NAME, "show-phones").click()
            driver.implicitly_wait(10)
            phone = driver.find_element(By.CLASS_NAME, "offer__contacts-phones").text

            pickle.dump(driver.get_cookies(), open(f"{t_date}_cookies", "wb"))

            for cookie in pickle.load(open(f"{t_date}_cookies", "rb")):
                driver.add_cookie(cookie)

            time.sleep(5)
        except NoSuchElementException or ElementNotInteractableException or StaleElementReferenceException as exception:
            print("Can't find element")
            phone = "empty"
            print(phone)
        finally:
            result.append([location, price, href, phone]) # NEED ADD AVG

    return result


def write_csv():
    result = get_data()

    with open(f'Result_{t_date}.csv', 'a', encoding='utf8') as file:
        writer = csv.writer(file)
        # NEED ADD AVG
        writer.writerow(
            (
                "Местонахождение",
                "Цена",
                "Ссылка",
                "Телефон",
            )
        )

        writer.writerows(result)


def main():
    get_url()
    # auth()
    write_csv()


if __name__ == '__main__':
    main()
