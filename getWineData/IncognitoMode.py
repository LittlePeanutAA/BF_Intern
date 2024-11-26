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

# Thiết lập đường dẫn lưu
save_dir = "D://Barefeets Intern//Task_10//wine_images"

# Thiết lập Chrome options
chrome_options = Options()

# Thêm argument cho chế độ ẩn danh
chrome_options.add_argument("--incognito")

# Các thiết lập bảo mật và chống phát hiện automation
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--start-maximized')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                            ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# Thêm một số argument để tăng tính ẩn danh
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


def download_image(url, save_dir, name):
    """Hàm tải và lưu ảnh"""
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Tạo tên file hợp lệ từ tên sản phẩm
        valid_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = os.path.join(save_dir, f"{valid_name}.jpg")

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
    except Exception as e:
        print(f"Lỗi khi tải ảnh: {e}")
        return None


try:
    # Đóng tất cả cửa sổ Chrome hiện tại
    os.system("taskkill /f /im chrome.exe")
    time.sleep(2)  # Đợi để đảm bảo Chrome đã đóng hoàn toàn

    # Khởi tạo driver
    driver = webdriver.Chrome(options=chrome_options)

    # Thêm JavaScript để ngụy trang webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Thêm delay ngẫu nhiên trước khi truy cập
    time.sleep(random.uniform(3, 7))

    # Điều hướng đến trang web
    driver.get("https://www.wine-searcher.com/discover")
    print("Đã điều hướng thành công!")

    # Đợi và tìm các sản phẩm
    print('Tìm vị trí các thẻ sản phẩm ...')
    time.sleep(random.uniform(8, 12))  # Thời gian đợi ngẫu nhiên

    products = []
    # product_cards = WebDriverWait(driver, 20).until(
    #     EC.presence_of_all_elements_located((By.CLASS_NAME, "card"))
    # )

    product_cards = driver.find_element(By.CSS_SELECTOR, ".selection-list-widget > div:nth-child(15)")
    print(f"Đã tìm thấy {len(product_cards)} sản phẩm")

    # Truy xuất thông tin các sản phẩm
    for index, card in enumerate(product_cards, 1):
        try:
            # Thêm delay ngẫu nhiên giữa các lần truy xuất
            time.sleep(random.uniform(0.5, 1.5))

            name = WebDriverWait(card, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-info'))
            ).text.strip()

            price = WebDriverWait(card, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'price__integer-part'))
            ).text.strip()

            image = WebDriverWait(card, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'img_fluid'))
            ).get_attribute('src')

            print(f'Đang xử lý sản phẩm {index}/{len(product_cards)}: {name}')

            # Tải ảnh
            local_url = download_image(image, save_dir, name)

            if name and price and local_url:
                products.append({
                    'name': name,
                    'price': price,
                    'image_url': local_url
                })

        except Exception as e:
            print(f"Lỗi khi xử lý sản phẩm {index}: {e}")
            continue

    # Lưu data vào file JSON
    print('Lưu thông tin vào file JSON...')
    with open('wines.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu thành công {len(products)} sản phẩm")

except Exception as e:
    print(f"Lỗi chính: {e}")
