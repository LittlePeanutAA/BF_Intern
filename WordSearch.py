"""
Given an m x n grid of characters board and a string word, return true if word exists in the grid.

The word can be constructed from letters of sequentially adjacent cells,
where adjacent cells are horizontally or vertically neighboring
The same letter cell may not be used more than once.

Constraints:
    m == board.length
    n = board[i].length
    1 <= m, n <= 6
    1 <= word.length <= 15
    board and word consists of only lowercase and uppercase English letters.
"""


def exist(board, word, road):
    """
    Tìm word trong bảng chữ cái board, sao cho đường nối chữ cái phải liên tục (4-neighbors)
    :param board: list[list[character]]
    :param word: str[character]
    :param road: đường đi được lưu lại
    :return: bool - Word exist in board?
    """
    rows, cols = len(board), len(board[0])

    def move(r, c, index):
        """
        Chọn hướng di chuyển, đúng hướng thì đi tiêp, sai đi lại cho đến khi hết bảng, hết từ
        :param r: Vị trí hàng hiện tại trong bảng
        :param c: Vị trí cột hiện tại trong bảng
        :param index: Vị trí của chữ cái đang xét trong từ
        :return: bool
        """

        # index được đánh từ 0 nên khi index = len(word) thì tức là đã duyệt qua hết các chữ cái
        if index == len(word):
            return True

        if (r < 0 or r >= rows  # Ngoài phạm vi số hàng
                or c < 0 or c >= cols  # Ngoài phạm vi số cột
                or board[r][c] != word[index]):  # Chữ cái không khớp
            return False

        # Đánh dấu ô này là đã sử dụng bằng cách thay đổi giá trị
        temp = board[r][c]  # Lưu trữ lại ông đang xét
        road.append([r, c])
        board[r][c] = '#'  # Đánh dấu ô đã sử dụng

        # Kiểm tra các ô kề (trên, dưới, trái, phải)
        found = (move(r + 1, c, index + 1) or  # Xuống dưới
                 move(r - 1, c, index + 1) or  # Lên trên
                 move(r, c + 1, index + 1) or  # Sang phải
                 move(r, c - 1, index + 1))  # Sang trái

        # Khi code chạy tiếp đến đây thì tức là tất cả các hướng được phát triển trong found đều sai
        # Nên ta cần khôi phục lại giá trị ô đã sử dụng và quay lại ô trước đó
        board[r][c] = temp
        if not found:
            road.pop(-1)

        return found

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == word[0]:  # Bắt đầu từ ký tự đầu tiên của từ
                if move(r, c, 0):
                    return True

    return False


# Test
# board = [
#     ['A', 'B', 'G', 'Y'],
#     ['S', 'A', 'B', 'S'],
#     ['A', 'Y', 'G', 'D']
# ]
# word = "ABGYA"     # Kết quả: True

board = [
    ['A', 'B', 'C', 'E'],
    ['S', 'F', 'C', 'S'],
    ['A', 'D', 'E', 'E']
]
word = "ABCCED"

road = []
if exist(board, word, road):
    print('Word ở vị trí: ', road)
    for x, y in road:
        board[x][y] = board[x][y].lower()
    for row in board:
        print(row)
else:
    print('Không tìm được word trong bảng.')
