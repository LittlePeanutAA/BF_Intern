"""
Viết code để test các method của class Query ở task 2.
Cố gắng test hết các function của class và test nhiều trường hợp nhất có thể.
Ví dụ: Để test hàm insert:
    status = dbQuery.insert(‘class’, { ‘id’: 1, ‘name’: ‘Class 1’ })
    assert status == 1
    assert dbQuery.where(‘id’, 1).from(‘Class’).select(‘id’).get() != None
"""

from database import *


def test_query(dbQuery):
    """
    :param dbQuery: database đã được khởi tạo
    :return: None
    """

    """
    1. Test where()
    * Chạy bình thương
    * Sai tên trường
    * Dữ liệu không tồn tại trong trường
    * Sai kiểu dữ liệu của trường hoặc data
    """

    print('1.1. Test normal where')
    results = dbQuery.where('id', 1).from_('class').select('name').get()
    assert results == [['Class 1']], "where sai"

    results = dbQuery.where('name', 'Bui Cong Duy').from_('student').select('id').get()
    # print('Nhung thang ten Bui Cong Duy: ', results)
    assert results != [[]], "where nhieu data trung nhau"

    results = dbQuery.where('id', 1).from_('class').get()
    assert results == [['1', 'Class 1']], "where khong co select() bi sai"

    print('1.2. Test where with non-exist field ("id" not "class_id")')
    results = dbQuery.where('class_id', 1).from_('class').select('name').get()
    assert results == [['Class 0'], ['Class 1'], ['Class 2'], ['Class 3'], ['Class 4'], ['Class 5'],
                       ['Class 6'], ['Class 7'], ['Class 8'], ['Class 9'], ['Class 10']],\
        "where bi sai khi nhap vao ten code khong ton tai"

    print("1.3. Test where with non-exist data")
    results = dbQuery.where('id', 99).from_('class').select('name').get()
    assert results == [], "where bi sai khi du lieu so sanh khong ton tai"

    print("1.4. Test where with error data")
    results = dbQuery.where(99, 1).from_('class').select('name').get()
    assert results == [['Class 0'], ['Class 1'], ['Class 2'], ['Class 3'], ['Class 4'], ['Class 5'],
                       ['Class 6'], ['Class 7'], ['Class 8'], ['Class 9'], ['Class 10']],\
        "where sai khi kieu du lieu cua cot so sanh khong dung"

    results = dbQuery.where('id', [1]).from_('class').select('name').get()
    assert results == [['Class 0'], ['Class 1'], ['Class 2'], ['Class 3'], ['Class 4'], ['Class 5'],
                       ['Class 6'], ['Class 7'], ['Class 8'], ['Class 9'], ['Class 10']],\
        "where sai khi kieu du lieu cua gia tri so sanh khong dung"

    """
    2. Test select()
    * Chạy bình thương
    * Sai tên trường
    * Sai kiểu dữ liệu của trường
    """

    print("2.1. Test select specific fields")
    results = dbQuery.where('id', 360127).from_('student').select('phone_number').get()
    assert results == [['0398338826']], "select() bi sai"

    results = dbQuery.where('id', 360127).from_('student').select('phone_number', 'name').get()
    assert results == [['0398338826', 'Le Ngoc Khanh']], "select nhieu cot bi sai"

    print("2.2. Sai ten truong")
    results = dbQuery.where('id', 2207).from_('student').select('phone').get()
    assert results == [], "select sai khi ten truong sai"

    results = dbQuery.where('id', 2207).from_('student').select('first name', 'phone_number').get()
    assert results == [], "select sai khi 1 trong cac cot bi sai ten"

    print("2.3. Sai kieu du lieu truong")
    results = dbQuery.where('id', 2207).from_('student').select(256).get()
    assert results == [['2207', 'Do Minh Nhi', '2001-11-26', '0728844496', '9']], "select sai khi sai kdl cua truong"

    results = dbQuery.where('id', 2207).from_('student').select('phone_number', 256).get()
    assert results == [['2207', 'Do Minh Nhi', '2001-11-26', '0728844496', '9']],\
        "select sai khi kieu du lieu cua 1 trong cac cot bi sai"

    """
    3. Test from_()
    * Chạy bình thương
    * Sai tên trường
    * Sai kiểu dữ liệu của trường
    """

    print("3.1. From chay binh thuong")
    results = dbQuery.where('id', 360127).from_('student').select('phone_number').get()
    assert results == [['0398338826']], "from() bi sai"

    print("3.2. Sai ten truong")
    results = dbQuery.where('id', 2207).from_('college').select('phone_number').get()
    assert results == [], "from sai khi ten bang khong ton tai"

    print("3.3. Sai kieu du lieu ten bang")
    results = dbQuery.where('id', 2207).from_(256).select('phone_number').get()
    assert results == [], "from sai khi sai kieu du lieu cua ten bang"

    """
    4. Test get()
    * Chay binh thuong
    * Không có hàm where(), from_(), select()
    * get() có làm thay đổi dữ liệu trong database không?
    """

    print("4.1. Test getting a record that does not exist")
    results = dbQuery.where('id', 1).from_('class').select('name').get()
    assert results == [], "get() bi sai"
    assert len(dbQuery.data['class']) == 11, "get() lam thay doi so luong du lieu"

    """
    5. Test insert()
    * Chay binh thuong (xem dữ liệu được chèn chưa)
    * Dữ liệu bị lỗi (thừa/thiếu trường)
    * Sai kiểu dữ liệu
    * Dữ liệu bị trùng
    * Chèn nhiều dữ liệu liên tục
    """

    print("5.1. Khi chen du lieu moi")
    status = dbQuery.insert('class', {'id': 11, 'name': 'Class 11'})
    print(dbQuery.data['class'])
    assert status == 1, "insert() khong chen duoc du lieu"
    assert dbQuery.where('id', 11).from_('class').select('name').get() != [[]], "Du lieu chua duoc chen"

    print("5.2. When inserting a duplicate data")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.insert('class', {'id': 1, 'name': 'Class 1'})
    assert status is None, "insert van chen du lieu trung"
    assert len(dbQuery.data['class']) == num_before, "Insert trung lap nhung van thay doi so luong"

    print("5.3. When inserting multi datas")
    dbQuery.insert('class', {'id': 12, 'name': 'Class 12'})
    dbQuery.insert('class', {'id': 13, 'name': 'Class 13'})
    assert dbQuery.where('id', 12).from_('class').select('name').get() != [[]], "chen 2 lan lien tiep bi loi"

    print("5.4. When inserting error data")
    status = dbQuery.insert('class', {'id': 14})
    assert status is None, "Insert failed 3"
    assert dbQuery.where('id', 14).from_('class').select('id').get() == [], "Insert thieu truong"

    status = dbQuery.insert('class', {'id': 15, 'name': 'Class 14', 'teacher': 'Tu'})
    assert status is None, "Insert failed 3"
    assert dbQuery.where('id', 15).from_('class').select('id').get() == [], "Insert thừa truong"

    print("5.5. Chèn sai tên trường")
    status = dbQuery.insert('class', {'id': 16, 'class_name': 'Class 16'})
    assert status is None, "Insert failed 3"
    assert dbQuery.where('id', 16).from_('class').select('id').get() == [], "Insert sai ten truong"

    """
    6. Test update()
    * Chay binh thuong (check xem dữ liệu có tăng lên hay mất đi, biến đổi)
    * Dữ liệu bị lỗi (thừa/thiếu trường)
    * Sai kiểu dữ liệu
    * Dữ liệu không thay đổi
    * Cập nhật nhiều dữ liệu liên tục (cùng 1 row)
    * Không có method where()
    """

    print("6.1. When updating a new data")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 0).update('class', {'id': 0, 'name': 'Class 00'})
    print(dbQuery.data['class'])
    assert status == 1, "update() bi sai"
    assert dbQuery.where('name', 'Class 00').from_('class').select('id').get() != [[]], "Ko thay du lieu moi"
    assert len(dbQuery.data['class']) == num_before, "Update nhung van thay doi so luong 0"

    print("6.2. When updating a duplicate data")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 1).update('class', {'id': 1, 'name': 'Class 1'})
    assert status is None, "update du lieu da ton tai 1"
    assert len(dbQuery.data['class']) == num_before, "ko Update nhung van thay doi so luong 1"

    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 2).update('class', {'id': 3, 'name': 'Class 3'})
    assert status is None, "update du lieu da ton tai 2"
    assert len(dbQuery.data['class']) == num_before, "ko Update nhung van thay doi so luong 2"

    print("6.3. When updating multi datas")
    num_before = len(dbQuery.data['class'])
    dbQuery.where('id', 4).update('class', {'id': 24, 'name': 'Class 24'})
    dbQuery.where('id', 4).update('class', {'id': 34, 'name': 'Class 34'})
    assert len(dbQuery.data['class']) == num_before, "Update nhieu lan lam thay doi so luong"

    print("6.4. When updating error data")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 5).update('class_name', {'id': 25, 'name': 'Class 25'})
    assert status is None, "update du lieu sai ten bang"
    assert len(dbQuery.data['class']) == num_before, "Update sai ten bang"

    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 6).update('class', {'class_id': 26, 'name': 'Class 26'})
    assert status is None, "update du lieu bi sai ten cot"
    assert len(dbQuery.data['class']) == num_before, "Update sai ten truong trong du lieu"

    print("6.5. Thừa, thiếu trường")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 7).update('class', {'id': 27})
    assert status is None, "update du lieu thieu"
    assert len(dbQuery.data['class']) == num_before, "Update thieu truong"

    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 8).update('class', {'id': 28, 'name': 'Class 28', 'teacher': 'Tu'})
    assert status is None, "update du lieu thua"
    assert len(dbQuery.data['class']) == num_before, "Update thua truong"

    print("6.6. Không có method where()")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.update('class', {'id': 100, 'name': 'Class 100'})
    assert status is None, "update du lieu khi khong co where"
    assert len(dbQuery.data['class']) == num_before, "Update khong co where"

    """
    7. Test delete()
    * Chay binh thuong
    * Bảng không tồn tại, bảng vừa bị xoá
    * Sai kiểu dữ liệu
    * Không có method where()
    """

    print("7.1. When deleting a data")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 0).delete('class')
    assert status == 1, "delete() bi sai"
    assert dbQuery.where('name', 'Class 0').from_('class').select('id').get() == [], "Du lieu chua bi xoa"
    assert len(dbQuery.data['class']) == num_before - 1, "Delete nhung ko thay doi so luong"

    print("7.2. Xoá bảng không tồn tại (sai tên bảng)")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 1).delete('class_')
    assert status is None, "delete van xoa khi sai ten bang"
    assert dbQuery.where('id', 1).from_('class').select('name').get() == [['Class 1']], "Du lieu sai bảng vẫn bị xoá"
    assert len(dbQuery.data['class']) == num_before, "Xoá sai bảng nhưng thay đổi số lượng"

    print("7.3. Sai du lieu where")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where(15, 15).delete('class')
    assert status is None, "delete van xoa khi where sai"
    assert len(dbQuery.data['class']) == num_before, "Xoá sai dwx lieu hang nhưng thay đổi số lượng"

    print("7.4. Xoa 2 lan lien tiep 1 dong")
    num_before = len(dbQuery.data['class'])
    dbQuery.where('id', 2).delete('class')
    dbQuery.where('id', 2).delete('class')
    assert len(dbQuery.data['class']) == num_before - 1, "Xoa 1 dong nhieu lan nhung so luong gap van de"

    print("7.5. Sai kieu du lieu ten bang")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.where('id', 5).delete(125)
    assert status is None, "Delete van xoa khi sai ten bang"
    assert dbQuery.where('id', 5).from_('class').select('name').get() == [['Class 5']], "Du lieu sai bảng vẫn bị xoá"
    assert len(dbQuery.data['class']) == num_before, "Xoá sai kieu du lieu bảng nhưng thay đổi số lượng"

    print("7.6. Không có method where()")
    num_before = len(dbQuery.data['class'])
    status = dbQuery.delete('class')
    assert status is None, "delete van xoa khi khong co where"
    assert len(dbQuery.data['class']) == num_before, "Delete khong co where"

    print()
    print()
    print('---------------------------------------------------------------------')
    print("All tests passed.")


student_data = read_data('OneMstudents.txt')
class_data = read_data('Class.txt')
DATA = {'student': student_data, 'class': class_data}
dbQuery = DBQuery(DATA)

test_query(dbQuery)
