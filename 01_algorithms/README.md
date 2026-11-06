# Bài 01: Luyện thuật toán với Python

**Mục tiêu:** làm quen với các cấu trúc dữ liệu cơ bản (cây nhị phân, danh sách liên kết, ma trận, tập hợp) và hai kỹ thuật hay gặp là **đệ quy** và **quay lui (backtracking)**.

## Đề bài

Giải 4 bài LeetCode dưới đây. Với mỗi bài, viết một hàm đúng chữ ký đã cho, kèm test.

| # | Bài | Mức | Ý chính cần luyện |
|---|---|---|---|
| 1 | [101. Symmetric Tree](https://leetcode.com/problems/symmetric-tree/) | Easy | đệ quy trên cây, so sánh hai cây con |
| 2 | [2. Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | Medium | duyệt danh sách liên kết, xử lý số nhớ |
| 3 | [79. Word Search](https://leetcode.com/problems/word-search/) | Medium | DFS + quay lui trên lưới |
| 4 | [1593. Split a String Into the Max Number of Unique Substrings](https://leetcode.com/problems/split-a-string-into-the-max-number-of-unique-substrings/) | Medium | quay lui + cắt nhánh |

### 1. Symmetric Tree

Cho gốc `root` của một cây nhị phân, trả về `True` nếu cây đối xứng qua trục giữa (cây con trái là ảnh gương của cây con phải).

```
    1            1
   / \          / \
  2   2        2   2
 / \ / \        \   \
3  4 4  3        3   3
  True           False
```

Ràng buộc: 1 ≤ số node ≤ 1000, −100 ≤ giá trị ≤ 100. Làm thêm: viết cả bản đệ quy và bản lặp.

### 2. Add Two Numbers

Hai số nguyên không âm được lưu dưới dạng danh sách liên kết, **chữ số hàng đơn vị đứng đầu**, mỗi node chứa một chữ số. Trả về tổng của chúng, cũng ở dạng danh sách liên kết như vậy.

```
l1 = 2 → 4 → 3      (342)
l2 = 5 → 6 → 4      (465)
kết quả = 7 → 0 → 8 (807)
```

Ràng buộc: mỗi danh sách có 1 đến 100 node; số không có chữ số 0 ở đầu (trừ chính số 0). **Không được** đổi cả danh sách ra `int` rồi cộng: mục đích của bài là cộng từng chữ số và mang số nhớ.

### 3. Word Search

Cho lưới ký tự `board` kích thước m × n và một từ `word`. Trả về `True` nếu đi được từ đó qua các ô **kề nhau theo cạnh** (trên, dưới, trái, phải), mỗi ô dùng **tối đa một lần**.

```
A B C E
S F C S      "ABCCED" → True,  "SEE" → True,  "ABCB" → False
A D E E
```

Ràng buộc: 1 ≤ m, n ≤ 6, 1 ≤ len(word) ≤ 15, chỉ gồm chữ cái tiếng Anh. Làm thêm: cắt nhánh để chạy nhanh trên các trường hợp xấu (ví dụ lưới toàn `A`, từ là `AAAAAAAAAAAAAB`).

### 4. Split a String Into the Max Number of Unique Substrings

Cho chuỗi `s`. Cắt `s` thành các chuỗi con liên tiếp, khác rỗng, **đôi một khác nhau**, sao cho ghép lại vẫn ra `s`. Trả về số đoạn lớn nhất có thể.

```
"ababccc" → 5   (a | b | ab | c | cc)
"aba"     → 2   (a | ba)
"aa"      → 1
```

Ràng buộc: 1 ≤ len(s) ≤ 16, chỉ gồm chữ thường.

## Yêu cầu nộp

- Mỗi bài một file trong `solution/`, có type hint và docstring ngắn.
- Test bằng `pytest` trong `tests/`, gồm ví dụ của đề và các trường hợp biên.
- Ghi độ phức tạp thời gian và bộ nhớ của từng lời giải.

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md).

```bash
pip install pytest
pytest -q
```
