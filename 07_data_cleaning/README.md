# Bài 07: Phân tích và làm sạch dữ liệu với pandas

**Mục tiêu:** dùng pandas để khám phá một bộ dữ liệu thật: gộp nhóm, nối bảng, so sánh theo thời gian. Phần chính là xử lý **dữ liệu thiếu**: tìm, mô tả, hiểu nguyên nhân, rồi chọn cách xử lý có lý do.

## Dữ liệu

[World Happiness Report](https://worldhappiness.report/) 2015, 2016, 2017 trong [data/](data/). Mỗi file là một năm, mỗi dòng là một nước. Ý nghĩa các cột: [data/COLUMNS.md](data/COLUMNS.md).

Lưu ý: tên cột mỗi năm viết một kiểu (ví dụ `Happiness Score` và `Happiness.Score`), và mỗi năm có vài cột riêng. Đây là một phần của bài.

## Đề bài

Trả lời các câu hỏi dưới đây bằng **code, số liệu và biểu đồ**, rồi viết một **báo cáo** tổng hợp kết quả.

**Khám phá**

1. Năm 2015, yếu tố nào đóng góp nhiều nhất vào điểm hạnh phúc (`Happiness Score`)? Đọc kỹ ý nghĩa các cột trước khi chọn cách đo "đóng góp".
2. Gộp nhóm (`groupby`, `pivot_table`, `agg`) theo khu vực cho thấy những gì mà bảng từng nước không cho thấy?
3. Tính điểm hạnh phúc trung bình của từng khu vực và so với trung bình thế giới. Với từng khu vực, tính tương quan giữa mỗi yếu tố và điểm hạnh phúc, rồi so với tương quan trên toàn thế giới: các yếu tố quan trọng có giống nhau ở mọi nơi không?

**Gộp dữ liệu**

4. pandas có những cách nào để gộp hai DataFrame (`concat`, `merge` với các kiểu `how`, `join`)? Mỗi cách cho kết quả bao nhiêu dòng khi gộp 2015 với 2016, và khi nào dùng cách nào?
5. Gộp 3 năm thành **một** bảng thống nhất (tên cột chung, có cột `year`), lưu ra CSV.
6. Hạnh phúc thế giới thay đổi thế nào từ 2015 đến 2017: theo toàn thế giới, theo khu vực, và những nước thay đổi nhiều nhất?

**Dữ liệu thiếu**

7. Vẽ heatmap cho thấy vị trí các ô trống trên bảng gộp, kèm vài nhận xét ngắn.
8. Xoá hoặc điền giá trị thiếu ảnh hưởng thế nào tới phân tích?
   - Bao nhiêu phần trăm dữ liệu bị thiếu?
   - Xoá các dòng thiếu có làm mất thông tin hữu ích ở các cột khác không?
9. Ô trống có theo quy luật nào không? Vì sao chúng bị thiếu?
10. Viết báo cáo về các cách điền giá trị thiếu (ưu, nhược điểm của từng cách) và chọn cách phù hợp nhất **cho từng cột**.

### Yêu cầu nộp

- Code tái sử dụng được (hàm đọc, chuẩn hoá, gộp), tách riêng khỏi phần phân tích; có test cho phần làm sạch.
- Một script chạy lại được toàn bộ phân tích, sinh ra biểu đồ và bảng kết quả.
- Báo cáo trả lời đủ 10 câu, mỗi kết luận đi kèm con số hoặc biểu đồ làm bằng chứng.

## Lời giải

Báo cáo ở [SOLUTION.md](SOLUTION.md), code ở [solution/](solution/).

```bash
pip install -r requirements.txt
cd solution && python analyze.py      # in số liệu, ghi figures/ và results/
pytest -q                             # chạy từ thư mục bài 07
```
