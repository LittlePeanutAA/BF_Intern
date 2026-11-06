# BF_Intern

Bộ bài tập thực tập ở BF, đi từ lập trình Python cơ bản tới học máy và thị giác máy tính. Mỗi bài có:

- `README.md`: đề bài, viết lại cho rõ ràng;
- `solution/`: lời giải;
- `SOLUTION.md`: giải thích chi tiết, kết quả, và so sánh với bản làm trước đây;
- `tests/`: chạy bằng `pytest -q` trong thư mục của bài.

## Lộ trình

| Bài | Chủ đề | Học được |
|---|---|---|
| [01](01_algorithms/) | Luyện thuật toán | cây nhị phân, danh sách liên kết, quay lui |
| [02](02_student_cli/) | Quản lý sinh viên bằng dòng lệnh | `argparse`, đọc/ghi file an toàn, kiểm tra dữ liệu đầu vào |
| [03](03_query_builder/) | Tự viết thư viện truy vấn | OOP, method chaining, đối tượng bất biến |
| [04](04_indexing/) | Index cho cơ sở dữ liệu | tìm kiếm nhị phân, index trên đĩa, đo hiệu năng với 1 triệu dòng |
| [05](05_unit_testing/) | Unit test | fixture, parametrize, đo độ phủ nhánh, mutation testing |
| [06](06_mysql/) | Quản lý sinh viên trên MySQL | lược đồ và ràng buộc, chống SQL injection, transaction |
| [07](07_data_cleaning/) | Phân tích và làm sạch dữ liệu | pandas, gộp bảng, cơ chế và cách xử lý dữ liệu thiếu |
| [08](08_loan_prediction/) | Dự đoán khoản vay | pipeline scikit-learn, rò rỉ dữ liệu, đánh giá đúng cách |
| [09](09_skin_detection/) | Đọc và cài đặt lại một bài báo | đọc bài báo phản biện, tái lập kết quả, so sánh công bằng |
| [10](10_web_scraping/) | Thu thập dữ liệu web | Selenium, dữ liệu có cấu trúc, crawl có trách nhiệm |
| [11](11_wine_label_detection/) | Phát hiện nhãn rượu | object detection hai bước với YOLO, chia dữ liệu chống rò rỉ, API |

Các bài 02 → 03 → 04 → 05 → 06 xây tiếp trên cùng một chương trình quản lý sinh viên. Bài 07 → 08 là hai bài phân tích dữ liệu bảng. Bài 09 → 11 là thị giác máy tính và dữ liệu web.

## Chạy

Mỗi bài có `requirements.txt` riêng. Nên dùng một virtualenv cho mỗi bài:

```bash
cd 08_loan_prediction
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Một số bài cần thêm:
- **06:** một MySQL 8 (`docker compose up -d` trong thư mục bài).
- **09:** tải bộ dữ liệu Pratheepan (`python data/download.py`).
- **10:** Google Chrome.
- **11:** dữ liệu ảnh nội bộ và GPU để train. Phần test chạy được mà không cần cả hai.

## Lịch sử

Repo này gộp từ các repo cũ (`PythonExercise`, `Task_1`…`Task_10`). Code cũ không còn trong cây thư mục, nhưng vẫn nằm nguyên trong lịch sử git.
