# Lời giải bài 02

```
solution/
├── storage.py   đọc/ghi một bảng text: chỉ biết dòng, cột và ký tự '|'
├── school.py    nghiệp vụ: schema 3 bảng, kiểm tra dữ liệu, thêm/sửa/xoá
└── qlsv.py      CLI: phân tích tham số, in bảng, đổi lỗi thành thông báo
sample_data/     dữ liệu mẫu (tên và số điện thoại đều là giả)
tests/           20 test, chạy CLI thật trên bản sao của sample_data
```

## 1. Chia thành 3 tầng

Lỗi hay gặp ở bài này là viết mọi thứ trong một file: `if command == "add_class": mở file, đọc, kiểm tra, ghi`, rồi lặp lại gần như y hệt cho 12 lệnh. Lời giải tách ra 3 tầng, mỗi tầng chỉ làm một việc:

| Tầng | Biết gì | Không biết gì |
|---|---|---|
| `storage.py` | định dạng file `a\|b\|c` | sinh viên, lớp là gì |
| `school.py` | quy tắc nghiệp vụ (ID duy nhất, lớp phải tồn tại…) | dữ liệu đến từ dòng lệnh hay từ đâu |
| `qlsv.py` | tham số dòng lệnh, cách in bảng | dữ liệu được lưu thế nào |

Lợi ích thấy ngay ở các bài sau:
- Bài 03 thay phần đọc/ghi bằng thư viện `DBQuery`.
- Bài 06 chuyển sang MySQL. `qlsv.py` gần như không phải sửa.
- Có thể test `School` trực tiếp mà không cần chạy CLI.

## 2. Mô tả schema bằng dữ liệu thay vì if/else

Ba bảng có cột khác nhau nhưng thao tác giống nhau. Thay vì viết `add_class`, `add_student`, `add_teacher` riêng, mỗi bảng được mô tả bằng một `Entity` gồm danh sách `Column`. Mỗi cột có `kind` (`id`, `ref`, `date`, `phone`, `text`):

```python
"student": Entity("student", "Student.txt", (Column("id", "ID", "id"), *PERSON, Column("class_id", "Class ID", "ref"))),
```

Từ mô tả đó:
- `build_parser()` tự sinh 12 lệnh con và tham số của chúng.
- `normalize()` biết cách kiểm tra từng cột theo `kind`.
- `add`, `edit`, `remove` dùng chung cho cả 3 bảng.

Muốn thêm một cột mới (ví dụ email) thì chỉ cần thêm một dòng `Column`.

## 3. Kiểm tra dữ liệu

`normalize(column, value)` chạy trên mọi giá trị trước khi ghi:

| Kiểm tra | Vì sao |
|---|---|
| không chứa `\|` hay xuống dòng | `\|` và xuống dòng chính là ký tự phân cách của file; để lọt vào thì file hỏng |
| ID là số nguyên dương, chuẩn hoá `"007"` thành `"7"` | để `--class_id 07` và `7` cùng trỏ tới một lớp |
| ngày sinh qua `date.fromisoformat` | bắt được cả ngày không tồn tại như `2004-13-01` hay `2023-02-29`; regex chỉ bắt được sai định dạng |
| số điện thoại khớp `0\d{9}` | `fullmatch` để không lọt `0912345678abc` |

Ràng buộc giữa các bảng nằm trong `_check_references` và `remove`:
- Sinh viên phải thuộc một lớp đang tồn tại.
- Lớp chủ nhiệm của giáo viên phải tồn tại, và mỗi lớp chỉ có một chủ nhiệm.
- Không xoá được lớp còn sinh viên hoặc còn chủ nhiệm. Đây là cách CSDL thật xử lý khoá ngoại (`ON DELETE RESTRICT`).

Mọi kiểm tra đều chạy **trước** khi ghi file, nên khi có lỗi thì dữ liệu không đổi. Test `test_errors` kiểm tra điều này cho cả 12 tình huống lỗi.

## 4. Ghi file an toàn

Mở file với mode `"w"` sẽ xoá nội dung cũ ngay lập tức. Nếu chương trình chết giữa chừng (Ctrl+C, hết đĩa…) thì mất sạch dữ liệu. `write_table` làm theo 3 bước:
1. Ghi ra một file tạm trong cùng thư mục.
2. `os.replace(tmp, path)`: thao tác đổi tên này là **nguyên tử**, nên người khác chỉ thấy file cũ hoặc file mới, không bao giờ thấy file ghi dở.
3. Có lỗi thì xoá file tạm.

## 5. Hiển thị lỗi

`SchoolError` là lỗi do người dùng nhập sai. `main()` bắt lỗi này, in `Lỗi: ...` ra stderr và trả mã thoát 1. Lỗi lập trình thật (bug) vẫn hiện traceback để dễ sửa: không bắt `Exception` chung chung.

## 6. In bảng có tiếng Việt

Chữ tiếng Việt có thể lưu ở dạng *tổ hợp* (NFD): chữ "ễ" gồm "e" cộng hai dấu. Khi đó `len("ễ") == 3` dù trên màn hình chỉ chiếm một ô. `width()` bỏ qua các ký tự dấu (`unicodedata.combining`) để cột không bị lệch.

## So với bản cũ

| Bản cũ | Bản mới |
|---|---|
| Mỗi lệnh một đoạn code đọc, ghi riêng | Một bộ `add`, `edit`, `remove` dùng chung, sinh từ schema |
| Không kiểm tra trùng ID; `Class.txt` mẫu có hai dòng `1\|Lớp K54QC` | Kiểm tra trùng ID, kiểu dữ liệu và ràng buộc giữa các bảng |
| Ghi đè file trực tiếp | Ghi file tạm rồi đổi tên |
| Dữ liệu mẫu chứa số điện thoại thật | Dữ liệu mẫu giả |
| Không có test | 20 test |
