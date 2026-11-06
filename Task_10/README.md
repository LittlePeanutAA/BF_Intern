## 1. Phân tích bài toán:

* Đây là bài toán Object Detection với nhiều level khác nhau
* Cần detect 3 loại object: nhãn rượu, tên loại rượu và năm sản xuất
* Input là ảnh chai rượu
* Output là các bounding box với tọa độ tương ứng


## 2. Các mô hình có thể giải quyết bài toán:

  a) Các mô hình single-stage:
  
  Input Image → CNN Backbone → Direct Prediction (boxes + classes)
  
  * YOLO (v5, v6, v7, v8): Tốc độ nhanh, độ chính xác khá tốt
  * SSD (Single Shot Detector): Phù hợp với object có scale khác nhau
  * RetinaNet: Xử lý tốt class imbalance

  b) Các mô hình two-stage:

  Stage 1: Input Image → CNN Backbone → Region Proposal Network (RPN)
  Stage 2: Region Proposals → ROI Pooling → Classification + Box Refinement
  
  * Faster R-CNN: Độ chính xác cao, phù hợp với object nhỏ
  * Mask R-CNN: Có thêm mask segmentation
  * Cascade R-CNN: Độ chính xác cao hơn Faster R-CNN


## 3. Lựa chọn mô hình phù hợp nhất:

Đề xuất sử dụng YOLOv8 vì các lý do:

  - Phù hợp với bài toán detect các object có cấu trúc rõ ràng như nhãn rượu
  - Tốc độ training và inference nhanh
  - Có thể fine-tune dễ dàng
  - Documentation tốt và cộng đồng lớn
  - Hỗ trợ nhiều backbone khác nhau để có thể tùy chỉnh theo dataset
  - Có thể detect object nhỏ như năm sản xuất khá tốt
