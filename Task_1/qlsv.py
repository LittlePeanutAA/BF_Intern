import argparse
import csv
from datetime import datetime

from entity import *
from save_file import *


# Tạo parser
parser = argparse.ArgumentParser(description='Ứng dụng Quản lý Sinh viên')
subparsers = parser.add_subparsers(dest='command', help='Lệnh')

# Các lệnh danh sách
# Lệnh danh sách lớp
list_class_parser = subparsers.add_parser('list_class', help='Danh sách lớp')

# Lệnh danh sách sinh viên
list_student_parser = subparsers.add_parser('list_student', help='Danh sách sinh viên')
list_student_parser.add_argument('--class_id', type=int, required=True, help='ID lớp')

# Lệnh danh sách giáo viên
list_teacher_parser = subparsers.add_parser('list_teacher', help='Danh sách giáo viên')

# Lệnh thêm lớp
add_class_parser = subparsers.add_parser('add_class', help='Thêm lớp')
add_class_parser.add_argument('--id', type=int, required=True, help='ID lớp')
add_class_parser.add_argument('--class_name', type=str, required=True, help='Tên lớp')

# Lệnh sửa lớp
edit_class_parser = subparsers.add_parser('edit_class', help='Sửa lớp')
edit_class_parser.add_argument('--id', type=int, required=True, help='ID lớp')
edit_class_parser.add_argument('--class_name', type=str, required=True, help='Tên lớp mới')

# Lệnh xoá lớp
remove_class_parser = subparsers.add_parser('remove_class', help='Xoá lớp')
remove_class_parser.add_argument('--id', type=int, required=True, help='ID lớp')

# Lệnh thêm sinh viên
add_student_parser = subparsers.add_parser('add_student', help='Thêm sinh viên')
add_student_parser.add_argument('--id', type=int, required=True, help='ID sinh viên')
add_student_parser.add_argument('--name', type=str, required=True, help='Tên sinh viên')
add_student_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh (YYYY-MM-DD)')
add_student_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại')
add_student_parser.add_argument('--class_id', type=int, required=True, help='ID lớp')

# Lệnh sửa sinh viên
edit_student_parser = subparsers.add_parser('edit_student', help='Sửa sinh viên')
edit_student_parser.add_argument('--id', type=int, required=True, help='ID sinh viên')
edit_student_parser.add_argument('--name', type=str, required=True, help='Tên sinh viên mới')
edit_student_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh mới (YYYY-MM-DD)')
edit_student_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại mới')
edit_student_parser.add_argument('--class_id', type=int, required=True, help='ID lớp mới')

# Lệnh xoá sinh viên
remove_student_parser = subparsers.add_parser('remove_student', help='Xoá sinh viên')
remove_student_parser.add_argument('--id', type=int, required=True, help='ID sinh viên')

# Lệnh thêm giáo viên
add_teacher_parser = subparsers.add_parser('add_teacher', help='Thêm giáo viên')
add_teacher_parser.add_argument('--id', type=int, required=True, help='ID giáo viên')
add_teacher_parser.add_argument('--name', type=str, required=True, help='Tên giáo viên')
add_teacher_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh (YYYY-MM-DD)')
add_teacher_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại')
add_teacher_parser.add_argument('--head_of_class', type=int, required=True, help='ID lớp chủ nhiệm')

# Lệnh sửa giáo viên
edit_teacher_parser = subparsers.add_parser('edit_teacher', help='Sửa giáo viên')
edit_teacher_parser.add_argument('--id', type=int, required=True, help='ID giáo viên')
edit_teacher_parser.add_argument('--name', type=str, required=True, help='Tên giáo viên mới')
edit_teacher_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh mới (YYYY-MM-DD)')
edit_teacher_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại mới')
edit_teacher_parser.add_argument('--head_of_class', type=int, required=True, help='ID lớp chủ nhiệm mới')

# Lệnh xoá giáo viên
remove_teacher_parser = subparsers.add_parser('remove_teacher', help='Xoá giáo viên')
remove_teacher_parser.add_argument('--id', type=int, required=True, help='ID giáo viên')

# Xử lý lệnh
args = parser.parse_args()


if args.command == 'list_class':
    # Hiển thị danh sách lớp
    print('Danh sách lớp:')
    data = read_data('Class.txt')
    for row in data:
        class_id, class_name = row
        print(f'ID: {class_id}, Tên lớp: {class_name}')

elif args.command == 'list_student':
    # Hiển thị danh sách sinh viên theo lớp
    print(f'Danh sách sinh viên lớp {args.class_id}: ')
    data = read_data('Student.txt')
    for row in data:
        student_id, student_name, birthday, phone_number, class_id = row
        if int(class_id) == args.class_id:
            print(f'ID: {student_id}, Tên sinh viên: {student_name}, '
                  f' Ngày sinh: {birthday}, Số điện thoại: {phone_number}')

elif args.command == 'list_teacher':
    # Hiển thị danh sách giáo viên
    print('Danh sách giáo viên:')
    data = read_data('Teacher.txt')
    for row in data:
        teacher_id, teacher_name, birthday, phone_number, head_of_class = row
        print(f'ID: {teacher_id}, Tên giáo viên: {teacher_name}, Ngày sinh: {birthday}, '
              f' Số điện thoại: {phone_number}, Lớp chủ nhiệm: {head_of_class}')

elif args.command == 'add_class':
    # Thêm lớp mới
    new_class = Class(str(args.id), args.class_name)
    data = read_data('Class.txt')
    data.append([new_class.id, new_class.name])
    write_data('Class.txt', data, ['ID', 'Class Name'])
    print(f'Lớp {args.class_name} đã được thêm vào.')

elif args.command == 'edit_class':
    # Sửa lớp
    data = read_data('Class.txt')
    updated_data = []
    for row in data:
        class_id, class_name, teacher_id = row
        if class_id == str(args.id):
            updated_data.append([class_id, args.class_name])
        else:
            updated_data.append(row)
    write_data('Class.txt', updated_data, ['ID', 'Class Name'])
    print(f'Lớp ID {args.id} đã được cập nhật.')

elif args.command == 'remove_class':
    # Xoá lớp
    data = read_data('Class.txt')
    updated_data = [row for row in data if row[0] != str(args.id)]
    write_data('Class.txt', updated_data, ['ID', 'Class Name'])
    print(f'Lớp ID {args.id} đã được xoá.')

elif args.command == 'add_student':
    # Thêm sinh viên
    birthday = datetime.strptime(args.birthday, '%Y-%m-%d').date()
    new_student = Student(str(args.id), args.name, birthday, args.phone_number, str(args.class_id))
    data = read_data('Student.txt')
    data.append([new_student.id, new_student.name, new_student.birthday.strftime('%Y-%m-%d'),
                 new_student.phone_number, new_student.class_id])
    write_data('Student.txt', data, ['ID', 'Name', 'Birthday', 'Phone Number', 'Class ID'])
    print(f'Sinh viên {args.name} đã được thêm vào.')

elif args.command == 'edit_student':
    # Sửa sinh viên
    birthday = datetime.strptime(args.birthday, '%Y-%m-%d').date()
    data = read_data('Student.txt')
    updated_data = []
    for row in data:
        student_id, student_name, birthday_str, phone_number, class_id = row
        if student_id == str(args.id):
            updated_data.append([student_id, args.name, birthday.strftime('%Y-%m-%d'),
                                 args.phone_number, str(args.class_id)])
        else:
            updated_data.append(row)
    write_data('Student.txt', updated_data, ['ID', 'Name', 'Birthday', 'Phone Number', 'Class ID'])
    print(f'Sinh viên ID {args.id} đã được cập nhật.')

elif args.command == 'remove_student':
    # Xoá sinh viên
    data = read_data('Student.txt')
    updated_data = [row for row in data if row[0] != str(args.id)]
    write_data('Student.txt', updated_data, ['ID', 'Name', 'Birthday', 'Phone Number', 'Class ID'])
    print(f'Sinh viên ID {args.id} đã được xoá.')

elif args.command == 'add_teacher':
    # Thêm giáo viên
    birthday = datetime.strptime(args.birthday, '%Y-%m-%d').date()
    new_teacher = Teacher(str(args.id), args.name, birthday, args.phone_number, str(args.head_of_class))
    data = read_data('Teacher.txt')
    data.append([new_teacher.id, new_teacher.name, new_teacher.birthday.strftime('%Y-%m-%d'),
                 new_teacher.phone_number, new_teacher.head_of_class])
    write_data('Teacher.txt', data, ['ID', 'Name', 'Birthday', 'Phone Number', 'Head of Class'])
    print(f'Giáo viên {args.name} đã được thêm vào.')

elif args.command == 'edit_teacher':
    # Sửa giáo viên
    birthday = datetime.strptime(args.birthday, '%Y-%m-%d').date()
    data = read_data('Teacher.txt')
    updated_data = []
    for row in data:
        teacher_id, teacher_name, birthday_str, phone_number, head_of_class = row
        if teacher_id == str(args.id):
            updated_data.append([teacher_id, args.name, birthday.strftime('%Y-%m-%d'),
                                 args.phone_number, str(args.head_of_class)])
        else:
            updated_data.append(row)
    write_data('Teacher.txt', updated_data, ['ID', 'Name', 'Birthday', 'Phone Number', 'Head of Class'])
    print(f'Giáo viên ID {args.id} đã được cập nhật.')

elif args.command == 'remove_teacher':
    # Xoá giáo viên
    data = read_data('Teacher.txt')
    updated_data = [row for row in data if row[0] != str(args.id)]
    write_data('Teacher.txt', updated_data, ['ID', 'Name', 'Birthday', 'Phone Number', 'Head of Class'])
    print(f'Giáo viên ID {args.id} đã được xoá.')
