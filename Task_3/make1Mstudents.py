import csv
import random
import string


filename = 'OneMstudents.txt'
header = ['ID', 'Name', 'Birthday', 'Phone Number', 'Class ID']
first_name = ["An",
              "Binh",
              "Cuc",
              "Duc",
              "Duy",
              "Giang",
              "Hai",
              "Khanh",
              "Linh",
              "Minh",
              "Nam",
              "Phuc",
              "Quang",
              "Son",
              "Tam",
              "Thao",
              "Tuan",
              "Van",
              "Yen",
              "Thuy",
              "Trang",
              "Hanh",
              "Hieu",
              "Kien",
              "Long",
              "Ly",
              "My",
              "Nhi",
              "Phuong",
              "Quy",
              "Sang",
              "Tam",
              "Tuyet",
              "Vinh",
              "Xuan",
              "Chau",
              "Dai",
              "Thang",
              "Tram",
              "Bich",
              "Diep",
              "Nhat",
              "Tu"]
middle_name = [" Cong ",
               " Van ",
               " Thi ",
               " Huu ",
               " Quoc ",
               " Minh ",
               " Hoa ",
               " Thanh ",
               " Anh ",
               " Duy ",
               " Tu ",
               " Linh ",
               " Tuyet ",
               " Ngoc ",
               " Khanh ",
               " Hai ",
               " Cuong ",
               " Tuan ",
               " Hanh ",
               " Son ",
               " Phuc ",
               " Ly "]
last_name = ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Phan', 'Vu',
             'Huynh', 'Vo', 'Dang', 'Bui', 'Do', 'Ho', 'Ngo', 'Duong', 'Ly']
id_list = list(range(1000000))
random.shuffle(id_list)

with open(filename, 'w', encoding="utf-8", newline='') as file:
    writer = csv.writer(file, delimiter='|')
    writer.writerow(header)
    for id in range(1000000):
        name = random.choice(last_name) + random.choice(middle_name) + random.choice(first_name)
        class_id = random.randint(0, 10)
        phone_num = '0' + str(random.randint(123456789, 987654321))
        birthday = '2001-' + str(random.randint(1, 12)) + '-' + str(random.randint(1, 30))

        data = [id_list[id], name, birthday, phone_num, class_id]
        writer.writerow(data)

        if (id % 10000) == 0:
            print(f'{id / 10000 + 1}%')
