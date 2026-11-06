# Bài 08: Dự đoán khoản vay có được trả đủ

**Mục tiêu:** đi trọn một bài toán học máy trên dữ liệu bảng: hiểu dữ liệu, làm sạch, chống **rò rỉ dữ liệu** (data leakage), huấn luyện, đánh giá đúng cách, và diễn giải kết quả theo góc nhìn của người dùng.

## Bối cảnh

Bạn là một **nhà đầu tư thận trọng** trên LendingClub, một nền tảng cho vay ngang hàng: người vay đăng khoản vay, nhà đầu tư chọn khoản để rót tiền. Bạn chỉ muốn đầu tư vào những khoản có khả năng cao được trả đủ. Nhiệm vụ: xây mô hình dự đoán một khoản vay sẽ được trả đủ (**Fully Paid**) hay bị xoá nợ (**Charged Off**), **chỉ dựa trên thông tin có tại thời điểm quyết định cho vay**.

## Dữ liệu

- [data/loans_2007.csv](data/loans_2007.csv): 42 552 khoản vay của LendingClub giai đoạn 2007–2011, 52 cột.
- [data/LCDataDictionary.xlsx](data/LCDataDictionary.xlsx): ý nghĩa từng cột.

## Đề bài

1. **Hiểu dữ liệu.** Đọc từ điển dữ liệu, phân loại các cột: thông tin khoản vay, thông tin người vay, lịch sử tín dụng, thông tin phát sinh sau khi cho vay.
2. **Chọn nhãn.** Dùng `loan_status` làm nhãn. Chỉ giữ hai trạng thái `Fully Paid` và `Charged Off`, bỏ mọi trạng thái khác, và giải thích vì sao.
3. **Loại cột.** Bỏ các cột thuộc một trong các nhóm sau, và với mỗi cột nêu rõ nhóm của nó:
   - tiết lộ thông tin **tương lai** (chỉ biết sau khi khoản vay đã được giải ngân);
   - không ảnh hưởng tới khả năng trả nợ (ví dụ ID sinh ngẫu nhiên);
   - định dạng kém, cần làm sạch nhiều;
   - cần thêm dữ liệu hoặc xử lý nhiều mới dùng được;
   - trùng lặp thông tin với cột khác.

   Danh sách gợi ý: `id, member_id, funded_amnt, funded_amnt_inv, grade, sub_grade, emp_title, issue_d, zip_code, out_prncp, out_prncp_inv, total_pymnt, total_pymnt_inv, total_rec_prncp, total_rec_int, total_rec_late_fee, recoveries, collection_recovery_fee, last_pymnt_d, last_pymnt_amnt, pub_rec_bankruptcies, earliest_cr_line, last_credit_pull_d, desc, url`.
4. **Làm sạch.**
   - Đổi các cột dạng chuỗi về số (`"10.65%"`, `" 36 months"`, `"10+ years"`).
   - Chuẩn hoá giá trị phân loại bị nhập sai (khác chữ hoa/thường, thừa khoảng trắng).
   - Xử lý giá trị thiếu.
   - Bỏ các cột chỉ có một giá trị.
5. **Huấn luyện.** Thử ít nhất một mô hình tuyến tính và một mô hình dạng cây. So với hai mốc:
   - mô hình luôn đoán "trả đủ";
   - xếp hạng khoản vay chỉ bằng lãi suất.
6. **Đánh giá đúng cách.**
   - Tách tập test trước mọi bước học từ dữ liệu, và chỉ dùng nó một lần.
   - Chọn mô hình bằng cross-validation.
   - Dữ liệu lệch lớp (khoảng 85/15), nên **không** dùng accuracy làm thước đo chính.
7. **Diễn giải cho nhà đầu tư.** Nếu chỉ đầu tư vào x% khoản vay mà mô hình đánh giá tốt nhất, thì tỷ lệ vỡ nợ và lãi suất trung bình của danh mục là bao nhiêu? Những đặc trưng nào quan trọng nhất?

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md).

```bash
pip install -r requirements.txt
cd solution
python train.py          # khoảng 15 giây: cross-validation, đánh giá trên test, vẽ hình
python leakage_demo.py   # minh hoạ rò rỉ dữ liệu
pytest -q                # chạy từ thư mục bài 08
```
