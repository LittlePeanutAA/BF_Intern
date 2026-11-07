# Lời giải bài 11

```
solution/annotations.py     DB rect (%) -> box YOLO; dHash gom ảnh trùng; chia split theo nhóm
solution/crops.py           cắt vùng nhãn, đổi box qua lại giữa ảnh gốc và vùng cắt
solution/yolo_data.py       dựng manifest + dataset bước 1 (ảnh gốc) và bước 2 (vùng nhãn)
solution/train.py           train một bước rồi đo một lần trên test
solution/eval_pipeline.py   đo cả pipeline (bước 1, bước 1 + 2) trên ảnh gốc của tập test
solution/configs/*.yaml     tham số train (chỉ gồm key hợp lệ của Ultralytics)
solution/api.py             API FastAPI hai bước
```

Weights đã train **không** có trong repo, vì chúng được học từ dữ liệu nội bộ.

## 1. Khảo sát mô hình

| Họ mô hình | Ví dụ | Hợp với bài này? |
|---|---|---|
| Detector một bước | YOLOv5/v8/v11, SSD, RetinaNet | **Có.** Nhanh, fine-tune dễ, thư viện tốt. Yếu với vật thể rất nhỏ ở `imgsz` thấp |
| Detector hai bước | Faster R-CNN, Cascade R-CNN | Chính xác hơn một chút với vật thể nhỏ, nhưng chậm hơn nhiều và cấu hình phức tạp hơn |
| Detector dạng transformer | DETR, RT-DETR | Cần nhiều dữ liệu và thời gian train hơn. Vài nghìn ảnh là ít |
| Phát hiện vùng chữ | DBNet, CRAFT, EAST | Tìm **mọi** dòng chữ rất tốt, nhưng không biết dòng nào là giống nho, dòng nào là năm. Cần thêm bước phân loại |
| Mô hình thị giác–ngôn ngữ (VLM) | Qwen-VL, Florence-2, GPT-4o | Không chỉ tìm mà còn **đọc** được chữ. Nặng, chậm hơn detector hàng chục lần |

Điểm mấu chốt về dữ liệu: nhãn chai là vật thể lớn, dễ. Dòng variety/vintage là **dòng chữ nhỏ**, thường chỉ vài chục pixel trên ảnh khoảng 400×600.

## 2. Chọn mô hình: YOLOv8s, hai bước

- **Bước 1:** detect `label`, `variety`, `vintage` trên ảnh gốc.
- **Bước 2:** cắt vùng nhãn (nới thêm 2%), detect lại `variety`, `vintage` trong vùng cắt.

Lý do:
- YOLO train nhanh trên một GPU phổ thông, chạy khoảng 3 ms/ảnh, có sẵn pipeline augmentation, đánh giá, export.
- Bản **s** thay vì **n**: tăng khoảng 0,08 mAP50 cho variety, mà vẫn nhanh.
- **Hai bước** giải quyết đúng điểm yếu chính (chữ nhỏ). Cùng `imgsz=640`, dòng chữ trong vùng nhãn đã cắt có nhiều pixel hơn hẳn so với trên ảnh gốc. Bước 1 tìm nhãn gần như hoàn hảo, nên bước 2 có đầu vào đáng tin.

## 3. Dựng dataset

[yolo_data.py](solution/yolo_data.py):

1. **Đổi toạ độ.** DB lưu `{top, left, bottom, right}` theo %, YOLO cần `(x_center, y_center, width, height)` trong [0, 1]. `rect_to_box` cắt box tràn ra ngoài ảnh, tự sắp lại khi trái/phải bị đảo, và bỏ box có diện tích 0.
2. **Gom ảnh trùng.** Cùng một ảnh có thể được upload nhiều lần dưới tên khác (dữ liệu thật có 82 nhóm, 308 ảnh). Chia ngẫu nhiên theo tên file thì bản sao rơi vào cả train lẫn test, và điểm test bị thổi phồng. `dhash` cho cùng một giá trị với ảnh bị nén lại hay đổi kích thước.
3. **Chia split theo nhóm, bằng hàm băm.** `assign_split(group)` là hàm thuần của khoá nhóm, không dùng `random.shuffle`. Vì vậy dataset bước 2 dựng từ cùng manifest luôn có cùng split với bước 1, và chạy lại bao nhiêu lần cũng ra cùng kết quả.
4. **Bước 2:** box variety/vintage được đổi sang toạ độ vùng cắt (`box_to_crop`), giữ lại nếu ít nhất 60% diện tích nằm trong vùng cắt. Vùng cắt không có box chữ nào thì bỏ: thiếu box thường có nghĩa là **chưa gán nhãn**, không có nghĩa là nhãn không in chữ đó, nên không dùng làm mẫu âm.

## 4. Kết quả

Train lại cả hai bước trên split theo nhóm ở mục 3 (11/2026, một GPU L4, hai bước chạy song song):

- Bước 1: 7 270 ảnh có box, chia train 5 145 / val 1 033 / test 1 092. Dừng sớm ở epoch 88 (tốt nhất ở epoch 68), mất 1,5 giờ.
- Bước 2: 4 431 vùng nhãn đã cắt, chia 3 132 / 644 / 655, cùng split với bước 1. Dừng ở epoch 72 (tốt nhất ở epoch 52), mất 1 giờ.

### 4.1. Từng bước, trên tập test của chính bước đó

| Bước | Class | P | R | mAP50 | mAP50-95 |
|---|---|---|---|---|---|
| 1 (ảnh gốc) | label | 0,975 | 0,970 | 0,992 | 0,942 |
| 1 (ảnh gốc) | variety | 0,898 | 0,742 | 0,822 | 0,674 |
| 1 (ảnh gốc) | vintage | 0,878 | 0,891 | 0,920 | 0,724 |
| 2 (vùng nhãn) | variety | 0,921 | 0,876 | **0,924** | **0,755** |
| 2 (vùng nhãn) | vintage | 0,923 | 0,909 | **0,959** | **0,762** |

Hai dòng cuối chưa so công bằng với ba dòng đầu: bước 2 được đo trên vùng cắt từ box nhãn **thật**, nên không tính trường hợp bước 1 cắt nhãn lệch hoặc không tìm thấy nhãn.

### 4.2. Cả pipeline, trên 1 092 ảnh gốc của tập test

[eval_pipeline.py](solution/eval_pipeline.py) chạy đúng logic của API rồi so box trả ra với ground truth trên ảnh gốc. Mỗi class chỉ lấy một box có độ tin cậy cao nhất, giống cách sản phẩm dùng kết quả. Box đúng khi IoU ≥ 0,5. Ảnh không có ground truth cho class nào thì không tính class đó (xem mục 7: thiếu box thường là chưa gán nhãn).

| Pipeline | Class | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|
| chỉ bước 1 | label | 1 065 | 21 | 27 | 0,981 | 0,975 |
| chỉ bước 1 | variety | 312 | 9 | 83 | 0,972 | 0,790 |
| chỉ bước 1 | vintage | 439 | 4 | 39 | 0,991 | 0,918 |
| bước 1 + 2 | variety | 343 | 11 | 52 | 0,969 | **0,868** |
| bước 1 + 2 | vintage | 440 | 5 | 38 | 0,989 | 0,921 |

(Box `label` của hai pipeline giống nhau, vì bước 2 không đổi nó.)

**Đọc kết quả:**
- Box nhãn đã giải xong: recall 0,975, mAP50 0,99.
- Bước 2 có ích cho **variety**: tìm thêm 31 dòng (recall 0,79 → 0,87), precision gần như giữ nguyên. Đây là phần lợi thật sau khi đã tính cả lỗi của bước 1. Nó nhỏ hơn mức tăng mAP50 ở mục 4.1 (0,82 → 0,92), vì hai con số ấy đo trên hai tập khác nhau.
- Với **vintage**, bước 2 gần như không thêm gì (recall 0,918 → 0,921). Dòng năm thường đã đủ to và rõ để bước 1 tự tìm.
- 52 dòng variety vẫn bị bỏ sót. Chưa xem từng ảnh nên chưa biết bao nhiêu trong số đó là lỗi model, bao nhiêu là do nhiễu gán nhãn ở mục 7.

**So với các run năm 2024** (split cũ bị rò rỉ: ba lần xáo trộn độc lập, 560 ảnh train của bước 2 là ảnh test của bước 1, ảnh trùng không được gom):

| Model | Tập đo | label | variety | vintage |
|---|---|---|---|---|
| 2024, v8s, ảnh gốc | test 1 091 ảnh | 0,993 | 0,787 | 0,912 |
| 2024, v8s, bước 2 | val 451 vùng cắt | | 0,924 | 0,979 |
| 2026, v8s, ảnh gốc | test 1 092 ảnh | 0,992 | 0,822 | 0,920 |
| 2026, v8s, bước 2 | test 655 vùng cắt | | 0,924 | 0,959 |

Dù split mới sạch hơn, bước 1 vẫn **tốt hơn** bản cũ, nhất là variety (+0,035 mAP50). Nhiều khả năng là nhờ sửa config (mục "So với bản cũ"): `box` về mặc định, `fliplr=0`. Chưa có thí nghiệm tách riêng từng thay đổi. Vintage của bước 2 thấp hơn bản cũ một chút (0,979 → 0,959), vì bản cũ đo trên val và có rò rỉ.

## 5. So với con số bên công bố mô hình

Ultralytics công bố YOLOv8s đạt **mAP50-95 = 44,9** trên COCO val2017 (YOLOv8n: 37,3). Không thể so trực tiếp với kết quả ở mục 4:
- **Dữ liệu khác:** COCO có 80 loại vật thể đời thường. Ở đây có 3 loại, một trong số đó là vật thể lớn, rõ ràng.
- **Thước đo khác:** mục 4 báo mAP50 (IoU ≥ 0,5). Con số của COCO là mAP50-95, trung bình trên 10 ngưỡng IoU, nên luôn thấp hơn nhiều.
- Con số công bố cho biết khả năng của **kiến trúc** trên một benchmark chung, và giúp chọn giữa n/s/m. Muốn biết model có đủ tốt cho **sản phẩm** hay không, phải đo trên dữ liệu của chính bài toán, với thước đo của sản phẩm (xem mục 7).

## 6. API

[api.py](solution/api.py): `POST /predict` nhận ảnh, trả box theo pixel của ảnh gốc.

```bash
curl -F image=@chai.jpg localhost:8000/predict
{"width": 600, "height": 900, "detections": [
  {"class": "label",   "confidence": 0.97, "bbox_xyxy": [120.0, 300.5, 480.2, 760.0]},
  {"class": "vintage", "confidence": 0.88, "bbox_xyxy": [260.1, 690.0, 330.4, 712.3]}]}
```

- Có model bước 2 thì API cắt nhãn có độ tin cậy cao nhất, detect trong đó, rồi cộng lại gốc toạ độ của vùng cắt. Kết quả variety/vintage của bước 2 thay cho kết quả của bước 1.
- Từ chối file không phải ảnh (400) và ảnh quá 10 MB (413).
- Model được nạp một lần (`lru_cache`) và inject qua `Depends`. Test thay model bằng detector giả, nên kiểm tra được toàn bộ logic API mà không cần weights hay GPU.

## 7. Giới hạn: detector mới làm được một nửa bài toán

YOLO chỉ trả lời "dòng chữ giống nho **nằm ở đâu**". Người dùng cần biết **"Merlot", 2019**, nên vẫn phải thêm OCR rồi chuẩn hoá về danh sách giống nho. Thước đo đúng của sản phẩm là **tỉ lệ đọc đúng chữ**, không phải mAP của box.

Dữ liệu cũng có nhiễu cần xử lý trước khi train lại:
- Năm thành lập bị gán nhầm là vintage (ví dụ "FUNDADA EN 1877"): chỉ nên giữ năm trong khoảng hợp lý.
- Nhiều nhãn có in giống nho nhưng không được gán `variety_rect`. Model học rằng dòng chữ đó là nền, nên recall variety bị kéo xuống.

Vì những lý do này, sản phẩm thật dùng VLM (Qwen-VL, mục 1) để tìm và đọc chữ trong một bước, và kết quả đọc nhãn khá chuẩn. Bài này vẫn có giá trị như bài tập train detector: dựng dataset, chia split không rò rỉ, đo đúng cái mà API trả cho người dùng.

## So với bản cũ

| Bản cũ (notebook 12/2024) | Bản mới |
|---|---|
| Chia dữ liệu 3 lần, mỗi lần xáo trộn độc lập, nên rò rỉ giữa các bước. Ảnh trùng không được gom | Một manifest; split là hàm băm của nhóm ảnh trùng |
| Tham số viết trong file yaml nhưng không có tác dụng: `class_weights`, `hyp: {fl_gamma, obj}` (của YOLOv5), file config truyền nhầm vào `data=`. Run "focal loss" thực chất chỉ là train tiếp với tham số mặc định | Config chỉ gồm key hợp lệ, truyền thẳng `YOLO.train(**cfg)`, nên key sai tên sẽ báo lỗi ngay |
| `box=0.05` (thang của YOLOv5) làm box loss nhỏ đi 150 lần so với mặc định 7,5 của v8 | Dùng mặc định |
| `fliplr=0.5` (mặc định) lật ngang ảnh có chữ | `fliplr=0` |
| Bỏ mọi box variety/vintage chạm mép vùng cắt | Giữ box nếu ít nhất 60% nằm trong vùng cắt |
| API Flask, chỉ bước 1, nạp model khi import, bắt mọi lỗi thành 500 | FastAPI hai bước, kiểm tra đầu vào, có test |
| Chỉ có mAP của từng bước, đo trên các tập khác nhau | Thêm đo toàn bộ pipeline trên ảnh gốc của cùng tập test |
| Weights `best.pt` nằm trong repo | Weights không đưa vào repo public |
