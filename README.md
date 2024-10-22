Condition, Loop, File IO
# Quản lý SV:
## QLSV bằng các câu lệnh: 
### List class
### List students in class
### List teacher
### Thêm/Sửa/Xoá class:
- Thêm class: ```python qlsv.py add_class --id 1 --class_name “Lớp K66CC”```
- Sửa class: ```python qlsv.py edit_class --id 1 --class_name “Lớp K66CC”```
- Xoá class: ```python qlsv.py remove_class --id 1```
### Thêm/Sửa/Xoá student
### Thêm/Sửa/Xoá teacher
Ví dụ: ```python qlsv.py --command --parameter```

Danh sách lớp: ```python qlsv.py list_class```

Danh sách sv: ```python qlsv.py list_student --class_id 1```
# Entity:
## Student:
- ID
- Name
- Birthday
- Phone number
- Class ID
## Class:
- ID
- Name
## Teacher
- ID
- Name
- Birthday
- Phone number
- Head of class (chủ nhiệm)
# Save to file:
File name = entity name (ví dụ thông tin sinh viên lưu vào file Student.txt)
1st row is column name - Cách nhau bằng dấu | - Ví dụ dòng đầu tiên file Class.txt là ID|Class Name
Next rows are data. Ví dụ 1 row trong file Class.txt: 1 | K66CC
