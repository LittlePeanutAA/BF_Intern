import requests
import cv2


# Gửi request
url = 'http://192.168.1.53:5000/api/predict'
image_path = 'test_img.jpg'

# Đọc và show ảnh gốc
img = cv2.imread(image_path)
cv2.imshow('Original Image', img)

# Gửi request và nhận kết quả
files = {'image': open(image_path, 'rb')}
response = requests.post(url, files=files)
predictions = response.json()['predictions']

# Vẽ bounding boxes lên ảnh
for pred in predictions:
    bbox = pred['bbox']
    class_name = pred['class_name']
    confidence = pred['confidence']

    x1, y1, x2, y2 = map(int, bbox)
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, f'{class_name}: {confidence: .2f}',
                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 255, 0), 2)

# Show ảnh với predictions
cv2.imshow('Predictions', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
