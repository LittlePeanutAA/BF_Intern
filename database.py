"""
Đóng gói lại các hàm làm việc đọc/ghi dữ liệu bằng cách viết các class sau
và sử dụng nó ở trong chương trình QLSV đã viết ở Task 1.

DBQuery: Có các method sau:

    Get(): Trả về dữ liệu
    Where(column_name, value): Set điều kiện cần lọc ví dụ dbQuery.where(‘id', 1)
    Select([ array of column names ]): Truyền vào tên các cột cần lấy data
    From( table_name): Chọn entity cần lấy dữ liệu
    Insert(table_name, data): Thêm dữ liệu vào entity
    Update(table_name, data): Update dữ liệu (cần dùng hàm where() ở trên để set điều kiện)
    Delete(table_name): Delete  (cần dùng hàm where() ở trên để set điều kiện)

Ví dụ để lấy các Sinh viên thuộc class có ID = 1 sẽ gọi như sau:
dbQuery.select([‘id',’name']).where(‘class_id', 1).from(‘student').get()
"""

# from BinaryTree import *
# from BinarySort import *
from MergeSort import *


indexOfHeader = {'student': {'id': 0, 'name': 1, 'birthday': 2, 'phone_number': 3, 'class_id': 4},
                 'teacher': {'id': 0, 'name': 1, 'birthday': 2, 'phone_number': 3, 'head_of_class': 4},
                 'class': {'id': 0, 'name': 1}}


class DBQuery:
    def __init__(self, data):
        self.data = data
        self.entity = []    # Target entity
        self.filters = []   # Condition for filtering
        self.columns = []   # The columns contain target data
        self.indexes = {}   # Save index for column

    # get(): return data
    def get(self):
        filtered_data = self.data
        header_dict = {}

        # Filter data by from()
        if self.entity:
            filtered_data = filtered_data[self.entity]
            header_dict = indexOfHeader[self.entity]
            self.entity = []

        # Filter data by where()
        if self.filters:
            column, value = self.filters
            indexOfColumn = header_dict[column]
            filtered_data = [row for row in filtered_data if row[indexOfColumn] == str(value)]
            self.filters = []

        # Filter data by select()
        if self.columns:
            filtered_data = [[row[header_dict[column]]
                              for column in self.columns]
                             for row in filtered_data]
            self.columns = []

        return filtered_data

    # where(column_name, value, value): setting condition for filtering
    def where(self, column_name, value):
        self.filters = [column_name, value]
        return self

    # select(columns): Passing names of columns needed to get data
    def select(self, columns):
        self.columns = columns
        return self

    # from(table_name): entity contain target data
    def from_(self, table_name):
        self.entity = table_name
        return self

    def insert(self, table_name, new_data):
        self.data[table_name].append(list(new_data.values()))

    # update(table_name, data): update data (need where() )
    def update(self, table_name, new_data):
        header_dict = indexOfHeader[table_name]
        for row in self.data[table_name]:
            column, value = self.filters
            if row[header_dict[column]] == str(value):
                for key, new_value in new_data.items():
                    row[header_dict[key]] = new_value
        self.filters = []

    # delete(table_name): delete data (need where() )
    def delete(self, table_name):
        header_dict = indexOfHeader[table_name]
        filtered_data = [row for row in self.data[table_name]]
        column, value = self.filters
        filtered_data = [row for row in filtered_data if row[header_dict[column]] != str(value)]
        self.data[table_name] = filtered_data
        self.filters = []

    """
    Thêm method: create_index(table_name, column_name)
        * Tạo 1 index để khi tìm kiếm theo column này thì thay vì duyệt hết cả bảng
        thì dùng cơ chế Binary Tree (cây nhị phân) để tìm kiếm.
        * Để dùng cơ chế này thì ta cần sắp xếp lại các giá trị theo thứ tự tăng dần,
        và lưu lại index của nó. Khi tìm kiếm thì dùng thuật toán cây nhị phân để tìm.
    """
    def create_index(self, table_name, column_name):
        index_arr = []
        header_dict = indexOfHeader[table_name]
        index_of_column = header_dict[column_name]
        data = self.data[table_name]

        # tree = BinaryTree()
        # for row in data[:10000]:
        #     tree.insert(int(row[index_of_column]))
        # self.indexes[column_name] = tree

        import time
        start = time.time()

        for row in data:
            # index_arr.append(int([row[index_of_column]), row])
            index_arr.append([row[index_of_column], row])

        # Sử dụng Binary Sort
        # sorted_index_arr = binary_insertion_sort(index_arr)
        # self.indexes[column_name] = sorted_index_arr

        # Sử dụng Merge Sort
        merge_sort(index_arr)
        self.indexes[column_name] = index_arr

        print("Create Index Time:", time.time() - start)
