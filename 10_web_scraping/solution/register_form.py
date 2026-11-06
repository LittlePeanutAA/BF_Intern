"""Phần C: tự động điền form đăng ký, kiểm tra thông báo lỗi, rồi đăng nhập và đăng xuất.

    python solution/register_form.py           # in bảng kết quả, chụp màn hình vào figures/
    python solution/register_form.py --show

Trang đích là practice.expandtesting.com: trang được dựng riêng cho người học kiểm thử tự động,
tài khoản tạo ra chỉ tồn tại trên trang luyện tập đó.
"""
import argparse
import secrets
from dataclasses import dataclass
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from browser import chrome

BASE = "https://practice.expandtesting.com"
FIG = Path(__file__).resolve().parents[1] / "figures"


@dataclass
class Case:
    name: str
    username: str
    password: str
    confirm: str
    expect_url: str
    expect_message: str


def submit_form(driver: WebDriver, url: str, fields: dict[str, str]) -> tuple[str, str]:
    """Mở trang, điền các ô theo id, gửi form bằng phím Enter; trả (URL sau khi gửi, nội dung thông báo)."""
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    *first, last = fields.items()
    for field_id, value in first:
        wait.until(EC.visibility_of_element_located((By.ID, field_id))).send_keys(value)
    # Gửi bằng Enter thay vì click nút: trên trang này quảng cáo hay che mất nút Submit,
    # click sẽ lỗi ElementClickInterceptedException
    driver.find_element(By.ID, last[0]).send_keys(last[1] + Keys.ENTER)
    wait.until(lambda d: d.current_url != url or d.find_elements(By.ID, "flash"))
    flash = wait.until(EC.visibility_of_element_located((By.ID, "flash")))
    # Bỏ ký tự "×" của nút đóng thông báo
    return driver.current_url, flash.text.replace("×", "").strip()


def register(driver: WebDriver, case: Case) -> tuple[str, str]:
    return submit_form(driver, f"{BASE}/register",
                       {"username": case.username, "password": case.password, "confirmPassword": case.confirm})


def login(driver: WebDriver, username: str, password: str) -> tuple[str, str]:
    return submit_form(driver, f"{BASE}/login", {"username": username, "password": password})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    username = f"bf-intern-{secrets.token_hex(4)}"  # chỉ được chữ thường, số và dấu gạch nối
    password = secrets.token_urlsafe(12)  # mật khẩu ngẫu nhiên, không lưu ở đâu cả
    cases = [
        Case("bỏ trống mọi ô", "", "", "", "/register", "All fields are required."),
        Case("tên quá ngắn", "ab", password, password, "/register", "Username must be at least 3 characters long."),
        Case("tên có ký tự không hợp lệ", "BF_Intern", password, password, "/register",
             "Invalid username. Usernames can only contain lowercase letters, numbers, and single hyphens, "
             "must be between 3 and 39 characters, and cannot start or end with a hyphen."),
        Case("mật khẩu quá ngắn", username, "abc", "abc", "/register", "Password must be at least 4 characters long."),
        Case("mật khẩu nhập lại không khớp", username, password, password + "x", "/register", "Passwords do not match."),
        Case("hợp lệ", username, password, password, "/login", "Successfully registered, you can log in now."),
        Case("tên đã tồn tại", username, password, password, "/register", "An error occurred during registration. Please try again."),
    ]

    FIG.mkdir(exist_ok=True)
    passed = 0
    with chrome(headless=not args.show) as driver:
        for case in cases:
            url, message = register(driver, case)
            ok = url.endswith(case.expect_url) and message == case.expect_message
            passed += ok
            print(f"{'OK ' if ok else 'SAI'} đăng ký {case.name:<30} -> {url.removeprefix(BASE):<10} {message!r}")

        url, message = login(driver, username, password + "x")
        ok = url.endswith("/login") and "invalid" in message.lower()
        passed += ok
        print(f"{'OK ' if ok else 'SAI'} đăng nhập sai mật khẩu{'':<17} -> {url.removeprefix(BASE):<10} {message!r}")

        url, message = login(driver, username, password)
        ok = url.endswith("/secure")
        passed += ok
        print(f"{'OK ' if ok else 'SAI'} đăng nhập đúng{'':<25} -> {url.removeprefix(BASE):<10} {message!r}")
        driver.save_screenshot(str(FIG / "form_secure_area.png"))

        driver.get(f"{BASE}/logout")
        WebDriverWait(driver, 15).until(EC.url_contains("/login"))
        driver.get(f"{BASE}/secure")  # sau khi đăng xuất, vào lại trang bảo mật phải bị đẩy về /login
        ok = "/login" in driver.current_url
        passed += ok
        print(f"{'OK ' if ok else 'SAI'} đăng xuất rồi vào /secure{'':<15} -> {driver.current_url.removeprefix(BASE)}")

    total = len(cases) + 3
    print(f"\n{passed}/{total} bước đúng như mong đợi")
    raise SystemExit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
