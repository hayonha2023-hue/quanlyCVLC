# HTCV Web 2.2 — Cổng nhân viên xem dữ liệu app

Bản này sửa trực tiếp trên kho `hayonha2023-hue/quanlyCVLC`, nền commit `06a2ce3597767a8e27a2e397c0c8621c7bbceee8`.

## Nhân viên xem gì?

Sau khi đăng nhập bằng tài khoản app, nhân viên xem toàn bộ các nhóm dữ liệu nghiệp vụ đã đồng bộ của chi nhánh được gán. Trang đầu là **Tổng quan**, phiên bản ở menu ghi **Web 2.2**.

| Màn hình web | Nguồn app trên Firebase | Nội dung |
|---|---|---|
| Xem Lịch | `schedule_v2`, `schedule_images` | Ca sáng/chiều/10h30, nhân sự, ảnh lịch, trạng thái chốt và nhật ký sửa |
| Tích Lũy | `schedule_v2/stats` | Tổng ca, sáng, chiều, 10h30 |
| Theo Dõi KPI | `kpi/emp`, `kpi/m`, `kpi/tot`, `kpi_images` | Target gốc, thiếu/dư, target tháng, đã bán, còn thiếu/vượt, ảnh KPI |
| Target Ngày | `daily_targets/metrics`, `daily_targets/results` | Đầu vào, kết quả mỗi người, mỗi ca, từng ca/mỗi người đã chốt trên app |
| Lịch Ecom | `ecom_history` | Sáng/chiều theo ngày |
| Quỹ Shop | `quy_shop` | Thu, chi, chi riêng, tồn quỹ và chi tiết phiếu |
| Thị Trường | `market_history` | Ngày, tuyến/địa điểm, nhân viên |
| Danh Bạ | `phones` ở gốc | Danh bạ chung như trên app, có tìm kiếm |
| AI Tư Vấn | Chức năng web đã có | Giữ hội thoại của phiên web, không giả định lịch sử chat trong app đã đồng bộ |

Chi nhánh mặc định đọc ở gốc `htcv`. Chi nhánh khác đọc `htcv/shops/<shop_id>`. Danh bạ là dữ liệu chung ở gốc như app. Nhân viên không xem danh sách mật khẩu, khóa API hay trang quản trị. Việc mở đầy đủ các nhóm nghiệp vụ là theo yêu cầu người dùng; quyền chỉnh sửa vẫn giữ riêng. Admin nhánh vẫn ở nhánh được gán, quản trị tổng được chọn nhánh.

## Đồng bộ

App **Lưu → Firebase → Web đọc lại**. Trang xem tự tải lại mỗi 30 giây khi đang mở và tải ngay khi đổi trang. Có nút **Làm mới dữ liệu**, tên chi nhánh và thời điểm tải thành công. Khi mất mạng, web giữ bản vừa tải gần nhất và báo dữ liệu chưa mới; không coi cache là dữ liệu đã đồng bộ mới.

Web ưu tiên lịch V2 kể cả khi rỗng hoặc đã xóa. Không hồi sinh lịch cũ. KPI đọc `base/short/tgt/sold` đúng app; không dùng nhánh `kpi/<shop_id>/<name>` của web cũ khi đã có bảng app. Target Ngày hiển thị đúng `results` đã chốt, không tính lại bằng công thức cũ trên web. Lịch legacy có dấu `/` và KPI web cũ vẫn đọc được khi chưa có cấu trúc app mới.

Đổi/sửa trên web: những người có quyền bật **Mở phần chỉnh sửa** tại Ecom, Quỹ, Thị Trường hoặc KPI. KPI ghi đúng `shops/<shop_id>/kpi/emp/<name>` (chi nhánh mặc định không có tiền tố `shops/...`). App nhận thay đổi khi đồng bộ Firebase. Target Ngày dùng app để chốt số và công thức; bộ tính Target web cũ không còn xuất hiện để tránh ghi sai cấu trúc app.

## Phần nào chưa có dữ liệu để đưa lên web?

File **Lập Hàng**, file **Chia Data**, trạng thái gửi **Zalo PC**, ảnh đầu vào tạm của Quét AI và cấu hình **Thông báo** tùy chỉnh hiện được giữ trên máy tính, không thuộc những nhánh app gửi lên Firebase. Web không thể tự đọc các file đó từ ổ cứng. Bản này không thay đổi app hoặc ba file Lập Hàng được bảo vệ; không khẳng định đã đồng bộ các dữ liệu chỉ có trên máy. Không đổi trình duyệt thành công cụ điều khiển Zalo PC.

## Chạy thử

```bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Đưa lên link đang dùng

ZIP là bản mã nguồn; tải ZIP không tự cập nhật website. Muốn `https://htcvlc.streamlit.app/` thay đổi:

1. Giữ bản mã đang chạy để có thể quay lại.
2. Trong kho `hayonha2023-hue/quanlyCVLC`, cập nhật nội dung thư mục giải nén vào **gốc kho**, gồm `app.py`, `requirements.txt`, `services/`, `views/`, `.streamlit/config.toml`. Không bọc thêm thư mục `HTCV_WEB_2.2...` phía ngoài. Không thay Secrets của Streamlit.
3. Commit vào đúng nhánh Streamlit đã liên kết; giữ đường dẫn chạy `app.py`.
4. Khi Streamlit triển khai xong, menu phải ghi **Web 2.2 • Cổng xem dữ liệu nhân viên** và có **Tổng quan, Tích Lũy, Target Ngày, Danh Bạ**. Nếu vẫn ghi bản cũ, kiểm tra nhánh/commit triển khai trên Streamlit.
5. Dùng tài khoản nhân viên của một chi nhánh, so lịch, KPI và kết quả Target đã chốt trong app. Thay đổi thử một mục được phép trên app, lưu thành công rồi bấm Làm mới dữ liệu trên web.

Kho GitHub chứa mã nguồn triển khai. Kiểm tra commit và nhánh trong Streamlit Cloud để xác nhận website đã nhận đúng bản Web 2.2. Không gửi mật khẩu hoặc token vào chat.

## Kiểm tra đã thực hiện

- 44 kiểm thử tự động đạt (Streamlit AppTest và logic đồng bộ), dùng dữ liệu giả, chặn mạng thật.
- Nhân viên mở đủ trang có dữ liệu; không hiển thị bản ghi chi nhánh khác hoặc mật khẩu/khóa API.
- Lịch V2, lịch đã xóa/rỗng, lịch legacy, tích lũy, KPI app, Target Ngày có kết quả chốt.
- Làm mới nhận thay đổi, mất mạng giữ dữ liệu cũ kèm trạng thái lỗi, tài khoản bị xóa kết thúc phiên, nhịp đọc 30 giây.
- Kiểm tra lịch do hàm `_serialize_schedule_payload` trong HTCV 2.0.76 tạo ra được web đọc đúng.
- Đối chiếu hash: phần Lập Hàng của app nguyên vẹn.

Chưa kiểm thử dữ liệu sản xuất, thao tác đồng thời nhiều người, trình duyệt/điện thoại thật hoặc triển khai Streamlit Cloud. Kiểm thử tự động không chứng minh website hiện tại đã được cập nhật. Không kiểm tra hay sửa Firebase Rules trong bản này.

Chạy lại: `python -m pip install pytest` rồi `python -m pytest tests -q`.
