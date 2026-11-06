import time
import autoit

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


from EmailVerifCode import *
from solveCaptcha import solveCaptcha


class BadooRegistration(GmailVerificationCode):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.wait = None
        self.setupDriver()

    def setupDriver(self):
        """
        Khởi tạo driver với các options cần thiết
        :return:
        """
        self.driver = webdriver.Chrome()
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
        time.sleep(1)       # Đợi animation hoàn thành

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

    def handleCaptcha(self):
        max_attempts = 100  # Số lần thử tối đa
        attempt = 0

        while attempt < max_attempts:
            try:
                # Kiểm tra xem CAPTCHA có xuất hiện không
                try:
                    # Đợi ngắn (2 giây) để kiểm tra CAPTCHA có xuất hiện không
                    captcha = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "captcha__image"))
                    )
                except TimeoutException:
                    # Nếu không tìm thấy CAPTCHA, thoát vòng lặp
                    return True

                # Nếu tìm thấy CAPTCHA, xử lý nó
                captcha_input = self.driver.find_element(By.ID, "captcha")

                if captcha_input:
                    # Giải CAPTCHA
                    captcha_text = solveCaptcha(captcha)

                    # Nếu không đọc được Captcha thì bấm Reload
                    if not captcha:
                        self.waitAndClick(By.CLASS_NAME, "captcha__reload")
                        continue

                    # Nhập CAPTCHA
                    captcha_input.clear()
                    captcha_input.send_keys(captcha_text)

                    # Dừng khoảng chừng là 3s để t xem m nhập cái gì
                    time.sleep(3)

                    # Click nút xác nhận
                    self.waitAndClick(By.CSS_SELECTOR, '[type="submit"]')

                    # Đợi một chút để hệ thống xử lý
                    time.sleep(2)

                    attempt += 1
                    print(f"Thử lần {attempt}")

            except NoSuchElementException:
                print("Không tìm thấy element CAPTCHA, tiếp tục...")
                return True

            except Exception as e:
                print(f"Lỗi khi xử lý CAPTCHA: {str(e)}")
                attempt += 1

        print(f"Đã thử {max_attempts} lần nhưng không thành công")
        return False

    def registerAccount(self, info):
        """
        Thực hiện quá trình đăng ký
        :return:
        """
        try:
            # Truy cập vào trang đăng ký
            self.driver.get("https://badoo.com/signup")
            time.sleep(3)       # Đợi trang load

            print('Step 1: Chọn đăng ký bằng Email (Ở đây ta sử dụng Gmail)')
            # Chọn Tiếp tục với Email
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="email-login"]')

            print('Step 2: Điền email')
            # Điền Email
            self.waitAndSendKeys(By.CSS_SELECTOR, '[data-qa="text-field-input"]', info['email'])

            # Tiếp tục
            self.waitAndClick(By.CSS_SELECTOR, '[type="submit"]')

            # Kiểm tra và xử lý CAPTCHA nếu xuất hiện
            if self.handleCaptcha():
                print("Đã xử lý CAPTCHA thành công")
                # Tiếp tục
                try:
                    self.waitAndClick(By.CSS_SELECTOR, '[type="submit"]')
                except:
                    pass
            else:
                print("Không thể xử lý CAPTCHA")

            # Không muốn gửi lời mời về email
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="modal-action-cancel"]')

            print('Step 3: Điền mã xác thực')
            # Lấy mã xác thực
            time.sleep(10)
            verif_code = self.getVerificationCode('hi@badoo.com')
            print(verif_code)

            # Điền mã xác thực
            self.waitAndSendKeys(By.CSS_SELECTOR, '[data-qa="code-input"]', verif_code)

            # Tiếp tục
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="continue-button"]')

            # Kiểm tra và xử lý CAPTCHA nếu xuất hiện
            if self.handleCaptcha():
                print("Đã xử lý CAPTCHA thành công")
                try:
                    self.waitAndClick(By.CSS_SELECTOR, '[type="submit"]')
                except:
                    pass
            else:
                print("Không thể xử lý CAPTCHA")

            print('Step 4: ')
            time.sleep(10)      # Trang sẽ load một lúc
            # Chọn giới tính
            if info['sex'] == 'male':
                self.waitAndClick(By.ID, "gender-male")
            elif info['sex'] == 'female':
                self.waitAndClick(By.ID, "gender-female")
            else:
                pass

            # Điền tên
            self.waitAndSendKeys(By.ID, "signup-name", info['name'])

            # Điền ngày sinh
            self.waitAndSendKeys(By.ID, "signup-dob", info['dob'])

            # Tiếp tục
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="continue-button"]')

            print('Step 4.5: bước thêm 2 ảnh (mới có)')
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="registration-add-photos__cta"]')
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa-provider="gallery"]')
            # Đợi cho hộp thoại Windows hiện ra
            time.sleep(2)

            # Chọn nhiều file bằng cách nhập đường dẫn
            file_path = (r'"D:\Barefeets Intern\Task_9\registration_anhduy22072001@gmail.com.png"'
                         r'"D:\Barefeets Intern\Task_9\registration_user2@example.com.png"')

            # Điền đường dẫn vào ô File name
            autoit.control_set_text("Open", "Edit1", file_path)

            # Nhấn nút Open
            autoit.control_click("Open", "Button1")

            # Đợi tải ảnh
            time.sleep(5)

            # Chọn các ảnh vừa tải lên
            image_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-qa="multimedia-image"]')
            for button in image_buttons:
                button.click()
                time.sleep(1)  # đợi 1 giây giữa mỗi lần click để tránh lỗi

            # Tải ảnh
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="navbar-link"]')

            # Đợi tải ảnh
            time.sleep(5)

            # Tiếp tục
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="continue-button"]')

            print('Step 5: Chọn mục đích sử dụng app')
            # Mục đích
            if info['target'] == 'date':
                self.waitAndClick(By.CSS_SELECTOR, '[data-qa-tiw-option-type="date"]')
            elif info['target'] == 'chat':
                self.waitAndClick(By.CSS_SELECTOR, '[data-qa-tiw-option-type="chat"]')
            else:
                self.waitAndClick(By.CSS_SELECTOR, '[data-qa-tiw-option-type="serious"]')

            # Tiếp tục
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="continue-button"]')

            # Để sau
            # self.waitAndClick(By.XPATH, "//span[contains(@class, 'csms-button__text') and text()='Để sau']")
            buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-qa="button"]')
            buttons[1].click()

            print('Step 6: Chọn nơi ở')
            # Điền nơi ở
            self.waitAndSendKeys(By.CSS_SELECTOR, '[data-qa="location-input"]', info['location'])

            time.sleep(5)       # Đợi nó load

            # Chọn nơi ở
            suggested_locations = self.driver.find_elements(By.CSS_SELECTOR, '[data-qa="suggested-location"]')
            suggested_locations[0].click()

            # Tiếp tục
            self.waitAndClick(By.CSS_SELECTOR, '[data-qa="continue-button"]')

            """print('Step 7 ')
            time.sleep(5)
            # Không cảm ơn
            # self.waitAndClick(By.XPATH, "//span[contains(@class, 'csms-button__text') and text()='Không cảm ơn']")
            buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-qa="button"]')
            buttons[1].click()"""

        except Exception as e:
            print(f"Error during registration: {str(e)}")
            return False

        finally:
            # Chụp ảnh màn hình để debug
            self.driver.save_screenshot(f"registration_{info['email']}.png")

    def close(self):
        """
        Đóng trình duyệt
        :return:
        """
        if self.driver:
            self.driver.quit()


regis = BadooRegistration()
info = {
    'name': 'Bui Cong Duy',
    'dob': "07-22-2001",
    'email': "anhduy22072001@gmail.com",
    'sex': "male",
    'target': "chat",
    'location': "Thai Binh"
}
regis.registerAccount(info)
print("Đăng ký thanh công!")
regis.close()
