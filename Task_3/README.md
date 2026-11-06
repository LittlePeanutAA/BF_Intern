# Task_3
## Thêm tính năng Indexing cho Database:
### Thử test trường hợp xử lý nhiều dữ liệu
 * Thử ghi 1 triệu sinh viên vào file, ID từ 1 đến 1.000.000
 * Thử tìm kiếm sinh viên có ID = 669.416
 * Đo và hiển thị thời gian thực thi
### Sử dụng index:
Thêm method: ```create_index(table_name, column_name)```
 * Tạo 1 index để khi tìm kiếm theo column này thì thay vì duyệt hết cả bảng thì dùng cơ chế Binary Tree (cây nhị phân) để tìm kiếm.
 * Để dùng cơ chế này thì ta cần sắp xếp lại các giá trị theo thứ tự tăng dần, và lưu lại index của nó. Khi tìm kiếm thì dùng thuật toán cây nhị phân để tìm.
 * Test lại thời gian tìm kiếm sinh viên có ID = 669.416 trong trường hợp có sử dụng index thì mất bao lâu.
