"""LeetCode 101: kiểm tra cây nhị phân có đối xứng hay không."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass
class TreeNode:
    val: int = 0
    left: TreeNode | None = None
    right: TreeNode | None = None


def build_tree(values: list[int | None]) -> TreeNode | None:
    """Dựng cây từ danh sách theo thứ tự BFS kiểu LeetCode, None là node trống."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        for side in ("left", "right"):
            if i < len(values) and values[i] is not None:
                child = TreeNode(values[i])
                setattr(node, side, child)
                queue.append(child)
            i += 1
    return root


def is_symmetric(root: TreeNode | None) -> bool:
    """Bản đệ quy: cây đối xứng khi cây con trái là ảnh gương của cây con phải."""

    def mirror(a: TreeNode | None, b: TreeNode | None) -> bool:
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    return root is None or mirror(root.left, root.right)


def is_symmetric_iterative(root: TreeNode | None) -> bool:
    """Bản lặp: lấy từng cặp node phải đối xứng nhau ra khỏi hàng đợi và so sánh."""
    if root is None:
        return True
    queue = deque([(root.left, root.right)])
    while queue:
        a, b = queue.popleft()
        if a is None and b is None:
            continue
        if a is None or b is None or a.val != b.val:
            return False
        queue.append((a.left, b.right))
        queue.append((a.right, b.left))
    return True
