def binary_search(arr, val, start, end):
    """Hàm tìm kiếm nhị phân để tìm vị trí chèn."""
    while start < end:
        mid = (start + end) // 2
        if arr[mid][0] < val:
            start = mid + 1
        else:
            end = mid
    return start


def binary_insertion_sort(array):
    """Sắp xếp mảng sử dụng thuật toán Insertion Sort với tìm kiếm nhị phân."""
    for i in range(1, len(array)):
        key = array[i]
        # Tìm vị trí chèn bằng tìm kiếm nhị phân
        position = binary_search(array, key[0], 0, i)

        # Di chuyển các phần tử để tạo chỗ cho key
        array = array[:position] + [key] + array[position:i] + array[i + 1:]

    return array
