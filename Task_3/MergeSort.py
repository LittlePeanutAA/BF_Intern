def merge_sort(array):
    """Hàm sắp xếp mảng bằng thuật toán Merge Sort."""
    if len(array) > 1:
        mid = len(array) // 2  # Tìm chỉ số giữa
        left_half = array[:mid]  # Tách mảng bên trái
        right_half = array[mid:]  # Tách mảng bên phải

        # Đệ quy sắp xếp hai nửa
        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0  # Khởi tạo chỉ số cho các mảng

        # So sánh và ghép mảng đã sắp xếp
        while i < len(left_half) and j < len(right_half):
            if left_half[i][0] < right_half[j][0]:
                array[k] = left_half[i]
                i += 1
            else:
                array[k] = right_half[j]
                j += 1
            k += 1

        # Nếu còn phần tử trong mảng bên trái
        while i < len(left_half):
            array[k] = left_half[i]
            i += 1
            k += 1

        # Nếu còn phần tử trong mảng bên phải
        while j < len(right_half):
            array[k] = right_half[j]
            j += 1
            k += 1
