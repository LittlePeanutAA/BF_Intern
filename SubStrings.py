"""
Given a string s, return the maximum number of unique substrings that the given string can be split into.

You can split string s into any list of non-empty substrings,
where the concatenation of the substrings forms the original string.
However, you must split the substrings such that all of them are unique.

A substring is a contiguous sequence of characters within a string.

Constraints:
    1 <= s.length <= 16
    s contains only lower case English letters.
"""


def maxUniqueSplit(s: str) -> int:
    """

    :param s: str - chuỗi input
    :return: int - số lượng chuỗi con tối đa
    """
    def backtrack(start: int, seen: set) -> int:
        """

        :param start: int - Điểm bắt đầu xét chuỗi con tiếp theo
        :param seen: set - chứa các chuỗi con đã được cắt
        :return: int
        """
        # Nếu đã đến cuối chuỗi, tất cả các chuỗi con đều duy nhất
        if start == len(s):
            return 0

        max_count = 0
        for end in range(start + 1, len(s) + 1):  # Tạo tất cả các chuỗi con có thể

            substring = s[start:end]

            if substring not in seen:  # Kiểm tra nếu chuỗi con là duy nhất
                seen.add(substring)  # Thêm vào tập hợp các chuỗi đã thấy

                # Gọi đệ quy để tìm số lượng tối đa từ vị trí hiện tại
                max_count = max(max_count, 1 + backtrack(end, seen))
                # print(seen)
                seen.remove(substring)  # Quay lui

        return max_count

    return backtrack(0, set())


# Ví dụ sử dụng
s = "ababccc"
print(maxUniqueSplit(s))  # Kết quả: 5
