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
