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


def maxUniqueSplit(s):
    """
    Nhận vào một chuỗi s và trả về số lượng tối đa các chuỗi con duy nhất mà chuỗi này có thể được chia thành.
    Các chuỗi con phải liên tiếp và không được trùng lặp.
    :param s: str - chuỗi input
    :return: int - số lượng chuỗi con tối đa
    """

    def backtrack(start, seen):
        """
        Hàm đệ quy được sử dụng để tìm kiếm các chuỗi con duy nhất
        :param start: int - Điểm bắt đầu xét chuỗi con tiếp theo
        :param seen: set - chứa các chuỗi con đã được cắt để đảm bảo tính duy nhất
        :return: int
        """
        # Nếu đã đến cuối chuỗi, tất cả các chuỗi con đều duy nhất
        if start == len(s):
            return 0

        max_count = 0  # Lưu trữ số lượng chuỗi con tối đa từ điểm start

        for end in range(start + 1, len(s) + 1):  # Tạo tất cả các chuỗi con có thể
            substring = s[start:end]

            if substring not in seen:  # Kiểm tra nếu chuỗi con là duy nhất
                seen.add(substring)  # Thêm vào tập hợp các chuỗi đã thấy

                """
                Gọi đệ quy backtrack với chỉ số bắt đầu mới là end, 
                bắt đầu kiểm tra từ vị trí ngay sau chuỗi con hiện tại.
                Cộng thêm 1 vào kết quả của gọi đệ quy để thêm chuỗi con hiện tại vào số lượng đếm
                Cập nhật max_count với giá trị lớn nhất giữa giá trị hiện tại và kết quả mới.
                """
                max_count = max(max_count, 1 + backtrack(end, seen))

                # print(seen)

                """
                Sau khi đệ quy trở về, ta loại bỏ chuỗi con từ tập hợp seen để đảm bảo rằng
                trong các lần kiểm tra tiếp theo, chuỗi con này có thể được sử dụng lại.
                Đây là bước quay lui (backtracking)
                """
                seen.remove(substring)

        return max_count

    return backtrack(0, set())


# Ví dụ sử dụng
# s = "ababccc"
s = 'abcd'
print(maxUniqueSplit(s))  # Kết quả: 5
