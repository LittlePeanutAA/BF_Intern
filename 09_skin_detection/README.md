# Bài 09: Đọc và cài đặt lại một bài báo: phát hiện vùng da

**Mục tiêu:** tập đọc một bài báo khoa học với con mắt phản biện, cài đặt lại phương pháp từ mô tả trong bài, rồi kiểm chứng các kết quả bài báo công bố trên dữ liệu thật.

Bài báo được chọn có chất lượng **không cao**, và đó là chủ ý: phần lớn bài báo bạn gặp ngoài thực tế cũng vậy. Kỹ năng cần luyện là tách điều bài báo *chứng minh được* khỏi điều bài báo chỉ *nói*.

## Tài liệu

- Bài báo: S. Kolkur, D. Kalbande, P. Shimpi, C. Bapat, J. Jatakia. *Human Skin Detection Using RGB, HSV and YCbCr Color Models.* ICCASP/ICMMD-2016, Advances in Intelligent Systems Research, vol. 137, 2017. Bản PDF ở [paper/kolkur2017.pdf](paper/kolkur2017.pdf) (giấy phép CC BY-NC 4.0).
- Dữ liệu: bộ **Pratheepan** mà bài báo dùng, 78 ảnh kèm mask ground truth (32 ảnh chân dung `FacePhoto`, 46 ảnh nhiều người `FamilyPhoto`). Tải bằng `python data/download.py`. Ảnh không được đưa vào repo vì bản quyền thuộc người chụp.

## Đề bài

Đọc bài báo, rồi trả lời:

1. **Bài toán.** Bài báo giải quyết bài toán gì? Đầu vào, đầu ra là gì? Bài toán này dùng để làm gì?
2. **Kết quả.** Bài báo công bố kết quả gì, đo bằng thước đo nào, trên dữ liệu nào?
3. **Phương pháp.** Mô tả chính xác thuật toán. Chỗ nào bài báo mô tả chưa rõ hoặc có lỗi, và bạn đã chọn cách hiểu nào?
4. **Cài đặt và kiểm chứng.**
   - Cài đặt thuật toán. Code phải chạy nhanh trên ảnh thật (không duyệt từng pixel bằng vòng lặp Python).
   - Chạy lại trên chính các ảnh trong bảng kết quả của bài báo. Có ra con số giống bài báo không? Nếu không, vì sao?
   - Chạy trên **toàn bộ** bộ dữ liệu. Kết quả có giữ được như bài báo công bố không?
5. **Bối cảnh.** Vì sao tác giả chọn ý tưởng này? Nó kế thừa từ những công trình nào trước đó? Có cách nào tốt hơn không? Thử ít nhất một cách khác và so sánh công bằng.

**Yêu cầu khi so sánh:** dùng cùng dữ liệu, cùng thước đo, và với phương pháp học từ dữ liệu thì ảnh dùng để đánh giá không được nằm trong dữ liệu huấn luyện.

## Lời giải

Code ở [solution/](solution/), giải thích ở [SOLUTION.md](SOLUTION.md).

```bash
pip install -r requirements.txt
python data/download.py        # khoảng 6 MB
python solution/evaluate.py    # khoảng 7 giây: bảng so sánh, ghi results/ và figures/
pytest -q
```
