# Bài 03: Tự viết thư viện truy vấn (OOP)

**Mục tiêu:** luyện lập trình hướng đối tượng bằng cách gói việc đọc/ghi dữ liệu của bài 02 thành một thư viện nhỏ có API giống SQL, rồi dùng lại nó trong chương trình quản lý sinh viên.

## Đề bài

Viết class `DBQuery` với các method sau:

| Method | Ý nghĩa | SQL tương ứng |
|---|---|---|
| `from_(table_name)` | chọn bảng (`from` là từ khoá của Python nên thêm `_`) | `FROM student` |
| `select(columns)` | chọn các cột cần lấy | `SELECT id, name` |
| `where(column, value)` | thêm điều kiện lọc; gọi nhiều lần thì nối bằng AND | `WHERE class_id = 1` |
| `get()` | chạy truy vấn, trả về danh sách bản ghi | |
| `insert(table_name, data)` | thêm một bản ghi | `INSERT INTO ...` |
| `update(table_name, data)` | sửa các bản ghi khớp `where()` | `UPDATE ... SET ... WHERE ...` |
| `delete(table_name)` | xoá các bản ghi khớp `where()` | `DELETE FROM ... WHERE ...` |

Ví dụ lấy id và tên của các sinh viên lớp 1:

```python
db_query.select(["id", "name"]).where("class_id", 1).from_("student").get()
# [{"id": 1, "name": "Nguyễn Văn An"}, {"id": 2, "name": "Trần Thị Bình"}]
```

### Yêu cầu

1. Các method dựng truy vấn (`from_`, `select`, `where`) gọi nối tiếp được theo **thứ tự bất kỳ**.
2. Mỗi bảng có kiểu cho từng cột, để `where("class_id", 1)` và `where("class_id", "1")` cho cùng kết quả.
3. `insert` từ chối id trùng và cột không tồn tại. `update` và `delete` **bắt buộc** có `where()`, để không lỡ tay sửa hoặc xoá cả bảng.
4. Truy vấn trước không được ảnh hưởng truy vấn sau (ví dụ điều kiện `where` của lần gọi trước không được "dính" sang lần sau).
5. Viết lại chương trình QLSV của bài 02 trên `DBQuery`, giữ nguyên các lệnh và mọi kiểm tra dữ liệu.

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md). Bộ test đầy đủ cho `DBQuery` nằm ở [bài 05](../05_unit_testing/).

```bash
cd solution && python qlsv.py --data-dir ../sample_data list_student --class_id 1
pytest -q          # chạy từ thư mục bài 03
```
