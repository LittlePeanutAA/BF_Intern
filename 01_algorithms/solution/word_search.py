"""LeetCode 79: tìm từ trên lưới ký tự bằng DFS + quay lui."""
from collections import Counter

VISITED = "#"  # ký tự không bao giờ xuất hiện trong đề (chỉ có chữ cái)


def exist(board: list[list[str]], word: str) -> bool:
    rows, cols = len(board), len(board[0])
    if len(word) > rows * cols:
        return False

    # Cắt nhánh 1: lưới không đủ ký tự cho từ thì khỏi tìm.
    available = Counter(ch for row in board for ch in row)
    if any(available[ch] < n for ch, n in Counter(word).items()):
        return False

    # Cắt nhánh 2: bắt đầu từ đầu hiếm hơn. Đảo từ không đổi kết quả
    # nhưng giảm mạnh số điểm xuất phát khi chữ đầu xuất hiện dày đặc.
    if available[word[0]] > available[word[-1]]:
        word = word[::-1]

    def dfs(r: int, c: int, i: int) -> bool:
        if board[r][c] != word[i]:
            return False
        if i == len(word) - 1:
            return True
        board[r][c] = VISITED  # đánh dấu tại chỗ, không cần tập visited riêng
        found = any(
            0 <= nr < rows and 0 <= nc < cols and dfs(nr, nc, i + 1)
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1))
        )
        board[r][c] = word[i]  # quay lui: trả lại ký tự cũ
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))
