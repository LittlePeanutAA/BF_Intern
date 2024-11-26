import requests
import json
import os
import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Đường dẫn đến profile
user_data_dir = "C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data"
profile = "Profile 2"

# Đường dẫn lưu ảnh
save_dir = "D://Barefeets Intern//Task_10//wine_images"


class Wine:
    def __init__(self, user_data_dir=None, profile=None):
        self.driver = None
        self.wait = None
        self.signInDriver(user_data_dir, profile)

    def signInDriver(self, user_data_dir, profile):
        """
        Khởi tạo driver với các options cần thiết
        :return:
        """
        chrome_options = Options()
        if user_data_dir and profile:
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument(f"--profile-directory={profile}")

            # Đóng tất cả cửa sổ Chrome hiện tại
            os.system("taskkill /f /im chrome.exe")
            time.sleep(2)  # Đợi để đảm bảo Chrome đã đóng hoàn toàn

        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def waitAndClick(self, by, value):
        """
        Đợi và click vào element
        :param by: Phương thức tìm kiếm
        :param value: Giá trị tìm kiếm
        :return:
        """
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        element.click()
        time.sleep(1)  # Đợi animation hoàn thành

    def waitAndSendKeys(self, by, value, keys):
        """
        Đợi và điền thông tin vào element
        :param by: Phương thức tìm kiếm
        :param value: Giá trị tìm kiếm
        :param keys: Giá trị được điền
        :return:
        """
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        element.clear()
        element.send_keys(keys)
        time.sleep(0.5)

    @staticmethod
    def download_image(url, save_dir, name):
        # Tạo tên file
        filename = f"image_{name}.jpg"

        # Tạo đường dẫn lưu file
        save_path = os.path.join(save_dir, filename)

        # Tải và lưu ảnh
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return os.path.join('images', filename)  # Trả về relative path
        return None

    def getWineData(self, save_dir):
        try:
            # Điều hướng đến trang web
            time.sleep(random.randint(3, 5))
            self.driver.get("https://winecellar.vn/ruou-vang-trang/")
            print("Đã điều hướng thành công!")
            time.sleep(10)      # Dừng lại để load

            # Tắt quảng cáo nếu hiện
            try:
                self.waitAndClick(By.XPATH, '//*[@id="popmake-27453"]/button')
                print("Đã tắt quảng cáo")
            except:
                print("Không có quảng cáo")

            print('Tìm vị trí các thẻ sản phẩm ...')
            time.sleep(3)
            products = []
            # product_cards = self.driver.find_elements()
            # print(len(product_cards))

            # Truy xuất thông tin các sản phẩm
            for index in range(24):
                try:
                    card = self.driver.find_element(By.XPATH,
                                                    f'//*[@id="main"]/div/div[2]/div/div[4]/div[{index+1}]/div/div[2]')
                    # Thêm try-except cho từng element để tránh fail toàn bộ nếu 1 element lỗi
                    name = card.find_element(By.CLASS_NAME, 'title-wrapper').text.strip()
                    price = card.find_element(By.CLASS_NAME, 'price').text.strip()
                    image = (card.find_element(By.CLASS_NAME, 'wcl-product__img').find_element(By.TAG_NAME, 'img').get_attribute('src'))

                    # Validate data trước khi thêm vào list
                    if name and price and image:
                        # Tải ảnh về thiết bị
                        print('Tải ảnh ...')
                        local_url = self.download_image(image, save_dir, name)

                        product = {
                            'name': name,
                            'price': price,
                            'image_url': local_url
                        }

                        products.append(product)

                except Exception as e:
                    print(f"Error scraping product: {e}")
                    continue

            # Lưu data vào file JSON
            print('Lưu thông tin vào .json ...')
            with open('wines.json', 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")

    def close(self):
        """
        Đóng trình duyệt
        :return:
        """
        if self.driver:
            self.driver.quit()


getWine = Wine()  # user_data_dir, profile
getWine.getWineData(save_dir)
getWine.close()
