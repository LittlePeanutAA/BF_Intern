# Bài 11: Phát hiện nhãn rượu trên ảnh chai

**Mục tiêu:** đi trọn một bài toán object detection trên dữ liệu thật: khảo sát mô hình, chọn mô hình có lý do, dựng dataset đúng cách, huấn luyện, đánh giá, và đóng gói thành API.

## Bài toán

**Đầu vào:** ảnh chụp một chai rượu.

**Đầu ra:** toạ độ các vùng sau trên ảnh:

| Mức | Vùng | Tên trong DB |
|---|---|---|
| 1 | nhãn rượu trên thân chai | `label_rect` |
| 2 (tuỳ chọn) | dòng chữ ghi giống nho (variety) trên nhãn | `variety_rect` |
| 3 (tuỳ chọn) | dòng chữ ghi năm thu hoạch (vintage) | `vintage_rect` |

## Dữ liệu

Dữ liệu là ảnh nội bộ do công ty cung cấp, **không** có trong repo. Mỗi ảnh có một bản ghi trong DB, toạ độ tính theo phần trăm kích thước ảnh:

```json
{"image": "chai_0001.jpg",
 "label_rect":   {"top": 30, "left": 10, "bottom": 92, "right": 76},
 "variety_rect": null,
 "vintage_rect": {"top": 79, "left": 38, "bottom": 83, "right": 50}}
```

Khoảng 7 300 ảnh có `label_rect`, 3 200 ảnh có `vintage_rect`, 2 600 ảnh có `variety_rect`.

## Đề bài

1. **Khảo sát.** Những họ mô hình nào giải được bài toán này? Nêu ưu, nhược điểm của từng họ đối với dữ liệu này (vật thể là **dòng chữ nhỏ**, vài nghìn ảnh).
2. **Chọn mô hình** phù hợp nhất và giải thích.
3. **Dựng dataset:** đổi toạ độ trong DB sang định dạng của mô hình, chia train/val/test. Ảnh trùng (cùng một ảnh upload nhiều lần) phải nằm cùng một tập.
4. **Huấn luyện và đánh giá** trên tập test: precision, recall, mAP50, mAP50-95 cho từng class.
5. **So sánh** với độ chính xác mà bên công bố mô hình đưa ra. So sánh đó có ý nghĩa không?
6. **Đóng gói** thành API: nhận ảnh, trả về các box.

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md).

```bash
pip install -r requirements.txt
python solution/yolo_data.py --records records.jsonl --images raw/ --out wine_data/
python solution/train.py --config solution/configs/stage1_full.yaml \
    --data wine_data/full/data.yaml --project runs --name stage1
python solution/train.py --config solution/configs/stage2_label_crop.yaml \
    --data wine_data/label_crop/data.yaml --project runs --name stage2
STAGE1_WEIGHTS=runs/stage1/weights/best.pt STAGE2_WEIGHTS=runs/stage2/weights/best.pt \
    uvicorn api:app --app-dir solution
pytest -q          # chạy trên dữ liệu tự tạo, không cần ảnh thật hay GPU
```
