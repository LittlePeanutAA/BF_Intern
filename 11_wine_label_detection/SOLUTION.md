# Lời giải bài 11

```
solution/annotations.py     DB rect (%) -> box YOLO; dHash gom ảnh trùng; chia split theo nhóm
solution/crops.py           cắt vùng nhãn, đổi box qua lại giữa ảnh gốc và vùng cắt
solution/yolo_data.py       dựng manifest + dataset bước 1 (ảnh gốc) và bước 2 (vùng nhãn)
solution/train.py           train một bước rồi đo một lần trên test
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

Kết quả dưới đây lấy từ các run năm 2024 (Tesla T4). mAP50 theo từng class:

| Model | Tập đo | label | variety | vintage |
|---|---|---|---|---|
| v8n, ảnh gốc | val 468 ảnh | 0,988 | 0,730 | 0,907 |
| v8s, ảnh gốc | test 1 091 ảnh | 0,993 | 0,787 | 0,912 |
| v8s, vùng nhãn đã cắt (bước 2) | val 451 vùng cắt | | **0,924** | **0,979** |

**Đọc kết quả, kèm mức độ tin cậy:**
- Box nhãn đã giải xong (mAP50 khoảng 0,99).
- Variety là phần khó. Trên ảnh gốc, recall chỉ khoảng 0,55–0,71.
- Bước 2 cải thiện rõ: variety 0,79 → 0,92, vintage 0,91 → 0,98.
- **Nhưng các run này dùng split cũ, bị rò rỉ:** dữ liệu được chia ba lần với ba lần xáo trộn độc lập, nên 560 ảnh trong train của bước 2 lại là ảnh test của bước 1. Ảnh trùng cũng không được gom. Vì vậy hai dòng cuối không so sánh công bằng được với nhau, và con số thật có thể thấp hơn.
- **Chưa làm:** train lại cả hai bước trên split theo nhóm ở mục 3 (cần GPU và dữ liệu nội bộ), rồi đo **toàn bộ pipeline** trên cùng một tập test: box variety mà API trả ra (bước 1 rồi bước 2) so với ground truth trên ảnh gốc.

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

Vì những lý do này, hướng phát triển tiếp theo của dự án là dùng VLM (mục 1) để tìm và đọc chữ trong một bước.

## So với bản cũ

| Bản cũ (notebook 12/2024) | Bản mới |
|---|---|
| Chia dữ liệu 3 lần, mỗi lần xáo trộn độc lập, nên rò rỉ giữa các bước. Ảnh trùng không được gom | Một manifest; split là hàm băm của nhóm ảnh trùng |
| Tham số viết trong file yaml nhưng không có tác dụng: `class_weights`, `hyp: {fl_gamma, obj}` (của YOLOv5), file config truyền nhầm vào `data=`. Run "focal loss" thực chất chỉ là train tiếp với tham số mặc định | Config chỉ gồm key hợp lệ, truyền thẳng `YOLO.train(**cfg)`, nên key sai tên sẽ báo lỗi ngay |
| `box=0.05` (thang của YOLOv5) làm box loss nhỏ đi 150 lần so với mặc định 7,5 của v8 | Dùng mặc định |
| `fliplr=0.5` (mặc định) lật ngang ảnh có chữ | `fliplr=0` |
| Bỏ mọi box variety/vintage chạm mép vùng cắt | Giữ box nếu ít nhất 60% nằm trong vùng cắt |
| API Flask, chỉ bước 1, nạp model khi import, bắt mọi lỗi thành 500 | FastAPI hai bước, kiểm tra đầu vào, có test |
| Weights `best.pt` nằm trong repo | Weights không đưa vào repo public |
