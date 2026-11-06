"""Khởi tạo Chrome cho Selenium, dùng chung cho mọi script trong bài."""
from contextlib import contextmanager

from selenium import webdriver


@contextmanager
def chrome(headless: bool = True, width: int = 1366, height: int = 900):
    """Mở Chrome và luôn đóng lại, kể cả khi script lỗi giữa chừng.

    Selenium >= 4.6 tự tải chromedriver khớp với Chrome đã cài (Selenium Manager),
    nên không cần webdriver_manager hay tự tải driver.
    Không có tuỳ chọn nào để giả làm người dùng thật hay giấu dấu hiệu tự động hoá:
    trang nào chặn bot thì tôn trọng quyết định đó.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()
