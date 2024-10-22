from database import *


def get_data_from_file(filename):
    try:
        data = read_data(filename)
        return data
    except:
        return []


class_data = get_data_from_file('Class.txt')
teacher_data = get_data_from_file('Teacher.txt')
student_data = get_data_from_file('Student.txt')

DATA = {'student': student_data, 'teacher': teacher_data, 'class': class_data}

dbQuery = DBQuery(DATA)

# Lấy id va ten tất cả sinh viên thuộc lớp có id = 2
students = dbQuery.select(['id', 'name']).where('class_id', 2).from_('student').get()
print('Danh sach sinh vien trong lop id = 2: ')
print(students)

# Xoa cac lop co id = 2
print('Danh sach cac lop ban dau: ', DATA['class'])
dbQuery.where('id', 2).delete('class')
print('Danh sach cac lop bi xoa cac lop id = 2: ', DATA['class'])

# Thêm một sinh viên mới
print('Danh sach sinh vien ban dau: ', DATA['student'])
new_student = {'id': 1794, 'name': 'Nguyen Tung Duong', 'birthday': '2001-03-17',
               'phone_number': '0362235652', 'class_id': 2}
dbQuery.insert('student', new_student)
print('Danh sach sinh vien sau: ', DATA['student'])

# Cập nhật ten va sdt cua giao vien lop 2
print('Danh sach cac giao vien ban dau: ', DATA['teacher'])
dbQuery.where('head_of_class', 2).update('teacher',
                                         {'name': 'Nguyen Thanh Quynh Anh', 'phone_number': '0480952380'})
print('Danh sach cac giao vien sau khi sua: ', DATA['teacher'])
