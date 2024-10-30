import argparse

from SQLConnection import *
from WorkWithText import *

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
list_class_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
list_class_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh danh sách sinh viên
list_student_parser = subparsers.add_parser('list_student', help='Danh sách sinh viên')
list_student_parser.add_argument('--class_id', type=int, required=True, help='ID lớp')
list_student_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
list_student_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh danh sách giáo viên
list_teacher_parser = subparsers.add_parser('list_teacher', help='Danh sách giáo viên')
list_teacher_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
list_teacher_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh thêm lớp
add_class_parser = subparsers.add_parser('add_class', help='Thêm lớp')
add_class_parser.add_argument('--id', type=int, required=True, help='ID lớp')
add_class_parser.add_argument('--class_name', type=str, required=True, help='Tên lớp')
add_class_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
add_class_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh sửa lớp
edit_class_parser = subparsers.add_parser('edit_class', help='Sửa lớp')
edit_class_parser.add_argument('--id', type=int, required=True, help='ID lớp')
edit_class_parser.add_argument('--class_name', type=str, required=True, help='Tên lớp mới')
edit_class_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
edit_class_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh xoá lớp
remove_class_parser = subparsers.add_parser('remove_class', help='Xoá lớp')
remove_class_parser.add_argument('--id', type=int, required=True, help='ID lớp')
remove_class_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
remove_class_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh thêm sinh viên
add_student_parser = subparsers.add_parser('add_student', help='Thêm sinh viên')
add_student_parser.add_argument('--id', type=int, required=True, help='ID sinh viên')
add_student_parser.add_argument('--name', type=str, required=True, help='Tên sinh viên')
add_student_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh (YYYY-MM-DD)')
add_student_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại')
add_student_parser.add_argument('--class_id', type=int, required=True, help='ID lớp')
add_student_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
add_student_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh sửa sinh viên
edit_student_parser = subparsers.add_parser('edit_student', help='Sửa sinh viên')
edit_student_parser.add_argument('--id', type=int, required=True, help='ID sinh viên')
edit_student_parser.add_argument('--name', type=str, required=True, help='Tên sinh viên mới')
edit_student_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh mới (YYYY-MM-DD)')
edit_student_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại mới')
edit_student_parser.add_argument('--class_id', type=int, required=True, help='ID lớp mới')
edit_student_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
edit_student_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh xoá sinh viên
remove_student_parser = subparsers.add_parser('remove_student', help='Xoá sinh viên')
remove_student_parser.add_argument('--id', type=int, required=True, help='ID sinh viên')
remove_student_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
remove_student_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh thêm giáo viên
add_teacher_parser = subparsers.add_parser('add_teacher', help='Thêm giáo viên')
add_teacher_parser.add_argument('--id', type=int, required=True, help='ID giáo viên')
add_teacher_parser.add_argument('--name', type=str, required=True, help='Tên giáo viên')
add_teacher_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh (YYYY-MM-DD)')
add_teacher_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại')
add_teacher_parser.add_argument('--head_of_class', type=int, required=True, help='ID lớp chủ nhiệm')
add_teacher_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
add_teacher_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh sửa giáo viên
edit_teacher_parser = subparsers.add_parser('edit_teacher', help='Sửa giáo viên')
edit_teacher_parser.add_argument('--id', type=int, required=True, help='ID giáo viên')
edit_teacher_parser.add_argument('--name', type=str, required=True, help='Tên giáo viên mới')
edit_teacher_parser.add_argument('--birthday', type=str, required=True, help='Ngày sinh mới (YYYY-MM-DD)')
edit_teacher_parser.add_argument('--phone_number', type=str, required=True, help='Số điện thoại mới')
edit_teacher_parser.add_argument('--head_of_class', type=int, required=True, help='ID lớp chủ nhiệm mới')
edit_teacher_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
edit_teacher_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Lệnh xoá giáo viên
remove_teacher_parser = subparsers.add_parser('remove_teacher', help='Xoá giáo viên')
remove_teacher_parser.add_argument('--id', type=int, required=True, help='ID giáo viên')
remove_teacher_parser.add_argument('--useSQL', action='store_true', help='Sử dụng SQL (mặc định là False)')
remove_teacher_parser.add_argument('--no-useSQL', action='store_false', dest='useSQL', help='Không sử dụng SQL')

# Xử lý lệnh
args = parser.parse_args()

if args.command == 'connect_sql':
    # Lưu thông tin kết nối lại
    try:
        # Kiểm tra tính chính xác của thông tin kết nối
        mysql.connector.connect(
            host=args.localhost,
            user=args.username,
            password=args.password,
            database=args.database
        )
        # Lưu thông tin kết nối vào file .json
        connection_info = {
            'host': args.localhost,
            'user': args.username,
            'password': args.password,
            'database': args.database
        }
        print('Kết nối thành công đến MySQL.')
        with open('connection_info.json', 'w') as file:
            json.dump(connection_info, file)

    except Error as e:
        print(f"Lỗi '{e}' xảy ra khi kết nối đến MySQL")

elif args.command == 'disconnect_sql':
    # Ngắt ket noi voi MySQL
    if not os.path.exists('connection_info.json'):
        print('Chưa kết nối đến MySQL')
    else:
        os.remove('connection_info.json')  # xoá file .json
        print('Đã ngắt kết nối đến MySQL.')

else:
    # Nếu yêu cầu làm việc với MySQL
    if args.command and args.useSQL:
        print(1)
        # Kiểm tra sự tồn tại của file connection_info.json
        if not os.path.exists('connection_info.json'):
            print('Chưa kết nối đến MySQL')
        else:
            # Lấy dữ liệu kết nô bên trong file .json
            with open('connection_info.json', 'r') as file:
                connection_info = json.load(file)
                host_name, user_name, user_password, db_name = connection_info.values()

            # Tạo object SQLConnection
            sql_connection = SQLConnection(host_name, user_name, user_password, db_name)
            # ('127.0.0.1', 'root', '*********', 'qlsv')

            if args.command == 'list_class':
                # Hiển thị danh sách lớp
                sql_connection.readDataFromTable('class')

            elif args.command == 'list_student':
                # Hiển thị danh sách sinh viên theo lớp
                sql_connection.readDataFromTable('student', args.class_id)

            elif args.command == 'list_teacher':
                # Hiển thị danh sách giáo viên
                sql_connection.readDataFromTable('teacher')

            elif args.command == 'add_class':
                # Thêm lớp mới
                data = (args.id, args.class_name)
                sql_connection.insertDataToTable('class', data)

            elif args.command == 'edit_class':
                # Sửa lớp
                update_data = (args.id, args.class_name)
                sql_connection.updateDataToTable('class', update_data)

            elif args.command == 'remove_class':
                # Xoá lớp
                sql_connection.deleteDataToTable('class', args.id)

            elif args.command == 'add_student':
                # Thêm sinh viên
                data = (args.id, args.name, args.birthday, args.phone_number, args.class_id)
                sql_connection.insertDataToTable('student', data)

            elif args.command == 'edit_student':
                # Sửa sinh viên
                update_data = (args.id, args.name, args.birthday, args.phone_number, args.class_id)
                sql_connection.updateDataToTable('student', update_data)

            elif args.command == 'remove_student':
                # Xoá sinh viên
                sql_connection.deleteDataToTable('student', args.id)

            elif args.command == 'add_teacher':
                # Thêm giáo viên
                data = (args.id, args.name, args.birthday, args.phone_number, args.head_of_class)
                sql_connection.insertDataToTable('teacher', data)

            elif args.command == 'edit_teacher':
                # Sửa giáo viên
                update_data = (args.id, args.name, args.birthday, args.phone_number, args.head_of_class)
                sql_connection.updateDataToTable('teacher', update_data)

            elif args.command == 'remove_teacher':
                # Xoá giáo viên
                sql_connection.deleteDataToTable('teacher', args.id)

    else:
        # Làm việc với file text
        class_data = read_data('Class.txt')
        teacher_data = read_data('Teacher.txt')
        student_data = read_data('Student.txt')

        DATA = {'student': student_data, 'teacher': teacher_data, 'class': class_data}
        # Tạo database từ file text
        dbQuery = DBQuery(DATA)

        if args.command == 'list_class':
            # Hiển thị danh sách lớp
            rows = dbQuery.from_('class').get()
            print('Danh sach lop: ')
            for row in rows:
                print(row)

        elif args.command == 'list_student':
            # Hiển thị danh sách sinh viên theo lớp
            rows = dbQuery.from_('student').where('class_id', args.class_id).get()
            print(f'Danh sach hoc sinh lop {args.class_id}: ')
            for row in rows:
                print(row)

        elif args.command == 'list_teacher':
            # Hiển thị danh sách giáo viên
            rows = dbQuery.from_('teacher').get()
            print('Danh sach giao vien: ')
            for row in rows:
                print(row)

        elif args.command == 'add_class':
            # Thêm lớp mới
            data = {'id': args.id, 'name': args.class_name}
            dbQuery.insert('class', data)

        elif args.command == 'edit_class':
            # Sửa lớp
            update_data = {'id': args.id, 'name': args.class_name}
            dbQuery.where('id', args.id).update('class', update_data)

        elif args.command == 'remove_class':
            # Xoá lớp
            dbQuery.where('id', args.id).delete('class')

        elif args.command == 'add_student':
            # Thêm sinh viên
            data = {'id': args.id, 'name': args.name, 'birthday': args.birthday,
                    'phone_number': args.phone_number, 'class_id': args.class_id}
            dbQuery.insert('student', data)

        elif args.command == 'edit_student':
            # Sửa sinh viên
            update_data = {'id': args.id, 'name': args.name, 'birthday': args.birthday,
                           'phone_number': args.phone_number, 'class_id': args.class_id}
            dbQuery.where('id', args.id).update('student', update_data)

        elif args.command == 'remove_student':
            # Xoá sinh viên
            dbQuery.where('id', args.id).delete('student')

        elif args.command == 'add_teacher':
            # Thêm giáo viên
            data = {'id': args.id, 'name': args.name, 'birthday': args.birthday,
                    'phone_number': args.phone_number, 'head_of_class': args.head_of_class}
            dbQuery.insert('teacher', data)

        elif args.command == 'edit_teacher':
            # Sửa giáo viên
            update_data = {'id': args.id, 'name': args.name, 'birthday': args.birthday,
                           'phone_number': args.phone_number, 'head_of_class': args.head_of_class}
            dbQuery.where('id', args.id).update('teacher', update_data)

        elif args.command == 'remove_teacher':
            # Xoá giáo viên
            dbQuery.where('id', args.id).delete('teacher')

        write_data('Class.txt', dbQuery.data['class'], ['ID', 'Name'])
        write_data('Student.txt', dbQuery.data['student'], ['ID', 'Name', 'Birthday', 'Phone Number', 'Class ID'])
        write_data('Teacher.txt', dbQuery.data['teacher'], ['ID', 'Name', 'Birthday', 'Phone Number', 'Head of Class'])
