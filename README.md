# Task_2
## Tự viết thư viện Database:
Đóng gói lại các hàm làm việc đọc/ghi dữ liệu bằng cách viết các class sau và sử dụng nó ở trong chương trình QLSV đã viết ở Task 1.

### DBQuery: Có các method sau:
 * Get(): Trả về dữ liệu
 * Where(column_name, value): Set điều kiện cần lọc ví dụ dbQuery.where(‘id', 1)
 * Select([ array of column names ]): Truyền vào tên các cột cần lấy data
 * From( table_name): Chọn entity cần lấy dữ liệu
 * Insert(table_name, data): Thêm dữ liệu vào entity 
 * Update(table_name, data): Update dữ liệu (cần dùng hàm where() ở trên để set điều kiện)
 * Delete(table_name): Delete  (cần dùng hàm where() ở trên để set điều kiện)

### Ví dụ để lấy các Sinh viên thuộc class có ID = 1 sẽ gọi như sau:
```dbQuery.select([‘id',’name']).where(‘class_id', 1).from(‘student').get()```
