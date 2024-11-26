import pytesseract
from PIL import Image
import io
import base64


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def solveCaptcha(captcha_element):
    # Lấy ảnh CAPTCHA
    captcha_img = captcha_element.screenshot_as_png

    # Chuyển đổi ảnh sang định dạng PIL
    image = Image.open(io.BytesIO(captcha_img))

    # Sử dụng pytesseract để đọc text
    captcha_text = pytesseract.image_to_string(image)

    return captcha_text.strip().replace(" ", "")
