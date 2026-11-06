# Đối tượng Student
class Student:
    def __init__(self, id, name, birthday, phone_number, class_id):
        self.id = id
        self.name = name
        self.birthday = birthday
        self.phone_number = phone_number
        self.class_id = class_id


# Đối tượng Class
class Class:
    def __init__(self, id, name):
        self.id = id
        self.name = name


# Đối tượng Teacher
class Teacher:
    def __init__(self, id, name, birthday, phone_number, head_of_class):
        self.id = id
        self.name = name
        self.birthday = birthday
        self.phone_number = phone_number
        self.head_of_class = head_of_class
