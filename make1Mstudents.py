import csv
import random
import string
letters = string.ascii_letters

filename = 'OneMstudents.txt'
header = ['ID', 'Name', 'Birthday', 'Phone Number', 'Class ID']
id_list = list(range(1000000))
random.shuffle(id_list)

with open(filename, 'w', encoding="utf-8", newline='') as file:
    writer = csv.writer(file, delimiter='|')
    writer.writerow(header)
    for id in range(1000000):
        name = ''.join(random.choice(letters) for i in range(10))
        class_id = random.randint(0, 10)
        phone_num = '0' + str(random.randint(123456789, 987654321))
        birthday = '2001-' + str(random.randint(1, 12)) + '-' + str(random.randint(1, 30))

        data = [id_list[id], name, birthday, phone_num, class_id]
        writer.writerow(data)

        if (id % 10000) == 0:
            print(f'{id/10000 + 1}%')
