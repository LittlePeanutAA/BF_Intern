"""Phần B: lấy thông tin và giá theo từng đồng coin của mọi gift card ở 3 quốc gia đầu tiên trên Cryptorefills.

    python solution/cryptorefills.py                       # 3 nước đầu, 5 coin -> output/cryptorefills.json
    python solution/cryptorefills.py --countries 1 --coins BTC USDT --show

Cách làm:
1. Danh sách sản phẩm lấy từ sitemap.xml (robots.txt trỏ tới nó), không phải đoán URL hay bấm khắp trang.
2. Thông tin cố định (tên, mô tả, ảnh, quốc gia, danh mục) đọc từ JSON-LD (schema.org) nhúng sẵn trong trang:
   dữ liệu có cấu trúc, ổn định hơn nhiều so với CSS class của giao diện.
3. Giá theo coin chỉ có sau khi trình duyệt chạy JavaScript và người dùng chọn coin, nên phần này cần Selenium.
"""
import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from html import unescape
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from browser import chrome

SITE = "https://www.cryptorefills.com"
SITEMAP = f"{SITE}/sitemap/0.xml"
CRAWL_DELAY = 1.0  # robots.txt: "Crawl-delay: 1"
DEFAULT_COINS = ["BTC", "ETH", "USDT", "USDC", "LTC"]
OUT = Path(__file__).resolve().parents[1] / "output" / "cryptorefills.json"
PRODUCT_URL = re.compile(rf"^{re.escape(SITE)}/en/([^/]+)/gift_cards/([^/]+)$")


# ---------- Bước 1: danh sách sản phẩm ----------

def product_urls(sitemap_xml: str) -> dict[str, list[str]]:
    """{quốc gia: [URL gift card]} từ nội dung sitemap."""
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    by_country: dict[str, list[str]] = {}
    for loc in ET.fromstring(sitemap_xml).iterfind("sm:url/sm:loc", ns):
        match = PRODUCT_URL.match(loc.text.strip())
        if match:
            by_country.setdefault(match.group(1), []).append(loc.text.strip())
    return {country: sorted(urls) for country, urls in sorted(by_country.items())}


# ---------- Bước 2: thông tin cố định từ JSON-LD ----------

def json_ld(html: str) -> dict[str, dict]:
    """Các khối <script type="application/ld+json">, theo @type."""
    blocks = {}
    for raw in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        blocks[data.get("@type", "")] = data
    return blocks


def product_info(html: str) -> dict:
    blocks = json_ld(html)
    crumbs = [item["item"]["name"] for item in blocks.get("BreadcrumbList", {}).get("itemListElement", [])]
    product = blocks.get("Product", {})  # sản phẩm hết hàng không có khối Product
    images = product.get("image") or [{}]
    offers = product.get("offers", {})
    redeem = re.search(r"May only be redeemable in [^<\"\\]+", html)
    # Sản phẩm hết hàng không có khối Product: lấy tạm từ thẻ <h1> và các thẻ meta
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    meta = {k: unescape(v) for k, v in
            re.findall(r'<meta (?:name|property)="(description|og:image)" content="([^"]*)"', html)}
    return {
        "country": crumbs[0] if crumbs else None,
        "category": crumbs[1] if len(crumbs) > 1 else None,
        "name": crumbs[-1] if crumbs else None,
        "title": product.get("name") or (unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else None),
        "description": product.get("description") or meta.get("description"),
        "image": images[0].get("url") or meta.get("og:image"),
        "redeem_area": redeem.group().strip() if redeem else None,
        # Bỏ qua giá trong JSON-LD: trang ghi priceCurrency "USD" cho cả thẻ mệnh giá €75
        "in_stock": offers.get("availability", "").endswith("InStock"),
    }


# ---------- Bước 3: giá theo coin (cần trình duyệt) ----------

def parse_option(text: str) -> dict:
    """'800 Robux\\n10.30 USDT' -> {'value': '800 Robux', 'price': 10.3, 'coin': 'USDT'}."""
    value, _, price_line = text.strip().rpartition("\n")
    match = re.fullmatch(r"([\d.,]+)\s+(\S+)", price_line.strip())
    if not value or not match:
        raise ValueError(f"Không đọc được lựa chọn: {text!r}")
    return {"value": value.strip(), "price": float(match.group(1).replace(",", "")), "coin": match.group(2)}


def open_listbox(driver: WebDriver, label: str) -> list:
    """Bấm vào listbox (Headless UI) có aria-label cho trước và trả các lựa chọn của nó."""
    button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'button[aria-label="{label}"]')))
    driver.execute_script("arguments[0].click()", button)
    return WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '[role="option"]')))


def close_listbox(driver: WebDriver) -> None:
    # Escape phải gửi vào phần tử đang được focus (chính listbox). Gửi vào <body> thì listbox không nhận được.
    driver.switch_to.active_element.send_keys(Keys.ESCAPE)
    WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '[role="option"]')))


def price_button(driver: WebDriver) -> str:
    return driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Select Currency"]').text.strip()


def prices_for_coin(driver: WebDriver, coin: str) -> list[dict] | None:
    before = price_button(driver).split()[0]
    options = open_listbox(driver, "Select Currency")
    choice = next((o for o in options if o.text.split("\n")[0] == coin), None)
    if choice is None:
        close_listbox(driver)
        return None  # sản phẩm này không nhận coin đó
    choice.click()
    # Đổi coin thì trang gọi API lấy giá mới. Trong lúc chờ, giao diện hiện SỐ CŨ với ĐƠN VỊ MỚI
    # (ví dụ "114.88 BTC"), nên chờ đơn vị đổi là chưa đủ: phải chờ con số đổi.
    # Hai stablecoin (USDT, USDC) có thể trùng giá, nên chỉ chờ tối đa 3 giây.
    try:
        WebDriverWait(driver, 3, poll_frequency=0.2).until(
            lambda d: price_button(d).endswith(f" {coin}") and price_button(d).split()[0] != before)
    except TimeoutException:
        pass
    rows = [parse_option(o.text) for o in open_listbox(driver, "Select Product")]
    close_listbox(driver)
    if any(r["coin"] != coin for r in rows):
        raise ValueError(f"danh sách mệnh giá không phải giá {coin}: {rows}")
    return [{"value": r["value"], "price": r["price"]} for r in rows]


def scrape_product(driver: WebDriver, url: str, coins: list[str]) -> dict:
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    except TimeoutException:
        return {"url": url, "error": "trang không tải được"}
    info = {"url": url, **product_info(driver.page_source), "prices": {}}
    if not driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Select Currency"]'):
        info["in_stock"] = False  # hết hàng: trang không có ô chọn mệnh giá và coin
        return info
    custom = driver.find_elements(By.CSS_SELECTOR, 'input[placeholder*=" - "]')
    if custom:
        # Thẻ nạp số tiền tuỳ ý (ví dụ PayPal, Payz): không có danh sách mệnh giá, chỉ có khoảng cho phép
        info["custom_amount_range"] = custom[0].get_attribute("placeholder")
        return info
    for coin in coins:
        try:
            prices = prices_for_coin(driver, coin)
        except (TimeoutException, ValueError) as error:
            print(f"    bỏ qua {coin}: {type(error).__name__}")
            prices = None
        if prices is not None:
            info["prices"][coin] = prices
    return info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--countries", type=int, default=3, help="số quốc gia đầu tiên theo thứ tự chữ cái")
    parser.add_argument("--coins", nargs="+", default=DEFAULT_COINS)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    sitemap = requests.get(SITEMAP, timeout=60)
    sitemap.raise_for_status()
    countries = dict(list(product_urls(sitemap.text).items())[:args.countries])
    print({c: len(u) for c, u in countries.items()})

    result = {"scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "note": "Giá theo coin là giá ước tính tại thời điểm crawl, tính theo tỉ giá lúc đó.",
              "countries": {}}
    with chrome(headless=not args.show) as driver:
        for country, urls in countries.items():
            products = []
            for i, url in enumerate(urls, 1):
                started = time.monotonic()
                product = scrape_product(driver, url, args.coins)
                products.append(product)
                status = ("hết hàng" if not product.get("in_stock")
                          else f"nhập số tiền tự do {product['custom_amount_range']}" if "custom_amount_range" in product
                          else f"{len(product['prices'])} coin")
                print(f"  [{country} {i}/{len(urls)}] {unquote(url.rsplit('/', 1)[-1])}: {status}")
                time.sleep(max(0.0, CRAWL_DELAY - (time.monotonic() - started)))
            result["countries"][country] = products
            OUT.parent.mkdir(exist_ok=True)  # ghi sau mỗi nước: lỡ dừng giữa chừng vẫn giữ được phần đã lấy
            OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    total = sum(len(p) for p in result["countries"].values())
    print(f"Đã lưu {total} sản phẩm vào {OUT}")


if __name__ == "__main__":
    main()
