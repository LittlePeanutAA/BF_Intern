# Bài 06: Quản lý sinh viên trên MySQL

**Mục tiêu:** chuyển chương trình [bài 02](../02_student_cli/) từ lưu file text sang cơ sở dữ liệu quan hệ. Học thiết kế lược đồ, ràng buộc (khoá chính, khoá ngoại, `UNIQUE`, `CHECK`), truy vấn có tham số để chống SQL injection, và transaction.

## Chuẩn bị

Một MySQL 8 bất kỳ. Cách nhanh nhất là Docker:

```bash
docker compose up -d        # MySQL 8.4 ở cổng 3306, tự chạy schema.sql lần đầu
pip install -r requirements.txt
```

## Đề bài

Giữ nguyên **mọi lệnh và mọi yêu cầu kiểm tra dữ liệu** của bài 02 (`list_*`, `add_*`, `edit_*`, `remove_*` cho lớp, sinh viên, giáo viên), nhưng dữ liệu nằm trong MySQL.

1. **Lược đồ.** Viết `schema.sql` tạo 3 bảng. Chọn kiểu dữ liệu phù hợp (ngày sinh là `DATE`, không phải chuỗi). Đưa càng nhiều quy tắc của bài 02 vào **ràng buộc của cơ sở dữ liệu** càng tốt:
   - ID không trùng;
   - sinh viên phải thuộc một lớp có thật; giáo viên chỉ chủ nhiệm lớp có thật;
   - một lớp có tối đa một giáo viên chủ nhiệm;
   - không xoá được lớp còn sinh viên hoặc chủ nhiệm;
   - số điện thoại đúng định dạng.

   Quy tắc nào của bài 02 **không cần nữa** khi chuyển sang cơ sở dữ liệu? Vì sao?
2. **Truy vấn an toàn.** Mọi giá trị do người dùng nhập phải truyền qua tham số của driver, không được ghép chuỗi vào câu SQL. Viết test chứng minh tên lớp `x'); DROP TABLE students; --` được lưu nguyên văn mà không phá dữ liệu.
3. **Thông báo lỗi.** Khi MySQL từ chối một thao tác vì vi phạm ràng buộc, in thông báo dễ hiểu như bài 02 (ví dụ "lớp id=1 đã có chủ nhiệm"), không in traceback hay mã lỗi thô.
4. **Transaction.** Viết `import_txt.py` chuyển dữ liệu từ các file của bài 02 vào MySQL. Nếu một dòng bất kỳ sai thì **không dòng nào** được ghi.
5. **Cấu hình.** Thông tin kết nối lấy từ tham số dòng lệnh hoặc biến môi trường, không ghi cứng mật khẩu trong code.
6. **Test** cho các lệnh chính và các lỗi ở mục 1–4.

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md).

```bash
cd solution
python import_txt.py ../sample_data
python qlsv.py list_student --class_id 1
python qlsv.py --db mysql://user:pass@host:3306/qlsv list_class

# Test: phần không cần MySQL luôn chạy; phần tích hợp cần một database được phép XOÁ SẠCH
QLSV_TEST_DB_URL=mysql://root:Ff8jHrRZBgVYVFBx@127.0.0.1:3306/qlsv_test pytest -q   # chạy từ thư mục bài 06
```
