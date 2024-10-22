import time
import csv
from database import *


test_id = 669416
filename = 'OneMstudents.txt'

"""
Thử test trường hợp xử lý nhiều dữ liệu
Thử ghi 1 triệu sinh viên vào file, ID từ 1 đến 1.000.000
Thử tìm kiếm sinh viên có ID = 669.416
Đo và hiển thị thời gian thực thi
"""
start = time.time()
with open(filename, 'r', encoding="utf-8") as file:
    reader = csv.reader(file, delimiter='|')
    _ = next(reader)  # Bỏ qua dòng header
    for row in reader:
        if int(row[0]) == test_id:
            print(f'Thong tin cua sinh vien co id = {test_id}: ', row)
            break

print(f'Thoi gian tim kiem thong thuong la: {time.time() - start} giay')


"""
Test index
"""


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


def search_data(index_arr, test_id):
    return index_arr[test_id][1]


student_data = read_data('OneMstudents.txt')
data = {'student': student_data}
dbQuery = DBQuery(data)
dbQuery.create_index('student', 'id')
index_arr = dbQuery.indexes['id']
result = search_data(index_arr, test_id)
print(result)
