# Bài 10: Thu thập dữ liệu web và tự động hoá trình duyệt với Selenium

**Mục tiêu:** dùng Selenium điều khiển trình duyệt để lấy dữ liệu từ trang có phân trang, trang dựng bằng JavaScript, và điền form; lưu kết quả thành JSON có cấu trúc. Học thêm cách crawl **có trách nhiệm**: đọc `robots.txt`, giãn cách request, và dừng lại khi trang không cho phép bot.

## Chuẩn bị

- Python 3.10+, Google Chrome. Selenium từ 4.6 tự tải `chromedriver` khớp với Chrome, không cần cài driver riêng.
- `pip install -r requirements.txt`

## Phần A: danh sách sản phẩm (60 sản phẩm, ảnh, tên, giá)

Đề gốc: lấy 60 chai vang đầu tiên ở [wine-searcher.com/discover](https://www.wine-searcher.com/discover?sl-ctr=USA&sl-st=ANY&sl-sh=Y), mỗi chai gồm ảnh, tên, giá, lưu JSON.

1. Thử truy cập trang đích bằng `requests` và bằng Selenium. Bạn nhận được gì? Vì sao?
2. Nếu trang đích chặn bot, **không** tìm cách vượt qua (giả user-agent, giấu dấu hiệu tự động hoá, giải captcha). Giải thích vì sao, rồi làm bài trên [books.toscrape.com](https://books.toscrape.com/), trang được dựng riêng để luyện scraping.
3. Lấy **60 sản phẩm đầu tiên** (đi qua nhiều trang bằng nút "next"). Mỗi sản phẩm gồm: tên đầy đủ, giá (số) và đơn vị tiền, URL ảnh tuyệt đối, số sao, còn hàng hay không, URL trang sản phẩm.
4. Lưu ra `output/books.json`.

## Phần B: sản phẩm của 3 quốc gia đầu tiên trên Cryptorefills

[Cryptorefills](https://www.cryptorefills.com/) bán gift card, thanh toán bằng tiền mã hoá.

1. Lấy danh sách gift card của **3 quốc gia đầu tiên** (theo thứ tự chữ cái).
2. Với mỗi sản phẩm: quốc gia, danh mục, tên, mô tả, ảnh, phạm vi sử dụng ("May only be redeemable in…"), còn hàng hay không.
3. Với mỗi đồng coin (ít nhất BTC, ETH, USDT, USDC, LTC): danh sách mệnh giá và giá tương ứng bằng coin đó.
4. Lưu ra `output/cryptorefills.json`, ghi kèm thời điểm crawl.
5. Đề gốc còn yêu cầu **5 địa chỉ ví nhận tiền** cho mỗi coin và mỗi mạng (network). Giải thích các địa chỉ này được tạo ra thế nào, và vì sao **không** nên tự động lấy chúng. Không cần cài đặt phần này.

Gợi ý: trước khi bấm vào giao diện, xem `robots.txt`, `sitemap.xml`, và dữ liệu có cấu trúc (`<script type="application/ld+json">`) nhúng sẵn trong trang.

## Phần C: tự động điền form

Trên trang luyện tập [practice.expandtesting.com/register](https://practice.expandtesting.com/register):

1. Viết script tự điền form đăng ký với các bộ dữ liệu sai (bỏ trống, tên quá ngắn, tên sai ký tự, mật khẩu quá ngắn, nhập lại không khớp, tên đã tồn tại). Kiểm tra mỗi trường hợp hiện đúng thông báo lỗi.
2. Đăng ký một tài khoản hợp lệ, đăng nhập sai mật khẩu, đăng nhập đúng, đăng xuất. Kiểm tra sau khi đăng xuất không vào lại được trang cần đăng nhập.
3. In bảng kết quả: mỗi bước đúng hay sai so với mong đợi.

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md).

```bash
python solution/books.py            # A: khoảng 10 giây
python solution/cryptorefills.py    # B: khoảng 5 phút (giãn cách 1 giây theo robots.txt)
python solution/register_form.py    # C: khoảng 30 giây
pytest -q                           # chạy offline trên HTML mẫu
```

Thêm `--show` để xem trình duyệt chạy thay vì chạy ẩn.
