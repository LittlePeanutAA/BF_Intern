import argparse

from SQLConnection import *

# Tạo parser
parser = argparse.ArgumentParser(description='Ứng dụng Quản lý Sinh viên')
subparsers = parser.add_subparsers(dest='command', help='Lệnh')

# Kết nối với MySQL
connect_sql_parser = subparsers.add_parser('connect_sql', help='Kết nối với MySQL')
connect_sql_parser.add_argument('--localhost', type=str, required=True, help='Local Host')
connect_sql_parser.add_argument('--username', type=str, required=True, help='Username')
connect_sql_parser.add_argument('--password', type=str, required=True, help='Password')
connect_sql_parser.add_argument('--database', type=str, required=True, help='Database name')

# Ngắt kết nối với MySQL
disconnect_sql_parser = subparsers.add_parser('disconnect_sql', help='Ngắt kết nối với MySQL')

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
if os.path.exists('connection_info.json'):
    with open('connection_info.json', 'r') as file:
        connection_info = json.load(file)
    connection = mysql.connector.connect(
                    host=connection_info['host'],
                    user=connection_info['user'],
                    password=connection_info['password'],
                    database=connection_info['database']
                )
else:
    connection = None
# connection = createConnection('127.0.0.1', 'root', 'Anhduy', 'qlsv')

if args.command == 'connect_sql':
    # Kết nốt với MySQL
    host_name, user_name, user_password, db_name = args.localhost, args.username, args.password, args.database
    createConnection(host_name, user_name, user_password, db_name)

elif args.command == 'list_class':
    # Hiển thị danh sách lớp
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        readDataFromTable(connection, 'class')

elif args.command == 'list_student':
    # Hiển thị danh sách sinh viên theo lớp
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        class_id = args.class_id
        readDataFromTable(connection, 'student', class_id)

elif args.command == 'list_teacher':
    # Hiển thị danh sách giáo viên
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        readDataFromTable(connection, 'teacher')

elif args.command == 'add_class':
    # Thêm lớp mới
    new_class = Class(str(args.id), args.class_name)
    data = (new_class.id, new_class.name)
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        insertDataToTable(connection, 'class', data)

elif args.command == 'edit_class':
    # Sửa lớp
    update_data = (args.id, args.class_name)
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        updateDataToTable(connection, 'class', update_data)


elif args.command == 'remove_class':
    # Xoá lớp
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        deleteDataToTable(connection, 'class', args.id)

elif args.command == 'add_student':
    # Thêm sinh viên
    data = (args.id, args.name, args.birthday, args.phone_number, args.class_id)
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        insertDataToTable(connection, 'student', data)

elif args.command == 'edit_student':
    # Sửa sinh viên
    update_data = (args.id, args.name, args.birthday, args.phone_number, args.class_id)
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        updateDataToTable(connection, 'student', update_data)

elif args.command == 'remove_student':
    # Xoá sinh viên
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        deleteDataToTable(connection, 'student', args.id)

elif args.command == 'add_teacher':
    # Thêm giáo viên
    data = (args.id, args.name, args.birthday, args.phone_number, args.head_of_class)
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        insertDataToTable(connection, 'teacher', data)

elif args.command == 'edit_teacher':
    # Sửa giáo viên
    update_data = (args.id, args.name, args.birthday, args.phone_number, args.head_of_class)
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        updateDataToTable(connection, 'teacher', update_data)

elif args.command == 'remove_teacher':
    # Xoá giáo viên
    if not connection:
        print('Chưa kết nối đến MySQL')
    else:
        deleteDataToTable(connection, 'teacher', args.id)

elif args.command == 'disconnect_sql':
    # Ngắt ket noi voi MySQL
    if os.path.exists('connection_info.json'):
        os.remove('connection_info.json') # xoá file .json
    else:
        print('Chua ket noi den MySQL')
