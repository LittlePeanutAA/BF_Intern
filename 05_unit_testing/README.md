# Bài 05: Unit test

**Mục tiêu:** viết bộ test tự động cho thư viện `DBQuery` của [bài 03](../03_query_builder/), học cách chọn trường hợp cần test, dùng fixture, tham số hoá test và đo độ phủ.

## Đề bài

Viết test cho **mọi method** của `DBQuery` (`from_`, `select`, `where`, `get`, `first`, `insert`, `update`, `delete`) và của `Database`. Mục tiêu là tìm được lỗi, không chỉ chứng minh code chạy được. Ví dụ test cho `insert`:

```python
status = db_query.insert("class", {"id": 1, "name": "Class 1"})
assert status == 1
assert db_query.where("id", 1).from_("class").select("id").get() == [{"id": 1}]
```

### Yêu cầu

1. Dùng `pytest`. Mỗi test **độc lập**: tự tạo dữ liệu trong thư mục tạm, không phụ thuộc thứ tự chạy, không đụng vào dữ liệu thật.
2. Với mỗi method, test đủ ba nhóm:
   - **trường hợp bình thường**: kết quả đúng, giá trị trả về đúng;
   - **trường hợp biên**: bảng rỗng, không dòng nào khớp, giá trị `None`, chuỗi số `"1"` thay cho số `1`…;
   - **trường hợp lỗi**: tham số sai phải báo lỗi rõ ràng, và **dữ liệu không bị đổi**.
3. Test cả những tính chất không nằm trong một method cụ thể:
   - truy vấn trước không ảnh hưởng truy vấn sau;
   - dữ liệu còn nguyên khi mở lại CSDL từ file;
   - ghi file lỗi giữa chừng không làm hỏng file cũ.
4. Đo **độ phủ** (coverage) bằng `pytest-cov`, đạt 100% dòng và nhánh, rồi giải thích vì sao 100% coverage vẫn **chưa đủ**.

## Lời giải

Test ở [tests/](tests/), giải thích ở [SOLUTION.md](SOLUTION.md). Code được test nằm ở `../03_query_builder/solution/minidb.py`, không chép sang bài này.

```bash
pip install pytest pytest-cov
pytest            # chạy từ thư mục bài 05, tự in báo cáo coverage
```
