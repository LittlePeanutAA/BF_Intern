"""Phần A: lấy 60 sản phẩm đầu tiên (ảnh, tên, giá) từ một trang danh sách có phân trang, lưu JSON.

    python solution/books.py                 # -> output/books.json
    python solution/books.py --limit 100 --show

Trang đích của đề gốc (wine-searcher.com) chặn mọi trình duyệt tự động bằng PerimeterX,
nên dùng books.toscrape.com: trang được dựng riêng để luyện scraping, cấu trúc giống một cửa hàng thật.
"""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from browser import chrome

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
OUT = Path(__file__).resolve().parents[1] / "output" / "books.json"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
CURRENCIES = {"£": "GBP", "$": "USD", "€": "EUR", "₫": "VND"}


def parse_price(text: str) -> tuple[float, str]:
    """'£51.77' -> (51.77, 'GBP'); '1.258.000 ₫' -> (1258000.0, 'VND').

    Dấu cuối cùng là dấu thập phân nếu sau nó có 1–2 chữ số; ngược lại mọi dấu đều là phân cách nghìn.
    """
    match = re.search(r"\d+(?:[.,]\d+)*", text)
    if not match:
        raise ValueError(f"Không đọc được giá: {text!r}")
    number = match.group()
    head, sep, tail = max(number.rpartition("."), number.rpartition(","), key=lambda p: len(p[0]))
    if sep and len(tail) <= 2:
        number = re.sub(r"[.,]", "", head) + "." + tail
    else:
        number = re.sub(r"[.,]", "", number)
    currency = next((code for sym, code in CURRENCIES.items() if sym in text), "")
    return float(number), currency


def parse_rating(class_attr: str) -> int | None:
    """'star-rating Three' -> 3."""
    return next((v for word, v in RATINGS.items() if word in class_attr.split()), None)


def scrape_page(driver: WebDriver) -> list[dict]:
    items = []
    for card in driver.find_elements(By.CSS_SELECTOR, "article.product_pod"):
        link = card.find_element(By.CSS_SELECTOR, "h3 a")
        price, currency = parse_price(card.find_element(By.CSS_SELECTOR, ".price_color").text)
        items.append({
            # Tên hiển thị bị cắt ("A Light in the ..."), tên đầy đủ nằm ở thuộc tính title
            "name": link.get_attribute("title"),
            "price": price,
            "currency": currency,
            # get_attribute("src") trả URL tuyệt đối dù HTML viết đường dẫn tương đối
            "image": card.find_element(By.CSS_SELECTOR, ".image_container img").get_attribute("src"),
            "rating": parse_rating(card.find_element(By.CSS_SELECTOR, ".star-rating").get_attribute("class")),
            "in_stock": "In stock" in card.find_element(By.CSS_SELECTOR, ".availability").text,
            "url": link.get_attribute("href"),
        })
    return items


def scrape(driver: WebDriver, start_url: str, limit: int, delay: float = 1.0) -> list[dict]:
    """Đi theo nút 'next' cho tới khi đủ `limit` sản phẩm hoặc hết trang."""
    items, url = [], start_url
    while url and len(items) < limit:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.product_pod")))
        items.extend(scrape_page(driver))
        print(f"  {url}: tổng {len(items)} sản phẩm")
        next_links = driver.find_elements(By.CSS_SELECTOR, "li.next a")
        url = urljoin(driver.current_url, next_links[0].get_attribute("href")) if next_links else None
        time.sleep(delay)  # lịch sự với máy chủ: không gửi request dồn dập
    return items[:limit]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--show", action="store_true", help="hiện cửa sổ Chrome thay vì chạy ẩn")
    args = parser.parse_args()
    with chrome(headless=not args.show) as driver:
        items = scrape(driver, START_URL, args.limit)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã lưu {len(items)} sản phẩm vào {OUT}")


if __name__ == "__main__":
    main()
