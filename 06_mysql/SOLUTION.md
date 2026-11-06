# Lời giải bài 06

```
schema.sql              3 bảng và mọi ràng buộc
docker-compose.yml      MySQL 8.4 cho máy học viên
solution/school.py      kết nối, kiểm tra dữ liệu, thêm/sửa/xoá, đổi lỗi MySQL thành thông báo
solution/qlsv.py        CLI, cùng lệnh với bài 02
solution/import_txt.py  chuyển dữ liệu từ file text của bài 02, trong một transaction
tests/test_offline.py   không cần MySQL
tests/test_mysql.py     tích hợp, chạy khi có QLSV_TEST_DB_URL
```

## 1. Lược đồ: để cơ sở dữ liệu giữ các quy tắc

| Quy tắc của bài 02 | Bài 02 (Python) | Bài 06 (MySQL) |
|---|---|---|
| ID không trùng | đọc cả file, tìm trùng | `PRIMARY KEY` |
| Sinh viên thuộc lớp có thật | đọc `Class.txt`, so sánh | `FOREIGN KEY (class_id) REFERENCES classes (id)` |
| Mỗi lớp tối đa một chủ nhiệm | duyệt mọi giáo viên | `UNIQUE (head_of_class)`. `UNIQUE` cho phép nhiều `NULL`, nên nhiều giáo viên không chủ nhiệm vẫn hợp lệ |
| Không xoá lớp còn người | duyệt sinh viên, giáo viên | `ON DELETE RESTRICT` |
| Số điện thoại 10 số, bắt đầu bằng 0 | regex | regex trong Python **và** `CHECK (phone REGEXP '^0[0-9]{9}$')` |
| Ngày sinh hợp lệ | `date.fromisoformat` | `date.fromisoformat`, cột kiểu `DATE` |
| Không chứa `|` hoặc xuống dòng | bắt buộc | **bỏ** |
| Ghi file an toàn khi bị ngắt | file tạm + `os.replace` | **bỏ**: transaction đảm bảo |

**Vì sao chuyển quy tắc vào cơ sở dữ liệu tốt hơn:**
- **Đúng cả khi có nhiều người ghi cùng lúc.** Ở bài 02, hai lệnh `add_teacher` chạy song song đều có thể đọc thấy "lớp 1 chưa có chủ nhiệm", rồi cả hai cùng ghi. Ràng buộc `UNIQUE` được MySQL kiểm tra ngay lúc ghi, nên lệnh thứ hai chắc chắn bị từ chối.
- **Đúng với mọi chương trình ghi vào cơ sở dữ liệu,** không chỉ `qlsv.py`: script import, một trang web viết sau này, hay người gõ SQL tay (`test_check_constraint_is_last_line_of_defense`).
- **Nhanh hơn:** kiểm tra khoá ngoại dùng index, không phải đọc lại cả bảng.

Python vẫn kiểm tra định dạng (ngày, số điện thoại, ID dương) **trước** khi gửi lên, vì thông báo lỗi rõ hơn và không tốn một lượt gọi tới máy chủ. `CHECK` là lớp bảo vệ cuối.

**Hai quy tắc không cần nữa,** vì chúng là giới hạn của **định dạng file**, không phải của dữ liệu:
- Cấm `|`: ký tự đó chỉ phá file khi dùng làm dấu phân cách cột. Giờ tên lớp chứa `|` vẫn lưu đúng.
- Ghi file tạm rồi đổi tên: transaction của MySQL đã đảm bảo "ghi hết hoặc không ghi gì".

## 2. Truy vấn có tham số: chống SQL injection

```python
# SAI: ghép chuỗi. Tên lớp  x'); DROP TABLE students; --  sẽ thành một câu lệnh SQL
cur.execute(f"INSERT INTO classes VALUES ({id}, '{name}')")

# ĐÚNG: driver gửi giá trị tách khỏi câu lệnh, nên giá trị không bao giờ được hiểu là SQL
cur.execute("INSERT INTO classes (id, class_name) VALUES (%s, %s)", (id, name))
```

Tham số chỉ thay được **giá trị**, không thay được **tên bảng hay tên cột**. Vì vậy `school.py` có ghép tên bảng và tên cột vào câu SQL, nhưng chúng lấy từ `ENTITIES` do code định nghĩa, không bao giờ từ input người dùng. `edit` chỉ nhận các khoá có trong `ENTITIES`.

`test_sql_injection_is_stored_as_plain_text` thêm lớp có tên `x'); DROP TABLE students; --`, rồi kiểm tra bảng `students` vẫn còn đủ 4 dòng và tên lớp được lưu nguyên văn.

## 3. Đổi lỗi MySQL thành thông báo

`explain()` dựa vào **mã lỗi** của MySQL, không dựa vào việc so sánh nội dung chuỗi lỗi:

| Mã | Ý nghĩa | Thông báo |
|---|---|---|
| 1062 `DUP_ENTRY` | trùng khoá | "student id=3 đã tồn tại". Nếu tên ràng buộc là `one_head_per_class` thì "lớp id=1 đã có chủ nhiệm" |
| 1452 `NO_REFERENCED_ROW_2` | khoá ngoại trỏ tới dòng không tồn tại | "lớp id=99 không tồn tại" |
| 1451 `ROW_IS_REFERENCED_2` | xoá dòng đang được tham chiếu | "lớp id=1 còn sinh viên hoặc giáo viên chủ nhiệm" |
| 3819 `CHECK_CONSTRAINT_VIOLATED` | vi phạm `CHECK` | "dữ liệu vi phạm ràng buộc…" |

Đặt tên cho ràng buộc (`CONSTRAINT one_head_per_class UNIQUE ...`) giúp phân biệt hai lỗi trùng khác nhau trên cùng một bảng.

**Một cái bẫy:** mặc định, MySQL trả về số dòng **thực sự thay đổi** sau `UPDATE`. Sửa số điện thoại thành đúng số cũ sẽ trả 0, và code tưởng "không tìm thấy sinh viên". Kết nối bật cờ `CLIENT.FOUND_ROWS` để nhận số dòng **khớp điều kiện** (`test_edit_only_given_fields_and_unchanged_value_is_not_not_found`).

## 4. Transaction

- Mỗi lệnh `add`/`edit`/`remove` chạy trong một transaction (`School._transaction`): thành công thì `commit`, bất kỳ lỗi nào thì `rollback`.
- `import_txt.py` nạp **cả 3 file** trong một transaction duy nhất, theo thứ tự lớp → sinh viên → giáo viên (vì khoá ngoại). Một dòng sai ở `Student.txt` thì cả các lớp đã chèn trước đó cũng bị huỷ (`test_import_is_all_or_nothing`). Lỗi báo rõ file và số dòng.
- Sau mỗi lần đọc cũng `commit`. Ở mức cô lập mặc định của InnoDB (`REPEATABLE READ`), một transaction đọc mở mãi sẽ chỉ thấy ảnh chụp dữ liệu cũ.

## 5. Cấu hình

URL kết nối lấy theo thứ tự: tham số `--db`, biến môi trường `QLSV_DB_URL`, rồi giá trị mặc định cho Docker trên máy cá nhân. Không có mật khẩu thật nào trong code. Nếu không kết nối được, CLI in một dòng lỗi và thoát với mã 2.

## 6. Test

- `test_offline.py` (12 test): kiểm tra dữ liệu đầu vào, đổi mã lỗi thành thông báo, CLI khi không có MySQL. Dữ liệu sai bị từ chối **trước khi** chạm tới cơ sở dữ liệu.
- `test_mysql.py` (14 test): mỗi test tạo lại database từ `schema.sql` và nạp `sample_data`, rồi chạy CLI thật. Database trong `QLSV_TEST_DB_URL` bị **xoá sạch**, nên đừng trỏ nó vào dữ liệu thật.

## So với bản cũ

| Bản cũ (`SQLConnection.py`) | Bản mới |
|---|---|
| Không có file lược đồ: bảng phải tạo tay, không có khoá ngoại, `UNIQUE` hay `CHECK` | `schema.sql` chứa mọi ràng buộc, chạy lại được |
| Ghép giá trị vào SQL bằng f-string (`f"... WHERE id = {id}"`, `f"INSERT ... VALUES {data_tuple}"`), nên dính SQL injection | Mọi giá trị qua tham số `%s`, có test chứng minh |
| Lệnh `connect_sql` lưu mật khẩu dạng chữ thường vào `connection_info.json` (file này còn được commit vào git) | `--db` hoặc biến môi trường `QLSV_DB_URL`, không ghi mật khẩu ra file |
| Nhánh SQL bỏ qua toàn bộ phần kiểm tra dữ liệu của bài trước | Kiểm tra trong Python, và MySQL là lớp bảo vệ cuối |
| `edit_*` bắt buộc nhập lại mọi trường | Chỉ sửa trường được truyền |
| Lỗi MySQL hiện nguyên traceback | Thông báo dễ hiểu theo mã lỗi |
| Hai chế độ file text và SQL trộn trong một CLI (`--useSQL`) | Một backend; dữ liệu text cũ chuyển sang bằng `import_txt.py` |
| Không có test | 12 test offline, 14 test trên MySQL 8.4 thật |
