# Bài 04: Index cho CSDL

**Mục tiêu:** hiểu vì sao CSDL thật tìm được một dòng trong hàng triệu dòng gần như tức thì, bằng cách tự cài **index** cho thư viện `minidb` của bài 03 và đo thời gian trước/sau.

## Đề bài

### Phần 1: đo khi chưa có index

1. Ghi **1 000 000** sinh viên vào file `student.txt`, id từ 1 đến 1 000 000. Nên xáo trộn thứ tự id trong file: dữ liệu thật hiếm khi nằm sẵn theo thứ tự.
2. Tìm sinh viên có `id = 669416` bằng `DBQuery`.
3. Đo và in thời gian của từng bước: ghi file, đọc file, tìm.

### Phần 2: thêm index

1. Thêm method `create_index(table_name, column_name)`.
2. Cách làm: sắp xếp các giá trị của cột theo thứ tự tăng dần và lưu kèm vị trí dòng tương ứng. Khi tìm theo cột đó thì dùng **tìm nhị phân** thay vì duyệt cả bảng.
3. `where()` trên cột đã có index phải tự động dùng index, với `=`, `<`, `<=`, `>`, `>=`, `in`. Kết quả phải **giống hệt** khi không có index.
4. Sau `insert`, `update`, `delete` thì index vẫn phải đúng.
5. Đo lại thời gian tìm `id = 669416` và so sánh với phần 1.

### Phần mở rộng (không bắt buộc)

Index ở phần 2 nằm trong RAM, nên vẫn phải đọc cả file vào bộ nhớ trước. Hãy lưu index ra đĩa để tìm được một dòng mà **không cần đọc cả bảng**.

### Câu hỏi cần trả lời

- Độ phức tạp của tìm kiếm có và không có index?
- Đề gợi ý "cây nhị phân". Mảng đã sắp xếp cộng tìm nhị phân có phải là cây nhị phân không? Nếu tự cài cây nhị phân tìm kiếm (BST) bình thường và chèn id theo thứ tự 1, 2, 3, … thì chuyện gì xảy ra?
- Index có cái giá gì? Khi nào **không** nên đánh index?

## Lời giải

Code ở [solution/](solution/), giải thích và kết quả đo ở [SOLUTION.md](SOLUTION.md).

```bash
cd solution && python benchmark.py          # khoảng 5 giây, tạo ./bench_data (~48 MB)
pytest -q                                   # chạy từ thư mục bài 04
```
