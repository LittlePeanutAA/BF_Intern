# Ý nghĩa các cột

Nguồn: World Happiness Report 2015–2017 (bản trên Kaggle). Tên trong ngoặc là tên chuẩn hoá trong lời giải.

| Cột | Ý nghĩa |
|---|---|
| Country (`country`) | tên nước |
| Region (`region`) | khu vực; **không có** trong file 2017 |
| Happiness Rank (`rank`) | thứ hạng theo điểm hạnh phúc |
| Happiness Score (`score`) | điểm trung bình của câu hỏi khảo sát "hãy tự chấm cuộc sống của bạn từ 0 đến 10" |
| Economy (GDP per Capita) (`economy`) | phần điểm được giải thích bởi GDP bình quân đầu người |
| Family (`family`) | phần điểm được giải thích bởi hỗ trợ từ gia đình, bạn bè |
| Health (Life Expectancy) (`health`) | phần điểm được giải thích bởi tuổi thọ khoẻ mạnh |
| Freedom (`freedom`) | phần điểm được giải thích bởi tự do lựa chọn cuộc sống |
| Trust (Government Corruption) (`trust`) | phần điểm được giải thích bởi mức độ tin rằng chính phủ không tham nhũng |
| Generosity (`generosity`) | phần điểm được giải thích bởi sự hào phóng (quyên góp) |
| Dystopia Residual (`dystopia_residual`) | điểm của "Dystopia" (một nước giả định tệ nhất ở cả 6 yếu tố) cộng phần dư mà 6 yếu tố không giải thích được |
| Standard Error (`standard_error`) | sai số chuẩn của điểm; chỉ có năm 2015 |
| Lower/Upper Confidence Interval (`ci_low`, `ci_high`) | khoảng tin cậy 95% của điểm; chỉ có năm 2016 |
| Whisker.low/high (`ci_low`, `ci_high`) | khoảng tin cậy của điểm; chỉ có năm 2017 |
| Year (`year`) | năm báo cáo |

Các cột từ `economy` đến `dystopia_residual` **không** phải số đo gốc (không phải GDP tính bằng đô la), mà là phần điểm hạnh phúc mà mỗi yếu tố giải thích được. Vì vậy `score = economy + family + health + freedom + trust + generosity + dystopia_residual`.
