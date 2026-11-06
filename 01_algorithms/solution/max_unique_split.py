"""LeetCode 1593: cắt chuỗi thành nhiều đoạn nhất sao cho các đoạn đôi một khác nhau."""


def max_unique_split(s: str) -> int:
    n = len(s)
    seen: set[str] = set()
    best = 0

    def backtrack(start: int) -> None:
        nonlocal best
        # Cắt nhánh: dù mỗi ký tự còn lại thành một đoạn riêng cũng không vượt được best.
        if len(seen) + (n - start) <= best:
            return
        if start == n:
            best = len(seen)
            return
        for end in range(start + 1, n + 1):
            piece = s[start:end]
            if piece in seen:
                continue
            seen.add(piece)
            backtrack(end)
            seen.remove(piece)

    backtrack(0)
    return best
