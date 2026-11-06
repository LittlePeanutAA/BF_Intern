"""
Đóng gói lại các hàm làm việc đọc/ghi dữ liệu bằng cách viết các class sau
và sử dụng nó ở trong chương trình QLSV đã viết ở Task 1.

DBQuery: Có các method sau:

    get(): Trả về dữ liệu
    where(column_name, value): Set điều kiện cần lọc ví dụ dbQuery.where(‘id', 1)
    select([ array of column names ]): Truyền vào tên các cột cần lấy data
    from( table_name): Chọn entity cần lấy dữ liệu
    insert(table_name, data): Thêm dữ liệu vào entity
    update(table_name, data): Update dữ liệu (cần dùng hàm where() ở trên để set điều kiện)
    delete(table_name): Delete  (cần dùng hàm where() ở trên để set điều kiện)

Ví dụ để lấy các Sinh viên thuộc class có ID = 1 sẽ gọi như sau:
dbQuery.select([‘id',’name']).where(‘class_id', 1).from(‘student').get()
"""

import csv


# Hàm đọc dữ liệu từ file
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


# Hàm ghi dữ liệu vào file
def write_data(filename, data, header):
    with open(filename, 'w', encoding="utf-8", newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(header)
        writer.writerows(data)


indexOfHeader = {'student': {'id': 0, 'name': 1, 'birthday': 2, 'phone_number': 3, 'class_id': 4},
                 'teacher': {'id': 0, 'name': 1, 'birthday': 2, 'phone_number': 3, 'head_of_class': 4},
                 'class': {'id': 0, 'name': 1}}


class DBQuery:
    def __init__(self, data):
        self.data = data
        self.entity = []  # Target entity
        self.filters = []  # Condition for filtering
        self.columns = []  # The columns contain target data

    # get(): return data
    def get(self):
        filtered_data = self.data
        header_dict = {}

        # Filter data by from()
        if self.entity:
            try:
                filtered_data = filtered_data[self.entity]
                header_dict = indexOfHeader[self.entity]

            except:
                print('Khong ton tai bang nay')
                self.entity = []
                return []
            self.entity = []

            # Filter data by where()
            if self.filters:
                column, value = self.filters
                try:
                    indexOfColumn = header_dict[column]
                    filtered_data = [row for row in filtered_data if row[indexOfColumn] == str(value)]
                except:
                    print('Khong ton tai cot nay')
                self.filters = []

            # Filter data by select()
            if self.columns:
                try:
                    filtered_data = [[row[header_dict[column]]
                                      for column in self.columns]
                                     for row in filtered_data]
                except:
                    print('Khong ton tai mot trong cac cot nay')
                    # filtered_data = []
                    self.columns = []
                    return []
                self.columns = []
            return filtered_data

        else:
            print('Su dung from() de chon bang du lieu muon lay du lieu')
            return []

    # where(column_name, value, value): setting condition for filtering
    def where(self, column_name, value):
        if isinstance(column_name, str) and isinstance(value, (str, int, float)):
            self.filters = [column_name, value]
        else:
            # self.filters = []
            print('Sai kiểu dữ liệu trong hàm where()')
        return self

    # select(columns): Passing names of columns needed to get data
    def select(self, *cols):
        for col in cols:
            if not isinstance(col, str):
                self.columns = []
                print('Sai kiểu dữ liệu tên cột')
                break
            else:
                self.columns.append(col)
        return self

    # from(table_name): entity contain target data
    def from_(self, table_name):
        if not isinstance(table_name, str):
            # self.columns = []
            print('Sai kiểu dữ liệu tên bảng')
        else:
            self.entity = table_name
        return self

    def insert(self, table_name, new_data):
        if not isinstance(table_name, str):
            print('Sai kiểu dữ liệu tên bảng')
        else:
            if not isinstance(new_data, dict):
                print('Sai kieu du lieu data')
            else:
                keys = list(new_data.keys())
                if not keys == list(indexOfHeader[table_name].keys()):
                    print('Sai kieu du lieu data')
                else:
                    new_data_value = list(new_data.values())
                    new_data_value = [str(value) for value in new_data_value]
                    if new_data_value in self.data[table_name]:
                        print('Data da ton tai')
                    else:
                        try:
                            self.data[table_name].append(list(new_data_value))
                            return 1
                        except:
                            print('Khong ton tai bang nay')

    # update(table_name, data): update data (need where() )
    def update(self, table_name, new_data):
        header_dict = {}
        try:
            header_dict = indexOfHeader[table_name]
        except:
            print('Ten bang khong hop le')

        if header_dict:
            if not isinstance(new_data, dict):
                print('Sai kieu du lieu data')
            else:
                keys = list(new_data.keys())
                if not keys == list(indexOfHeader[table_name].keys()):
                    print('Sai form du lieu data')
                else:
                    new_data_value = list(new_data.values())
                    new_data_value = [str(value) for value in new_data_value]
                    if new_data_value in self.data[table_name]:
                        print('Data da ton tai')
                    else:
                        try:
                            column, value = self.filters
                            for row in self.data[table_name]:
                                if row[header_dict[column]] == str(value):
                                    row = new_data_value
                            self.filters = []
                            return 1
                        except:
                            print('Khong ton tai bang hoac cot nay')
        self.filters = []

    # delete(table_name): delete data (need where() )
    def delete(self, table_name):
        header_dict = {}
        try:
            header_dict = indexOfHeader[table_name]
        except:
            print('Ten bang khong hop le')

        if header_dict:
            try:
                filtered_data = [row for row in self.data[table_name]]
                column, value = self.filters
                filtered_data = [row for row in filtered_data if row[header_dict[column]] != str(value)]
                self.data[table_name] = filtered_data
                self.filters = []
                return 1
            except:
                print('Khong ton tai bang hoac cot nay')
        self.filters = []
