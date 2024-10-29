import mysql.connector
from mysql.connector import Error
import json
import os


def createConnection(host_name, user_name, user_password, db_name):
    """Tạo kết nối đến cơ sở dữ liệu MySQL."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("Kết nối thành công đến MySQL")
        connection_info = {
            'host': host_name,
            'user': user_name,
            'password': user_password,
            'database': db_name
        }

        with open('connection_info.json', 'w') as file:
            json.dump(connection_info, file)

    except Error as e:
        print(f"Lỗi '{e}' xảy ra khi kết nối đến MySQL")
    return connection


def readDataFromTable(connection, table_name, id=None):
    """Đọc dữ liệu từ bảng"""
    cursor = connection.cursor()
    if table_name == 'student':
        cursor.execute(f"SELECT * FROM {table_name} WHERE class_id = {id}")
    else:
        cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    print(f"Dữ liệu từ bảng {table_name}: ")
    for row in rows:
        print(row)


def insertDataToTable(connection, table_name, data_tuple):
    """Insert du lieu trong bang"""
    cursor = connection.cursor()
    query = f"INSERT INTO {table_name} VALUES {data_tuple}"
    cursor.execute(query)
    connection.commit()
    print("Dữ liệu đã được ghi vào bảng thành công")


def updateDataToTable(connection, table_name, data_tuple):
    """Update du lieu trong bang"""
    cursor = connection.cursor()
    if table_name == 'class':
        query = f"UPDATE {table_name} SET name = %s WHERE id = {data_tuple[0]}"
    elif table_name == 'student':
        query = (f"UPDATE {table_name} SET name = %s, birthday = %s, phone_number = %s, class_id = %s"
                 f"WHERE id = {data_tuple[0]}")
    elif table_name == 'teacher':
        query = (f"UPDATE {table_name} SET name = %s, birthday = %s, phone_number = %s, head_of_class = %s"
                 f"WHERE id = {data_tuple[0]}")
    else:
        query = ""
    cursor.execute(query, data_tuple[1:])
    connection.commit()
    print("Dữ liệu đã được cap nhat vào bảng thành công")


def deleteDataToTable(connection, table_name, id):
    """Delete du lieu trong bang"""
    cursor = connection.cursor()
    query = f"DELETE FROM {table_name} WHERE id = {id}"
    cursor.execute(query)
    connection.commit()
    print("Dữ liệu đã được xoa thành công")
