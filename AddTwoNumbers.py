"""
You are given two non-empty linked lists representing two non-negative integers.
The digits are stored in reverse order, and each of their nodes contains a single digit.
Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

Constraints:
    The number of nodes in each linked list is in the range [1, 100].
    0 <= Node.val <= 9
    It is guaranteed that the list represents a number that does not have leading zeros.
"""


def addTwoNumbers(number1, number2):
    """
    Mục đích là cộng 2 số nguyên âm có thể rất lớn (vượt quá biểu diễn)
    Các số được biểu diễn dưới dạng list các chữ số bắt đầu từ hàng đơn vị
    Thực hiện theo đúng nguyên tắc cộng 2 số có nhớ
    :param number1: list[int]
    :param number2: list[int]
    :return: list[int]
    """

    bonus = 0  # Nhớ của phép cộng
    resultNum = []
    length = max(len(number1), len(number2))

    for index in range(length):

        try:
            add2digit = number1[index] + number2[index] + bonus
        except:
            try:
                add2digit = number1[index] + bonus
            except:
                add2digit = number2[index] + bonus

        if add2digit > 9:   # Cộng có nhớ
            bonus = 1
            resultNum.append(add2digit - 10)
            if index == length - 1:     # Khi cộng đến số cuối mà vẫn còn nhớ
                resultNum.append(1)
                return resultNum
        else:               # Cộng không có nhớ
            bonus = 0
            resultNum.append(add2digit)

    return resultNum


l1 = [9, 9, 9, 9, 9, 9, 9]
l2 = [9, 9, 9, 9]
# Output: [8,9,9,9,0,0,0,1]
print(addTwoNumbers(l1, l2))
