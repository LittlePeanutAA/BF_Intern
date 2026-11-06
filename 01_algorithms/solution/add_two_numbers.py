"""LeetCode 2: cộng hai số lưu ở danh sách liên kết, chữ số hàng đơn vị đứng đầu."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListNode:
    val: int = 0
    next: ListNode | None = None


def from_digits(digits: list[int]) -> ListNode | None:
    """[2, 4, 3] -> 2 -> 4 -> 3."""
    head = None
    for d in reversed(digits):
        head = ListNode(d, head)
    return head


def to_digits(node: ListNode | None) -> list[int]:
    out = []
    while node:
        out.append(node.val)
        node = node.next
    return out


def add_two_numbers(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    """Cộng từng cặp chữ số như cộng tay, mang số nhớ sang node kế tiếp."""
    dummy = ListNode()  # node giả để không phải xử lý riêng node đầu
    tail = dummy
    carry = 0
    while l1 or l2 or carry:
        total = carry
        if l1:
            total += l1.val
            l1 = l1.next
        if l2:
            total += l2.val
            l2 = l2.next
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
    return dummy.next
