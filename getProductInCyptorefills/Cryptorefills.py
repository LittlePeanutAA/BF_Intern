import os
import json
import time
import urllib
import random
# import pandas as pd
from time import sleep
# from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from webdriver_manager.chrome import ChromeDriverManager


def setUpChrome():
    options = webdriver.ChromeOptions()

    options.add_argument('--headless')
    options.add_argument("--incognito")
    """options.add_argument("--nogpu")
    options.add_argument("--disable-gpu")
    options.add_argument('--disable-notifications')
    options.add_argument('--start-maximized')
    # options.add_argument("--window-size=1280,1280")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-javascript")
    options.add_argument("--disable-application-cache")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')

    # prx = random.choice(proxyList)
    # print(prx)
    # options.add_argument('--proxy-server={}'.format('117.4.50.142:32650'))

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(driver_version='131.0.6778.86').install()))"""
    driver = webdriver.Chrome(options=options)
    return driver


# 1. Setup Chrome Driver
driver = setUpChrome()

# 2. Đăng nhập tài khoản (Thử không đăng nhập nữa)
"""url = "https://www.cryptorefills.com/en/login"
driver.get(url)
# driver.implicitly_wait(20)
print(driver.title)

sleep(10)   # Load web
email = driver.find_element(By.ID,'email')
password = driver.find_element(By.ID,'password')

email.send_keys('user1@example.com')
password.send_keys('h9TxFSjAdSxYILu5')
sleep(10)

# Captcha "không phải robot"
driver.find_element(By.XPATH, '//div[@class= "recaptcha-checkbox-spinner"]').click()
sleep(2)        # Đợi thực hiện recaptcha
'''Captcha click in parts of image'''

# Nhấn nút Login
driver.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
sleep(10)"""


# 3. Truy cập vào các link sản phẩm để lấy thông tin
txt_file = open("country_list.txt", "r")
brand_names = txt_file.readlines()
len(brand_names)

JSON_DATA = {}

for brand_name in brand_names:
    brand_name = brand_name.rstrip()
    print(brand_name)

    driver.get(brand_name)

    # LẤY CÁC THÔNG TIN CƠ BẢN CỦA SẢN PHẨM
    INFO_DICT = {}
    # Lấy country và type, name
    try:
        # Locate đường dẫn "Country/Type/Name"
        nav = driver.find_element(By.XPATH, "//nav[@aria-label='Breadcrumb']")

        # Lấy text từ 3 thẻ li
        country = nav.find_element(By.XPATH, ".//li[1]//a").text
        product_type = nav.find_element(By.XPATH, ".//li[2]//a").text
        product_name = nav.find_element(By.XPATH, ".//li[3]").text

        INFO_DICT['type'] = product_type
        INFO_DICT['name'] = product_name

    except Exception as e:
        country = "Loi roi con dau"
        print(f"Error: {str(e)}")

    # Lấy title, delivery, area redeem và content
    try:
        info_box = driver.find_element(By.XPATH, '//*[contains(@class, "relative mt-5")]')

        # Lấy title: Mobile Legends gift card
        INFO_DICT['title'] = info_box.find_element(By.TAG_NAME, 'h1').text

        # Lấy delivery: Instant delivery
        INFO_DICT['delivery'] = info_box.find_element(
            "xpath",
            ".//div[contains(@class, 'flex flex-row items-center')]"
        ).text

        # Lấy area redeem: May only be redeemable in Vietnam
        INFO_DICT['area_redeem'] = info_box.find_element(By.XPATH, '//p[@class= "text-sm font-semibold"]').text

        # Lấy content: đoạn sớ dài loằng ngoằng dưới title
        INFO_DICT['content'] = info_box.find_element(By.XPATH, ".//*[contains(@class, 'text-base')]//p").text

    except Exception as e:
        print("Error getting content")
        print(e)

    # Lấy logo image
    try:
        INFO_DICT['img'] = driver.find_element(
            By.XPATH, "//*[contains(@class, 'md:sticky')]//img"
        ).get_attribute('src')

    except Exception as e:
        INFO_DICT['img'] = ''

    # print(INFO_DICT)

    # LẤY CÁC THÔNG TIN RIÊNG VỚI TỪNG LOẠI COIN
    # Ấn vào danh sách các coins
    def showCoinList():
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located(
            (By.XPATH,'//*[contains(@class, "relative mt-5")]//button[@aria-label= "Select Currency"]')
        ))
        payment = driver.find_element(
            By.XPATH,'//*[contains(@class, "relative mt-5")]//button[@aria-label= "Select Currency"]'
        )
        payment.click()

    showCoinList()      # Hiện danh sách các coins

    # Lấy danh sách các coins
    WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'relative cursor-pointer select-none')]"))
    )
    coins = driver.find_elements(By.XPATH, "//*[contains(@class, 'relative cursor-pointer select-none')]")

    # Số lượng loại coins thu thập thông tin
    coins_num = min(5, len(coins))

    """# Dictionary để lưu trữ element duy nhất dựa trên text
    unique_elements = {}

    for coin in coins:
        coin_name = coin.find_element(By.XPATH, ".//span[contains(@class, 'flex flex-row')]").text
        if coin_name not in unique_elements:
            unique_elements[coin_name] = coin

        # Dừng nếu đã có đủ 5 phần tử
        if len(unique_elements) == 5:
            break"""

    showCoinList()      # Đóng danh sách các coins

    # print(unique_elements)

    # for coin_name, coin_element in unique_elements.items():
    for idx in range(coins_num):
        showCoinList()  # Mở danh sách các coins
        sleep(1)

        coin_element = driver.find_elements(
            By.XPATH, "//*[contains(@class, 'relative cursor-pointer select-none')]"
        )[idx]    # Lấy coin theo thứ tự index

        coin_name = coin_element.find_element(By.XPATH, ".//span[contains(@class, 'flex flex-row')]").text

        # Chọn loại coin đang xét
        try:
            coin_element.click()
        except:
            # Cuộn đến phần tử đang xét
            driver.execute_script("arguments[0].scrollIntoView(true);", coin_element)
            # Đợi animation cuộn  và chọn
            time.sleep(0.5)
            coin_element.click()

        item_list = []      # Lưu trữ thông tin của loại coin hiện tại

        # Ấn vào danh sách các items
        def showItemList():
            WebDriverWait(driver, 3).until(EC.visibility_of_element_located(
                (By.XPATH, '//button[@aria-label="Select Product"]'))
            )
            show_items = driver.find_element(By.XPATH, '//button[@aria-label="Select Product"]')
            show_items.click()

        showItemList()  # Mở danh sách items

        # Xét item đầu tiên
        item_elements = driver.find_elements(   # Lấy danh sách các items
            By.XPATH, '//div//*[contains(@class, "relative cursor-pointer select")]'
        )
        amount = item_elements[0].find_element(By.XPATH, '//span//*[contains(@class, "whitespace")]').text
        item_elements[0].click()    # Chọn item đầu tiên
        estimated_price = driver.find_element(
            By.XPATH,
            '//button[@aria-label="Select Currency"]//span[contains(@class, "mr-12")]'
        ).text
        points = driver.find_element(By.XPATH, '//div//*[contains(@class, "flex mt-4")]').text

        item_list.append({
            "value": amount,
            "price": estimated_price,
            "point_plus": points
        })

        showItemList()  # Mở danh sách items

        # Xét item cuối cùng
        item_elements = driver.find_elements(   # Lấy danh sách các items
            By.XPATH, '//div//*[contains(@class, "relative cursor-pointer select")]'
        )
        try:
            # Thử click trực tiếp
            amount = item_elements[-1].find_element(By.XPATH, './/span//*[contains(@class, "whitespace")]').text
            item_elements[-1].click()

        except Exception as e:
            try:
                # Nếu không click được, cuộn xuống rồi click
                last_item = item_elements[-1]

                # Cuộn đến phần tử cuối
                driver.execute_script("arguments[0].scrollIntoView(true);", last_item)
                # Đợi animation cuộn
                time.sleep(0.5)

                # Thử lại việc lấy text và click
                amount = last_item.find_element(By.XPATH, './/span//*[contains(@class, "whitespace")]').text
                last_item.click()

            except Exception as e:
                print(f"Error after scrolling: {str(e)}")

        estimated_price = driver.find_element(
            By.XPATH,
            '//button[@aria-label="Select Currency"]//span[contains(@class, "mr-12")]'
        ).text
        points = driver.find_element(By.XPATH, '//div//*[contains(@class, "flex mt-4")]').text

        item_list.append({
            "value": amount,
            "price": estimated_price,
            "point_plus": points
        })

        # Ấn nút Buy now
        driver.find_element(By.XPATH, '//button[contains(text(), "Buy now")]').click()
        sleep(3)

        # Mục Contact details sẽ xuất hiện ở lần đầu tiên bấm Buy now (tức là idx=0)
        contact_details = driver.find_elements(By.XPATH, "//div[@id='contactInformationFrom']")
        if contact_details:  # Nếu list không rỗng (tức là tìm thấy element)
            # Nhập email
            email_input = driver.find_element(By.XPATH, '//input[@id= "email"]')
            email_input.clear()
            email_input.send_keys(INFO_DICT['name']+'@gmail.com')
            # Nhấn "I declare ..."
            driver.find_elements(By.XPATH, '//div[contains(@class, "justify-center rounded-md")]')[0].click()
            # Nhấn Continue
            driver.find_element(By.XPATH, '//button[@type= "submit"]').click()
            sleep(3)

        # Ấn nút Continue to payment
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '//button[contains(text(), "Continue to payment")]'))
        )
        continue_to_pay = driver.find_element(By.XPATH, '//button[contains(text(), "Continue to payment")]')
        continue_to_pay.click()

        # Chụp lại ảnh
        driver.save_screenshot("anh_loi.png")

        # Lấy wallet address
        #   Đợi cho wallet xuất hiện và scroll đến nó
        wallet_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//p[contains(@class, "text-base text")]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", wallet_element)
        time.sleep(1)   # Thêm delay nhỏ để đảm bảo scroll hoàn tất

        #   Lấy thông tin
        wallet_addr = driver.find_element(By.XPATH, '//p[contains(@class, "text-base text")]').text
        network = driver.find_element(By.XPATH, '//span[@class="ml-8"]').text

        # Lưu thông tin về items và wallet address
        INFO_DICT[coin_name] = {'items': item_list,
                                'wallet_address': {network: wallet_addr}}

        # Quay lại trang ban đầu của sản phẩm
        driver.back()

        if idx == coins_num - 1:    # Nếu là lần cuối thì cần phải xoá giỏ hàng, tối đa 10 products
            wallet_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//button[@class="border-0 transition"]'))
            )
            driver.find_element(By.XPATH, '//button[@class="border-0 transition"]').click()

        driver.back()
        wait = WebDriverWait(driver, 5)    # Đợi cho trang load xong

    # Lưu lại thông tin về sản phầm của quốc gia đang xét
    JSON_DATA[country] = INFO_DICT

    print(f'{country} done!')


# Lưu data vào file JSON
print('Lưu thông tin vào .json ...')
with open('sample.json', 'w', encoding='utf-8') as f:
    json.dump(JSON_DATA, f, ensure_ascii=False, indent=2)
