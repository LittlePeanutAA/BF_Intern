import sys
sys.setrecursionlimit(10000000)

"""
class Node:
    def __init__(self, value, data):
        self.value = value
        self.data = data
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value, data):
        if self.root is None:
            self.root = Node(value, data)
        else:
            self._insert(value, data, self.root)

    def _insert(self, value, data, node):
        if value < node.value:
            if node.left is None:
                node.left = Node(value, data)
            else:
                self._insert(value, data, node.left)
        else:
            if node.right is None:
                node.right = Node(value, data)
            else:
                self._insert(value, data, node.right)

    def search(self, value):
        return self._search(value, self.root)

    def _search(self, value, node):
        if node is None:
            return []
        elif value < node.value:
            return self._search(value, node.left)
        elif value > node.value:
            return self._search(value, node.right)
        else:
            result = [node.data]
            result.extend(self._search(value, node.left))
            result.extend(self._search(value, node.right))
            return result
"""


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert(value, self.root)

    def _insert(self, value, node):
        # print(value, node)
        if value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert(value, node.left)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert(value, node.right)

    def search(self, value):
        return self._search(value, self.root)

    def _search(self, value, node):
        if node is None:
            return []
        elif value < node.value:
            return self._search(value, node.left)
        elif value > node.value:
            return self._search(value, node.right)
        else:
            result = [node.value]
            result.extend(self._search(value, node.left))
            result.extend(self._search(value, node.right))
            return result
