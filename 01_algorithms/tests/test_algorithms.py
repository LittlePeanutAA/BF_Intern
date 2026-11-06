import itertools
import random
import time

import pytest

from solution.add_two_numbers import add_two_numbers, from_digits, to_digits
from solution.max_unique_split import max_unique_split
from solution.symmetric_tree import build_tree, is_symmetric, is_symmetric_iterative
from solution.word_search import exist


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 2, 3, 4, 4, 3], True),
    ([1, 2, 2, None, 3, None, 3], False),
    ([1], True),
    ([1, 2], False),
    ([1, 2, 2, 2, None, 2], False),   # cùng giá trị nhưng lệch hình dạng
    ([], True),
])
def test_symmetric(values, expected):
    root = build_tree(values)
    assert is_symmetric(root) is expected
    assert is_symmetric_iterative(root) is expected


@pytest.mark.parametrize("a, b, expected", [
    ([2, 4, 3], [5, 6, 4], [7, 0, 8]),
    ([0], [0], [0]),
    ([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9], [8, 9, 9, 9, 0, 0, 0, 1]),  # số nhớ ở cuối
    ([5], [5], [0, 1]),
])
def test_add_two_numbers(a, b, expected):
    assert to_digits(add_two_numbers(from_digits(a), from_digits(b))) == expected


def test_add_two_numbers_random():
    rng = random.Random(0)
    for _ in range(200):
        x, y = rng.randrange(10**30), rng.randrange(10**30)
        digits = lambda v: [int(d) for d in reversed(str(v))]
        assert to_digits(add_two_numbers(from_digits(digits(x)), from_digits(digits(y)))) == digits(x + y)


BOARD = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]


@pytest.mark.parametrize("word, expected", [
    ("ABCCED", True), ("SEE", True), ("ABCB", False), ("Z", False),
])
def test_word_search(word, expected):
    board = [row[:] for row in BOARD]
    assert exist(board, word) is expected
    assert board == BOARD  # hàm phải trả lưới về như cũ


def test_word_search_revisit_needs_backtracking():
    # Đường đi phải vòng qua ô E rồi quay lại: chỉ đúng khi quay lui trả ô về đúng chỗ.
    board = [["A", "B", "C", "E"], ["S", "F", "E", "S"], ["A", "D", "E", "E"]]
    assert exist(board, "ABCESEEEFS") is True


def test_word_search_worst_case_is_fast():
    board = [["A"] * 6 for _ in range(6)]
    start = time.perf_counter()
    assert exist(board, "A" * 14 + "B") is False
    assert exist(board, "B" + "A" * 14) is False
    assert time.perf_counter() - start < 0.5


def brute_force_split(s):
    """Thử mọi cách đặt dao cắt, chỉ dùng để đối chiếu với chuỗi ngắn."""
    best = 0
    for cuts in itertools.product([0, 1], repeat=len(s) - 1):
        pieces, start = [], 0
        for i, cut in enumerate(cuts, 1):
            if cut:
                pieces.append(s[start:i])
                start = i
        pieces.append(s[start:])
        if len(set(pieces)) == len(pieces):
            best = max(best, len(pieces))
    return best


@pytest.mark.parametrize("s, expected", [("ababccc", 5), ("aba", 2), ("aa", 1), ("a", 1)])
def test_max_unique_split(s, expected):
    assert max_unique_split(s) == expected


def test_max_unique_split_matches_brute_force():
    rng = random.Random(1)
    for _ in range(300):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 10)))
        assert max_unique_split(s) == brute_force_split(s)
