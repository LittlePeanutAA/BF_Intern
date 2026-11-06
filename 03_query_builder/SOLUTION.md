# Lời giải bài 03

```
solution/
├── minidb.py   thư viện: Table, Database, DBQuery
├── school.py   nghiệp vụ QLSV viết lại trên DBQuery
└── qlsv.py     CLI, gần như giữ nguyên từ bài 02
sample_data/    class.txt, student.txt, teacher.txt (có kiểu cột ở dòng đầu)
```

## 1. Ba class, ba trách nhiệm

| Class | Trách nhiệm |
|---|---|
| `Table` | giữ schema (tên cột và kiểu) cùng các dòng dữ liệu; đổi giá trị về đúng kiểu (`convert`) |
| `Database` | quản lý các bảng trong một thư mục: tạo bảng, đọc file khi dùng lần đầu, ghi file an toàn |
| `DBQuery` | dựng và chạy truy vấn; không đụng tới file |

Nhờ tách như vậy, bài 04 thêm index chỉ cần sửa `Table` và `DBQuery`, còn bài 06 thay `Database` bằng MySQL.

## 2. Định dạng file có kiểu

```
id:int|name:str|birthday:str|phone:str|class_id:int
1|Nguyễn Văn An|2004-03-12|0912000001|1
```

Bản cũ lưu mọi thứ dạng chuỗi rồi so sánh `row[i] == str(value)`. Hệ quả:
- `where("id", "01")` không khớp với `1`.
- Sắp xếp theo id ra thứ tự `1, 10, 2`, nên bài 04 (cần sắp xếp để tìm nhị phân) sẽ sai.

Khi ghi kiểu vào tiêu đề, `Table.convert` đưa mọi giá trị (đọc từ file, truyền vào `where`, `insert`, `update`) về cùng một kiểu. Ô rỗng là `None`, tương tự `NULL` trong SQL.

## 3. DBQuery bất biến (immutable)

Đây là quyết định thiết kế quan trọng nhất của bài. Bản cũ lưu điều kiện vào `self.filters` rồi tự xoá sau `get()`:

```python
q.where("class_id", 1)           # quên gọi get()
q.from_("teacher").get()         # điều kiện class_id=1 vẫn còn, lọc nhầm bảng teacher
```

Ở bản mới, `DBQuery` là `@dataclass(frozen=True)`. Mỗi method dựng truy vấn trả về **một đối tượng mới** bằng `dataclasses.replace`, còn đối tượng gốc không đổi:

```python
students = q.from_("student")              # q vẫn rỗng
class1 = students.where("class_id", 1)     # students vẫn không có điều kiện
class1.get(); class1.select("name").get()  # dùng lại thoải mái
```

Lợi ích:
- Không bao giờ có trạng thái sót lại từ truy vấn trước (yêu cầu 4).
- Gọi các method theo thứ tự bất kỳ đều được (yêu cầu 1).
- Một truy vấn dở dang có thể dùng làm "mẫu". `school.py` tận dụng điều này: `target = q.from_(entity).where("id", id_)`, sau đó `target.first()` để kiểm tra rồi `target.update(...)`.

SQLAlchemy, Django ORM và pandas đều dùng cách này.

## 4. Chặn lỗi "UPDATE/DELETE quên WHERE"

`update` và `delete` không có điều kiện sẽ báo `DBError`. Đây là lỗi kinh điển làm mất dữ liệu ngoài đời; MySQL cũng có chế độ `--safe-updates` cho đúng mục đích này. Muốn áp dụng cho cả bảng thì phải viết rõ ý định: `where("id", None, "!=")`.

## 5. Toán tử so sánh

`where(column, value, op="=")` hỗ trợ `= != < <= > >= in`. Mỗi toán tử được ánh xạ sang một hàm trong `operator` (`operator.eq`, `operator.lt`…) thay vì một chuỗi if/elif dài. Riêng `None` được xử lý như `NULL` của SQL: không lớn hơn, cũng không nhỏ hơn giá trị nào.

## 6. Dùng lại trong QLSV

`school.py` giữ nguyên API của bài 02 (`rows`, `add`, `edit`, `remove`), nên `qlsv.py` gần như không đổi. Phần kiểu dữ liệu chuyển hết sang `minidb`; `school.py` chỉ còn quy tắc nghiệp vụ (định dạng ngày sinh, số điện thoại, ràng buộc giữa các bảng). Bộ test của bài 02 chạy lại được trên bản này với vài sửa nhỏ (tên file, dòng tiêu đề), tổng cộng 21 test.

## So với bản cũ

| Bản cũ | Bản mới |
|---|---|
| Lọc chỉ được một điều kiện `where` (gọi lần hai thì đè lần một) | Nhiều `where`, nối bằng AND, có toán tử |
| Lưu trạng thái trong đối tượng, tự xoá sau `get()` | Bất biến, mỗi bước trả về truy vấn mới |
| Mọi giá trị là chuỗi | Cột có kiểu, chuyển đổi nhất quán |
| `update`/`delete` không có `where` thì áp dụng cho cả bảng | Báo lỗi |
| `insert` không kiểm tra cột hay id trùng | Có kiểm tra |
