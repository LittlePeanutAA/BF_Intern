"""
Given the root of a binary tree, check whether it is a mirror of itself
(i.e., symmetric around its center).

# Example usage:
# Construct a symmetric tree
#       1
#      / \
#     2   2
#    / \ / \
#   3  4 4  3

return: True
"""


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def isMirror(leftNode, rightNode):
    """
    Hàm nhận vào vào 2 nút
    Kiểm tra 2 nút
    Kiếm tra xem nút trái của hàm này so với nút phải của hàm còn lại
    Khi so sánh 2 cặp nút con, ta sử dụng đệ quy để so sánh tương tự 2 nút mẹ
    :param leftNode: TreeNode
    :param rightNode: TreeNode
    :return: bool
    """
    # Khi 2 nốt này không tồn tại thì 2 nốt này đối xứng
    if not leftNode and not rightNode:
        return True

    # Khi không tồn tại 1 trong 2 nốt thì 2 nốt này không đối xứng
    if not leftNode or not rightNode:
        return False

    # Khi 2 TH trên không xảy ra thì 2 nút đều tồn tại
    # Vì vậy ta check giá trị 2 nút và các nút con của nó
    if (leftNode.val == rightNode.val
            and isMirror(leftNode.left, rightNode.right)
            and isMirror(leftNode.right, rightNode.left)):
        return True


def isSymmetric(root):
    """
    Kiểm tra nốt gốc
    Sử dụng hàm đệ quy isMirror() để kiểm tra tuần tự các nốt trái phải
    :type root: Optional[TreeNode]
    :rtype: bool
    """
    # Không có gốc => Cây rỗng => Đối xứng
    if not root:
        return True

    # Bắt đầu check từ 2 nốt con của gốc:
    return isMirror(root.left, root.right)


# Test kết quả
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(2)
root.left.left = TreeNode(3)
root.left.right = TreeNode(4)
root.right.left = TreeNode(4)
root.right.right = TreeNode(3)

print(isSymmetric(root))
