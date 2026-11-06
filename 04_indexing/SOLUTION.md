# Lời giải bài 04

```
solution/
├── minidb.py       minidb của bài 03 + lower_bound/upper_bound, SortedIndex, create_index, insert_many
├── disk_index.py   phần mở rộng: index lưu trên đĩa, tìm bằng seek
└── benchmark.py    sinh 1 triệu sinh viên, đo các bước
tests/              7 test: đối chiếu index với duyệt bảng, index sau khi sửa dữ liệu, index trên đĩa
```

## Kết quả đo

`python benchmark.py`, chạy trên Apple M5 với Python 3.12:

```
== 1,000,000 sinh viên, tìm id=669416
ghi file                              1.19 s   (48 MB)
đọc file vào RAM                   808.46 ms
tìm, không index (duyệt cả bảng)   223.94 ms   -> Nguyễn Văn Nam
create_index('student', 'id')      527.09 ms
tìm, có index (tìm nhị phân)          2.4 µs   nhanh hơn 95,153 lần
dựng index trên đĩa                804.71 ms
tìm bằng index trên đĩa              37.3 µs   (20 lần đọc index, không nạp bảng vào RAM)
```

Ba điều rút ra:

1. **Có index thì một lần tìm nhanh hơn khoảng 100 000 lần.** Duyệt bảng so sánh 1 000 000 dòng; tìm nhị phân chỉ cần log₂(1 000 000) ≈ 20 phép so sánh.
2. **Dựng index tốn 0,5 s**, gấp đôi một lần duyệt bảng. Vì vậy index chỉ đáng giá khi bảng được tìm **nhiều lần**. Nếu chỉ tìm đúng một lần thì duyệt bảng nhanh hơn.
3. **Với index trong RAM, thứ tốn nhiều nhất vẫn là đọc file (0,8 s).** Index trên đĩa bỏ được bước này: 20 lần đọc 16 byte, tổng cộng 37 µs.

## 1. Tìm nhị phân

Trên danh sách đã sắp xếp, `lower_bound(keys, x)` trả về vị trí đầu tiên có `keys[i] >= x`:

```python
lo, hi = 0, len(keys)
while lo < hi:               # bất biến: keys[< lo] < x  và  keys[>= hi] >= x
    mid = (lo + hi) // 2
    if keys[mid] < x: lo = mid + 1
    else:             hi = mid
return lo
```

Mỗi vòng lặp loại một nửa khoảng tìm kiếm, nên cần tối đa ⌈log₂ n⌉ vòng. Viết theo **bất biến** (comment ở dòng `while`) giúp tránh các lỗi kinh điển của tìm nhị phân: lặp vô hạn, lệch một đơn vị, sai khi có giá trị trùng.

`upper_bound` giống hệt, chỉ đổi `<` thành `<=`. Có hai hàm này thì mọi truy vấn đều quy về một đoạn liên tiếp trên mảng đã sắp xếp:

| Điều kiện | Đoạn trên mảng đã sắp xếp |
|---|---|
| `= v` | `[lower_bound(v), upper_bound(v))`, đúng cả khi có giá trị trùng (ví dụ `class_id`) |
| `< v` | `[0, lower_bound(v))` |
| `<= v` | `[0, upper_bound(v))` |
| `> v` | `[upper_bound(v), n)` |
| `>= v` | `[lower_bound(v), n)` |
| `in [a, b, c]` | gộp các đoạn `= a`, `= b`, `= c` |

Thư viện chuẩn có sẵn `bisect.bisect_left` và `bisect.bisect_right` (viết bằng C, nhanh hơn). Ở đây viết tay để thấy thuật toán; test `test_bounds_match_bisect` đối chiếu hai bên trên 500 trường hợp ngẫu nhiên.

## 2. SortedIndex và cách truy vấn dùng index

`SortedIndex` giữ hai danh sách song song: `keys` là các giá trị đã sắp xếp, `rows` là tham chiếu tới dòng tương ứng. Lưu thẳng tham chiếu tới dòng thay cho số thứ tự dòng, để xoá dòng khác không làm lệch vị trí.

Trong `_matching`, nếu một điều kiện `where` nằm trên cột có index thì:
1. Lấy tập ứng viên bằng tìm nhị phân, ví dụ `class_id = 7` cho khoảng 2 000 dòng thay vì 1 000 000.
2. Kiểm tra các điều kiện còn lại **chỉ trên tập ứng viên** đó.

Toán tử không dùng được index (`!=`) hoặc giá trị `None` thì quay về duyệt bảng. Cách xử lý này giống bộ tối ưu truy vấn của SQL, chỉ là đơn giản hơn nhiều.

**Giữ index đúng khi dữ liệu đổi.** Mỗi lần `insert`, `update`, `delete`, `Table.changed()` xoá index cũ, và lần truy vấn sau sẽ dựng lại. Cách này đơn giản và luôn đúng, đổi lại mỗi lần ghi sẽ làm lần đọc kế tiếp tốn O(n log n). CSDL thật cập nhật index tại chỗ với chi phí O(log n) bằng B-tree.

**Kiểm chứng.** `test_index_gives_same_results_as_scan` chạy khoảng 1 800 truy vấn ngẫu nhiên (6 toán tử × 2 cột × 150 giá trị, cộng 20 truy vấn `in`), một lần không index và một lần có index, rồi so kết quả. Đây là cách test tốt cho tối ưu hoá: bản nhanh phải cho ra đúng kết quả của bản chậm nhưng hiển nhiên đúng.

## 3. Index trên đĩa (phần mở rộng)

`disk_index.build` ghi file `student.id.idx` gồm các bản ghi **dài cố định 16 byte**: khoá int64 và vị trí byte của dòng trong `student.txt`, sắp xếp theo khoá. Vì độ dài cố định nên bản ghi thứ `i` nằm ở byte `16·i`. Tìm nhị phân chạy thẳng trên file bằng `seek` mà không cần nạp file vào RAM. Tìm được khoá thì `seek` tới đúng dòng trong `student.txt` và đọc một dòng.

Đây là ý tưởng nền của index trong MySQL và PostgreSQL. Khác biệt là chúng dùng **B-tree**: mỗi node là một trang 8–16 KB chứa hàng trăm khoá. Nhờ vậy cây 1 triệu khoá chỉ cao 3–4 tầng, tức 3–4 lần đọc đĩa thay vì 20.

## 4. Trả lời câu hỏi

**Độ phức tạp.**
- Không index: O(n) cho mỗi lần tìm.
- Có index: O(log n + k), với k là số dòng kết quả.
- Dựng index: O(n log n) vì phải sắp xếp. Bộ nhớ thêm: O(n).

**Mảng sắp xếp có phải cây nhị phân không?** Có, theo nghĩa *ngầm định*. Phần tử giữa mảng là gốc, nửa trái là cây con trái, nửa phải là cây con phải. Tìm nhị phân chính là đi từ gốc xuống lá của một **cây cân bằng hoàn hảo**, độ sâu luôn ⌈log₂ n⌉.

**BST tự cài và id chèn theo thứ tự.** Một BST thông thường (node có `left`/`right`, không tự cân bằng) chèn 1, 2, 3, … sẽ thành một "cây" chỉ toàn nhánh phải, thực chất là danh sách liên kết dài 1 000 000:
- Tìm kiếm thành O(n), chậm như duyệt bảng.
- Hàm đệ quy vượt giới hạn đệ quy của Python (1000) và văng `RecursionError`.

Mà id tăng dần chính là trường hợp phổ biến nhất ngoài thực tế. Muốn dùng cây thật thì phải là cây **tự cân bằng** (AVL, đỏ-đen) hoặc B-tree. Với dữ liệu không đổi thường xuyên, mảng sắp xếp cộng tìm nhị phân đơn giản hơn, tốn ít bộ nhớ hơn và nhanh hơn.

**Cái giá của index, và khi nào không nên dùng.**
- Tốn bộ nhớ: ở đây là hai danh sách 1 triệu phần tử.
- Tốn thời gian dựng và làm mọi thao tác ghi chậm đi.

Không nên đánh index khi:
- bảng nhỏ (duyệt vài trăm dòng đã đủ nhanh);
- bảng ghi nhiều hơn đọc;
- cột có rất ít giá trị khác nhau, ví dụ giới tính: điều kiện `= 'nữ'` vẫn trả về một nửa bảng, nên index không giảm được bao nhiêu việc.

## So với bản cũ

| Bản cũ | Bản mới |
|---|---|
| Tìm nhị phân trên danh sách id kiểu chuỗi | Cột có kiểu nên so sánh số đúng; có `lower_bound`/`upper_bound` cho cả giá trị trùng và truy vấn khoảng |
| Index tách rời `DBQuery`, phải gọi hàm tìm riêng | `where()` tự dùng index khi có, kết quả giống hệt khi không có |
| Index không cập nhật khi dữ liệu đổi | Tự dựng lại sau mỗi thao tác ghi |
| Có thêm `BinarySort`, `MergeSort` tự viết | Dùng `sorted` có sẵn (Timsort, O(n log n), ổn định); công sức dành cho phần index |
