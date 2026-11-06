"""Test chạy offline: chỉ dùng HTML mẫu trong tests/fixtures, không gửi request nào ra Internet."""
import json
import shutil
from pathlib import Path

import pytest

from books import parse_price, parse_rating
from cryptorefills import parse_option, product_info, product_urls

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("text, expected", [
    ("£51.77", (51.77, "GBP")),
    ("$1,299.00", (1299.0, "USD")),
    ("484.000 ₫", (484000.0, "VND")),      # kiểu Việt Nam: dấu chấm phân cách nghìn
    ("1.258.000 ₫", (1258000.0, "VND")),
    ("1,234", (1234.0, "")),
    ("12", (12.0, "")),
])
def test_parse_price(text, expected):
    assert parse_price(text) == expected


def test_parse_price_rejects_text_without_number():
    with pytest.raises(ValueError):
        parse_price("Liên hệ")


def test_parse_rating():
    assert parse_rating("star-rating Three") == 3
    assert parse_rating("star-rating") is None


@pytest.mark.parametrize("text, expected", [
    ("800 Robux\n10.30 USDT", {"value": "800 Robux", "price": 10.3, "coin": "USDT"}),
    ("$$100\n0.00104567 BTC", {"value": "$$100", "price": 0.00104567, "coin": "BTC"}),
    ("1 month\n1,234.50 USDC", {"value": "1 month", "price": 1234.5, "coin": "USDC"}),
])
def test_parse_option(text, expected):
    assert parse_option(text) == expected


def test_parse_option_rejects_missing_price():
    with pytest.raises(ValueError):
        parse_option("800 Robux")


def test_product_urls_groups_gift_cards_by_country():
    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://www.cryptorefills.com/en/albania/gift_cards/roblox</loc></url>
      <url><loc>https://www.cryptorefills.com/en/aland_islands/gift_cards/netflix</loc></url>
      <url><loc>https://www.cryptorefills.com/en/albania/gift_cards/c%26a</loc></url>
      <url><loc>https://www.cryptorefills.com/en/albania/mobile_top_up/vodafone_credits</loc></url>
      <url><loc>https://www.cryptorefills.com/en/albania</loc></url>
      <url><loc>https://www.cryptorefills.com/de/albania/gift_cards/roblox</loc></url>
    </urlset>"""
    urls = product_urls(sitemap)
    assert list(urls) == ["aland_islands", "albania"]
    assert [u.rsplit("/", 1)[-1] for u in urls["albania"]] == ["c%26a", "roblox"]


def ld(obj: dict) -> str:
    return f'<script type="application/ld+json">{json.dumps(obj)}</script>'


def test_product_info_from_json_ld():
    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"item": {"name": "Albania"}}, {"item": {"name": "Games"}}, {"item": {"name": "Roblox"}}]}
    product = {"@type": "Product", "name": "Roblox gift card", "description": "Mô tả",
               "image": [{"url": "https://cdn.example/roblox.webp"}],
               "offers": {"availability": "https://schema.org/InStock",
                          "offers": [{"price": "24.99"}, {"price": "9.99"}]}}
    html = ld(breadcrumb) + ld(product) + "<p>May only be redeemable in Albania</p>"
    assert product_info(html) == {
        "country": "Albania", "category": "Games", "name": "Roblox", "title": "Roblox gift card",
        "description": "Mô tả", "image": "https://cdn.example/roblox.webp",
        "redeem_area": "May only be redeemable in Albania", "in_stock": True}


def test_product_info_out_of_stock_page_has_no_product_block():
    html = ld({"@type": "BreadcrumbList", "itemListElement": [{"item": {"name": "Albania"}}]}) + \
        '<meta name="description" content="Buy X with crypto">' + \
        '<meta property="og:image" content="https://cdn.example/x.png?a=1&amp;b=2">' + '<h1 class="t">X &amp; Co<!-- --> gift card</h1>'
    info = product_info(html)
    assert info["in_stock"] is False and info["description"] == "Buy X with crypto"
    assert info["title"] == "X & Co gift card" and info["image"] == "https://cdn.example/x.png?a=1&b=2"


@pytest.mark.skipif(shutil.which("google-chrome") is None and not Path(
    "/Applications/Google Chrome.app").exists(), reason="cần Chrome")
def test_books_scrape_page_on_local_file():
    from books import scrape_page
    from browser import chrome

    with chrome() as driver:
        driver.get((FIXTURES / "books_page.html").as_uri())
        items = scrape_page(driver)
    assert [i["name"] for i in items] == ["A Light in the Attic", "Tipping the Velvet"]
    assert items[0]["price"] == 51.77 and items[0]["rating"] == 3 and items[0]["image"].endswith(".jpg")
