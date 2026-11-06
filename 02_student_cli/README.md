# Bài 02: Quản lý sinh viên bằng dòng lệnh

**Mục tiêu:** luyện điều kiện, vòng lặp, đọc/ghi file, và cách tổ chức một chương trình CLI nhỏ có kiểm tra dữ liệu đầu vào.

## Đề bài

Viết chương trình `qlsv.py` quản lý **lớp**, **sinh viên** và **giáo viên**. Dữ liệu lưu trong file text, mỗi lệnh là một lần chạy chương trình.

### Dữ liệu

| Thực thể | File | Cột |
|---|---|---|
| Lớp | `Class.txt` | `ID`, `Class Name` |
| Sinh viên | `Student.txt` | `ID`, `Name`, `Birthday`, `Phone Number`, `Class ID` |
| Giáo viên | `Teacher.txt` | `ID`, `Name`, `Birthday`, `Phone Number`, `Head Of Class` |

`Head Of Class` là ID của lớp mà giáo viên làm chủ nhiệm; để trống nếu không chủ nhiệm lớp nào.

Định dạng file:
- Dòng đầu là tên cột, các dòng sau là dữ liệu.
- Các cột ngăn cách bằng `|`. Ví dụ `Class.txt`:

```
ID|Class Name
1|K66CC
2|K66CD
```

### Lệnh

```bash
python qlsv.py list_class
python qlsv.py list_student [--class_id 1]
python qlsv.py list_teacher

python qlsv.py add_class    --id 1 --class_name "K66CC"
python qlsv.py edit_class   --id 1 --class_name "K66CA"
python qlsv.py remove_class --id 1

python qlsv.py add_student  --id 1 --name "Nguyễn Văn A" --birthday 2004-05-01 --phone 0912345678 --class_id 1
python qlsv.py edit_student --id 1 --phone 0987654321     # chỉ sửa trường được truyền vào
python qlsv.py remove_student --id 1

python qlsv.py add_teacher  --id 1 --name "Trần Thị B" --birthday 1985-02-03 --phone 0901234567 --head_of_class 1
python qlsv.py edit_teacher / remove_teacher               # tương tự sinh viên
```

### Yêu cầu

1. Đủ các lệnh ở trên. Sai cú pháp thì in hướng dẫn sử dụng.
2. **Kiểm tra dữ liệu.** Báo lỗi rõ ràng và trả mã thoát khác 0, không để chương trình văng traceback, khi:
   - ID bị trùng khi thêm, hoặc không tồn tại khi sửa/xoá;
   - ngày sinh không đúng dạng `YYYY-MM-DD`, số điện thoại không phải 10 chữ số bắt đầu bằng `0`;
   - giá trị chứa ký tự `|` hoặc xuống dòng (sẽ làm hỏng file);
   - sinh viên trỏ tới lớp không tồn tại, hoặc giáo viên chủ nhiệm lớp không tồn tại;
   - một lớp có hai giáo viên chủ nhiệm;
   - xoá lớp vẫn còn sinh viên hoặc giáo viên chủ nhiệm.
3. File chưa tồn tại thì coi như bảng rỗng. Ghi file sao cho nếu chương trình bị ngắt giữa chừng thì file cũ không bị hỏng.
4. Có test tự động cho các lệnh chính và các lỗi ở mục 2.

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md).

```bash
cd solution
python qlsv.py --data-dir ../sample_data list_student --class_id 1
pytest -q          # chạy từ thư mục bài 02
```
