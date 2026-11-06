import mysql.connector
from mysql.connector import Error
import json
import os


class SQLConnection:
    def __init__(self, host_name, user_name, user_password, db_name):
        """
        Tạo kết nối đến cơ sở dữ liệu MySQL.
        Nếu kết nối thanh công, lưu tham số vào file .json
        :param host_name: host local
        :param user_name: username
        :param user_password: password
        :param db_name: name of database
        """
        self.host = host_name
        self.username = user_name
        self.password = user_password
        self.database = db_name

        self.connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )

    def readDataFromTable(self, table_name, id=None):
        """
        Đọc dữ liệu từ bảng
        :param table_name: tên bảng
        :param id: id của class cho bảng student
        :return: None
        """
        cursor = self.connection.cursor()
        if table_name == 'student':
            cursor.execute(f"SELECT * FROM {table_name} WHERE class_id = {id}")
        else:
            cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"Dữ liệu từ bảng {table_name}: ")
        for row in rows:
            print(row)

    def insertDataToTable(self, table_name, data_tuple):
        """
        Insert du lieu trong bang
        :param table_name: tên bảng
        :param data_tuple: tuple chứa thông tin cập nhật được lưu theo đúng thứ tự
        :return: None
        """
        cursor = self.connection.cursor()
        query = f"INSERT INTO {table_name} VALUES {data_tuple}"
        cursor.execute(query)
        self.connection.commit()
        print("Dữ liệu đã được ghi vào bảng thành công")

    def updateDataToTable(self, table_name, data_tuple):
        """
        Update du lieu trong bang
        :param table_name: tên bảng
        :param data_tuple: tuple chứa thông tin cập nhật được lưu theo đúng thứ tự
        :return: None
        """
        cursor = self.connection.cursor()
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
        self.connection.commit()
        print("Dữ liệu đã được cap nhat vào bảng thành công")

    def deleteDataToTable(self, table_name, id):
        """
        Delete du lieu trong bang
        :param table_name: tên bảng
        :param id: id của dữ liệu cần xoá
        :return: None
        """
        cursor = self.connection.cursor()
        query = f"DELETE FROM {table_name} WHERE id = {id}"
        cursor.execute(query)
        self.connection.commit()
        print("Dữ liệu đã được xoa thành công")
