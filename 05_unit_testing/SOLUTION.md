# Lời giải bài 05

```
tests/
├── conftest.py     fixture: CSDL trong thư mục tạm + dữ liệu mẫu; trỏ import tới minidb của bài 03
├── test_query.py   from_, select, where, get, first, tính bất biến của truy vấn
└── test_write.py   insert, update, delete, lưu file, ghi lỗi giữa chừng, Database
```

Kết quả: **62 test, 100% dòng và 100% nhánh** của `minidb.py`, chạy trong khoảng 0,15 s.

```
Name         Stmts   Miss Branch BrPart  Cover
minidb.py      166      0     58      0   100%
62 passed in 0.14s
```

## 1. Fixture: mỗi test một CSDL mới

```python
@pytest.fixture
def db(tmp_path):            # tmp_path: pytest cấp cho mỗi test một thư mục tạm riêng
    database = Database(tmp_path)
    ...

@pytest.fixture
def q(db):                   # fixture dùng lại fixture khác
    query = DBQuery(db)
    for row in STUDENTS: query.insert("student", row)
    return query
```

Test nào cần dữ liệu mẫu thì chỉ cần khai báo tham số `q`. Mỗi test nhận một bản dữ liệu mới, nên:
- test A xoá dữ liệu không làm test B hỏng theo;
- chạy riêng một test, chạy ngược thứ tự hay chạy song song đều ra cùng kết quả.

Đây là điều kiện tiên quyết của unit test. Bản cũ gom mọi kiểm tra vào **một** hàm `test_query` dài gần 300 dòng, dùng chung dữ liệu đọc từ file `Class.txt` thật. Một `assert` hỏng làm dừng mọi kiểm tra phía sau, và kết quả phụ thuộc nội dung file lúc chạy.

Dữ liệu mẫu được chọn có chủ đích, mỗi chi tiết phục vụ một nhóm test:
- 4 sinh viên ở 2 lớp, để có nhiều dòng khớp và cả trường hợp không dòng nào khớp;
- 1 sinh viên có `gpa = None`, để test cách xử lý giống NULL;
- tên có dấu tiếng Việt, để test mã hoá UTF-8 khi ghi file.

## 2. Tham số hoá: một test, nhiều trường hợp

```python
@pytest.mark.parametrize("op, value, expected", [
    ("=", 2.5, [2]), ("!=", 2.5, [1, 3, 4]), ("<", 3.2, [2]), ...
])
def test_operators(self, q, op, value, expected): ...
```

Bảng tham số dễ đọc như một bảng đặc tả, và mỗi dòng chạy thành một test riêng (`test_operators[<-3.2-expected2]`). Nhờ vậy khi lỗi, ta biết ngay dòng nào sai. Thêm trường hợp mới chỉ cần thêm một dòng.

## 3. Chọn trường hợp cần test

Với mỗi method, lời giải đi qua ba câu hỏi:

| Câu hỏi | Ví dụ trong bộ test |
|---|---|
| Trường hợp bình thường có đúng không? | `test_updates_matching_rows_and_returns_count`: đúng các dòng bị sửa, trả đúng số dòng |
| Ở biên thì sao? | bảng rỗng, không dòng nào khớp, `where("id", "03")`, cột thiếu khi insert thành `None`, `gpa >= 0` với dòng `None` |
| Dùng sai thì sao? | 7 kiểu dòng không hợp lệ khi insert, update/delete thiếu `where`, toán tử lạ, cột lạ, file hỏng |

Mỗi test lỗi kiểm tra **hai** điều: có báo lỗi với thông báo đúng (`pytest.raises(..., match=...)`), và **dữ liệu không đổi**. Điều thứ hai hay bị bỏ quên. Ví dụ `test_invalid_value_changes_nothing`: update hai cột mà cột thứ hai sai kiểu thì cột thứ nhất cũng không được đổi.

Một số test kiểm tra tính chất của cả hệ thống chứ không của riêng method nào:
- `TestImmutability`: truy vấn dựng dở không làm hỏng truy vấn sau (đúng lỗi của bản cũ), gọi method theo thứ tự nào cũng được.
- `TestPersistence`: ghi xong, mở lại `Database` từ file thì phải ra đúng dữ liệu đó.
- `test_failed_write_keeps_old_file`: dùng `monkeypatch` thay `os.replace` bằng hàm ném lỗi "đĩa đầy", rồi kiểm tra file cũ còn nguyên và không sót file tạm. `monkeypatch` cho phép giả lập những lỗi rất khó tạo ra thật.

## 4. 100% coverage vẫn chưa đủ

Coverage chỉ cho biết dòng code **đã chạy** khi test, không cho biết test có **kiểm tra** kết quả hay không. Một test gọi `q.get()` mà không có `assert` nào vẫn làm tăng coverage.

Cách kiểm tra chất lượng test là **mutation testing**: cố ý cài lỗi vào code rồi xem test có phát hiện không. Với bộ test này:

| Lỗi cài vào `minidb.py` | Số test phát hiện |
|---|---|
| bỏ kiểm tra "update/delete phải có where" | 2 |
| so sánh `None` như số (NULL >= 0 thành True) | 5 |
| `where` thứ hai đè `where` thứ nhất thay vì AND (đúng lỗi của bản cũ) | 1 |
| ghi file xong lại làm rỗng file | 2 |

Cả 4 lỗi đều bị bắt. Có công cụ tự động hoá việc này, ví dụ `mutmut`: nó tự sinh hàng trăm biến thể lỗi và báo những biến thể nào lọt qua bộ test.

## 5. Quy ước đặt tên

Tên test là một câu mô tả hành vi, ví dụ `test_cannot_change_id_to_existing_one` hay `test_none_behaves_like_sql_null`. Khi test hỏng, đọc tên là biết hành vi nào bị vỡ mà chưa cần mở code. Test được nhóm theo class (`TestInsert`, `TestUpdate`…) để báo cáo dễ đọc.

## So với bản cũ

| Bản cũ | Bản mới |
|---|---|
| Một hàm test dài, dùng chung dữ liệu từ file thật, theo dõi tiến độ bằng `print` | 62 test độc lập, mỗi test một thư mục tạm |
| Chủ yếu test trường hợp bình thường | Bình thường + biên + lỗi, và kiểm tra dữ liệu không đổi khi lỗi |
| Không đo độ phủ | 100% dòng và nhánh, cộng mutation test thủ công |
