def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid][0] == target:
            return arr[mid][1]  # Trả về data tại vị tri mong muốn
        elif arr[mid][0] < target:
            low = mid + 1  # Tìm trong nửa bên phải
        else:
            high = mid - 1  # Tìm trong nửa bên trái

    return []  # Trả về rỗng nếu không tìm thấy


def binary_search_2(arr, target):
    low, high = 0, len(arr) - 1
    first_index = -1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid][0] == target:  # So sánh với số đầu tiên trong list
            first_index = mid
            high = mid - 1  # Tìm bên trái để tìm chỉ số đầu tiên
        elif arr[mid][0] < target:
            low = mid + 1
        else:
            high = mid - 1

    if first_index == -1:
        return []  # Nếu không tìm thấy, trả về danh sách rỗng

    # Lấy tất cả các dữ liệu có số đầu tiên giống nhau
    result = []
    while first_index < len(arr) and arr[first_index][0] == target:
        result.append(arr[first_index][1])  # Giả sử dữ liệu nằm ở vị trí thứ hai trong list
        first_index += 1

    return result
