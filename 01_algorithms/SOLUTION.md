# Lời giải bài 01

Chạy test: `pytest -q`. Test gồm ví dụ của đề, các trường hợp biên, và phép đối chiếu với lời giải vét cạn trên dữ liệu ngẫu nhiên.

## 1. Symmetric Tree ([symmetric_tree.py](solution/symmetric_tree.py))

**Ý tưởng.** Một cây đối xứng khi cây con trái là ảnh gương của cây con phải. Hai cây `a` và `b` là ảnh gương của nhau khi:
- cả hai cùng rỗng, hoặc
- cùng giá trị gốc, `a.left` là gương của `b.right`, và `a.right` là gương của `b.left`.

Định nghĩa này tự nó đã là đệ quy, nên code chỉ cần viết lại đúng định nghĩa:

```python
def mirror(a, b):
    if a is None or b is None:
        return a is b            # True chỉ khi cả hai cùng None
    return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
```

`a is b` là cách viết gọn của "cả hai cùng None": đã biết ít nhất một bên là None, nên hai bên trùng nhau khi và chỉ khi cả hai đều None.

**Bản lặp.** Đưa các *cặp* node cần so sánh vào hàng đợi. Lấy ra từng cặp: nếu khác nhau thì trả `False`, ngược lại đẩy hai cặp con `(a.left, b.right)` và `(a.right, b.left)` vào. Bản lặp không bị giới hạn độ sâu đệ quy của Python (mặc định 1000), hữu ích khi cây bị lệch thành một đường dài.

**Độ phức tạp.** Thời gian O(n), vì mỗi node được thăm một lần. Bộ nhớ O(h) cho đệ quy (h là chiều cao cây) hoặc O(w) cho hàng đợi (w là bề rộng lớn nhất).

**Lỗi hay gặp.** Chỉ so sánh *giá trị* theo thứ tự duyệt (ví dụ duyệt inorder rồi kiểm tra đối xứng) là sai. Cây `[1, 2, 2, 2, None, 2]` có giá trị đối xứng nhưng hình dạng không đối xứng; test có trường hợp này.

## 2. Add Two Numbers ([add_two_numbers.py](solution/add_two_numbers.py))

**Ý tưởng.** Vì chữ số hàng đơn vị đứng đầu, duyệt danh sách từ đầu chính là cộng tay từ phải sang trái. Mỗi bước: `tổng = số nhớ + chữ số của l1 + chữ số của l2`, rồi `số nhớ, chữ số = divmod(tổng, 10)`.

Ba chi tiết làm code gọn:
1. **Node giả (`dummy`).** Kết quả được nối vào sau `dummy`, nên không phải viết riêng trường hợp "danh sách kết quả đang rỗng". Cuối cùng trả `dummy.next`.
2. **Điều kiện lặp `while l1 or l2 or carry`.** Một vòng lặp xử lý cả ba tình huống: hai danh sách dài khác nhau, và số nhớ còn sót lại ở cuối (`5 + 5 = 10` cần thêm node `1`).
3. **`divmod`** tính thương và số dư trong một lần gọi.

**Vì sao không đổi ra `int`?** Python có số nguyên vô hạn nên đổi ra `int` vẫn chạy được. Nhưng ở hầu hết ngôn ngữ khác, số 100 chữ số sẽ tràn kiểu số. Mục đích của bài là luyện thao tác danh sách liên kết.

**Độ phức tạp.** Thời gian O(max(m, n)), bộ nhớ O(1) ngoài danh sách kết quả.

## 3. Word Search ([word_search.py](solution/word_search.py))

**Ý tưởng.** Thử xuất phát từ mọi ô. Từ một ô, DFS sang 4 ô kề để khớp ký tự tiếp theo. Khi đi vào ngõ cụt thì **quay lui**: bỏ đánh dấu ô vừa đi qua để nhánh khác còn dùng được ô đó.

```python
board[r][c] = "#"        # đánh dấu đã dùng
found = any(dfs(...) for 4 hướng)
board[r][c] = word[i]    # quay lui: trả lại như cũ
```

Đánh dấu ngay trên `board` thay vì dùng một tập `visited` riêng giúp tiết kiệm bộ nhớ và chạy nhanh hơn. Đổi lại phải nhớ trả lưới về trạng thái cũ; test kiểm tra điều này.

**Cắt nhánh.** Trường hợp xấu nhất là lưới toàn `A` và từ là `AAA…AB`: mọi đường đi đều khớp gần hết rồi mới hỏng ở ký tự cuối, nên số đường đi tăng theo hàm mũ. Hai mẹo:
1. **Đếm ký tự trước.** Nếu lưới không đủ số lượng một ký tự nào đó trong từ thì trả `False` ngay, khỏi DFS.
2. **Bắt đầu từ đầu hiếm hơn.** Tìm `word` và tìm từ đảo ngược của nó cho cùng kết quả, vì đường đi có thể đi theo cả hai chiều. Nếu chữ đầu xuất hiện nhiều hơn chữ cuối thì đảo từ lại, để DFS xuất phát từ ít ô hơn và hỏng sớm hơn.

**Độ phức tạp.** Thời gian O(m·n·3^L): từ mỗi ô xuất phát, mỗi bước có tối đa 3 hướng mới (không quay lại ô vừa đi). Bộ nhớ O(L) cho ngăn xếp đệ quy, với L là độ dài từ.

## 4. Max Unique Split ([max_unique_split.py](solution/max_unique_split.py))

**Ý tưởng.** Chuỗi dài tối đa 16, nên có 2^15 cách đặt dao cắt: vét cạn được. Quay lui: tại vị trí `start`, thử mọi đoạn `s[start:end]` chưa dùng, thêm vào tập `seen`, đệ quy từ `end`, rồi xoá khỏi `seen` (quay lui).

**Cắt nhánh.** Từ vị trí `start` thì số đoạn tối đa còn đạt được là `len(seen) + (n - start)`, khi mỗi ký tự còn lại là một đoạn riêng. Nếu con số đó không vượt được kết quả tốt nhất đã có thì bỏ nhánh. Đây là kỹ thuật *branch and bound*: ước lượng cận trên của nhánh, rồi bỏ nhánh không thể tốt hơn.

**So với bản cũ.** Bản cũ trả kết quả qua giá trị trả về của đệ quy (`max(max_count, 1 + backtrack(...))`) và không cắt nhánh. Bản mới giữ `best` toàn cục bằng `nonlocal`, nhờ đó so được cận trên với `best` để cắt nhánh sớm.

**Kiểm chứng.** Test đối chiếu với lời giải vét cạn thử cả 2^(n−1) cách cắt, trên 300 chuỗi ngẫu nhiên.

**Độ phức tạp.** Xấu nhất O(2^n · n) (2^n cách cắt, mỗi lần cắt chuỗi con tốn O(n)). Trên thực tế cắt nhánh bỏ được phần lớn số nhánh.
