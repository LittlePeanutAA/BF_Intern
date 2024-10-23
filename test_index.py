import time
import csv
from database import *
from BinarySearch import binary_search, binary_search_2


filename = 'OneMstudents.txt'

"""
Thử test trường hợp xử lý nhiều dữ liệu
Thử ghi 1 triệu sinh viên vào file, ID từ 1 đến 1.000.000
Thử tìm kiếm sinh viên có ID = 669.416
Đo và hiển thị thời gian thực thi
"""
start = time.time()
test_id_0 = 220701
with open(filename, 'r', encoding="utf-8") as file:
    reader = csv.reader(file, delimiter='|')
    _ = next(reader)  # Bỏ qua dòng header
    for row in reader:
        if int(row[0]) == test_id_0:
            print(f'Thong tin cua sinh vien co id = {test_id_0}: ', row)
            break

print(f'Thoi gian tim kiem thong thuong la: {time.time() - start} giay')


"""
Test index
"""


# Hàm đọc dữ liệu 1 triệu sinh viên từ file text được lưu từ task 2
def read_data(filename):
    data = []
    try:
        with open(filename, 'r', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter='|')
            _ = next(reader)  # Bỏ qua dòng header
            for row in reader:
                data.append(row)

    except FileNotFoundError:
        pass
    return data


# Đọc dữ liệu student và tạo database
student_data = read_data('OneMstudents.txt')
data = {'student': student_data}
dbQuery = DBQuery(data)


test_id = '669416'


# Tạo index cho cột id
dbQuery.create_index('student', 'id')
index_arr = dbQuery.indexes['id']

# Tìm kiếm giá trị id mong muốn
start = time.time()
result = binary_search(index_arr, test_id)
if result:
    print(f'Thong tin co id = {test_id} la {result} duoc tim kiem trong thoi gian {time.time() - start}')
else:
    print('Khong tim thay sinh vien co id = ', test_id)


test_class_id = '3'


# Tạo index cho cột class_id
dbQuery.create_index('student', 'class_id')
index_arr = dbQuery.indexes['class_id']

# Tìm kiếm giá trị id mong muốn
start = time.time()
result = binary_search_2(index_arr, test_class_id)
if result:
    print(f'Thong tin co lop co id = {test_class_id} duoc tim kiem trong thoi gian {time.time() - start}')
    for r in result[:20]:
        print(r)
else:
    print('Khong tim thay lop co id = ', test_class_id)


test_name = 'Bui Cong Duy'

# Tạo index cho cột name
dbQuery.create_index('student', 'name')
index_arr = dbQuery.indexes['name']

# Tìm kiếm giá trị id mong muốn
start = time.time()
result = binary_search_2(index_arr, test_name)
if result:
    print(f'Thong tin sinh vien co ten la {test_name} duoc tim kiem trong thoi gian {time.time() - start}')
    for r in result:
        print(r)
else:
    print('Khong tim thay sinh vien co ten ', test_name)
    