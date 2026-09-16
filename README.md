# HTCV Web 2.5 — Không gian làm việc

## Giao diện Web 2.5

- Tổng quan đồng bộ tông xanh đậm – trắng với màn hình đăng nhập; ba thẻ mở nhanh Sắp lịch & Đảo ca, Quét AI KPI và Chia Data.
- Menu chính ưu tiên Tổng quan và ba công cụ. Nhóm Dữ liệu & báo cáo thu gọn, tự mở khi chọn một trang trong nhóm. Quản trị tiếp tục chỉ mở khi người dùng yêu cầu.
- Điện thoại có ô **Đi đến chức năng** ngay trong trang; thanh bên tự thu gọn theo kích thước màn hình. Chuyển trang bằng menu, ô chọn hoặc thẻ mở nhanh đều đóng chế độ chỉnh sửa.
- Tiêu đề trang, thông tin chi nhánh/cập nhật, bảng, biểu mẫu và nút thống nhất. Ba công cụ có hướng dẫn theo bước. Giao dịch quỹ hiển thị bằng bảng có thể cuộn ngang trên màn hình nhỏ.
- Giữ tài khoản, quyền và cấu trúc đồng bộ hiện có. 63 kiểm thử với dữ liệu giả đạt, chặn kết nối mạng thật; đã kiểm tra thêm điều hướng di động và chế độ sáng/tối. Chưa đăng nhập vào tài khoản sản xuất hoặc kiểm tra trên điện thoại thật trong lần cập nhật này.

Bản này sửa trực tiếp trên kho `hayonha2023-hue/quanlyCVLC`, nền commit `06a2ce3597767a8e27a2e397c0c8621c7bbceee8`.

## Giao diện Web 2.4

- Công cụ quản trị đóng mặc định; bấm **Công cụ quản trị** để mở, bấm **Đóng công cụ quản trị** để về Tổng quan.
- Chọn đúng một tác vụ: duyệt tài khoản hoặc nhân sự/phân quyền. Khi quản lý nhân sự, chọn một người rồi mới hiện biểu mẫu của người đó.
- Các thao tác sửa nằm trong **Chỉnh sửa dữ liệu**; chuyển chức năng tự trở về chế độ xem.
- Đổi nền, mật khẩu, sáng/tối và đăng xuất gom vào **Tài khoản & giao diện**.
- Nền sáng, khối nội dung tách rõ, menu chọn có điểm nhấn; các cột xếp dọc trên màn hình nhỏ.

## Nhân viên xem gì?

Sau khi đăng nhập bằng tài khoản app, nhân viên xem toàn bộ các nhóm dữ liệu nghiệp vụ đã đồng bộ của chi nhánh được gán. Trang đầu là **Tổng quan**, phiên bản ở menu ghi **Web 2.4**.

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

## Ba công cụ bổ sung trong Web 2.3

- **Sắp lịch & Đảo ca**: danh sách ca sáng, chiều, 10h30 theo cấu hình app; đảo danh sách sáng/chiều; nhân viên đặc biệt tối đa hai ngày/tuần. Dùng thuật toán `ScheduleService` của app 2.0.76, chỉ đổi đồng hồ sang múi giờ Việt Nam. Tạo bản xem trước rồi bấm lưu riêng. Lưu cùng định dạng lịch V2, mốc công bằng và danh sách đầu vào của app. Giữ quyền `CHIA LỊCH TỰ ĐỘNG`, `ĐẢO TÊN CA`.
- **Quét AI KPI**: tải ảnh JPG/PNG, phân tích bằng Groq với key đã cấu hình trên app hoặc key riêng của phiên. Model `qwen/qwen3.6-27b` theo [Groq Vision](https://console.groq.com/docs/vision). Xem và tải kết quả văn bản; không tự ghi số KPI từ nhận diện AI. Có hướng dẫn dùng Gemini qua web.
- **Chia Data**: tải Excel XLS/XLSX, chọn người từ danh bạ/lịch trực hoặc nhập tên. Chia theo đúng thương và số dư như app, giữ thứ tự dòng, xuất Excel từng người trong ZIP. Cần quyền `CHIA ĐỀU SỐ LIỆU`, đã bổ sung tùy chọn này trong Quản Trị Admin. Kết quả chỉ ở phiên web, có nút dọn; không ghi các file vào ổ đĩa máy chủ hoặc Firebase.

Giao diện có ba nút mở nhanh trên Tổng quan, menu đánh dấu chức năng đang chọn, chữ và nút rõ hơn, bảng và vùng nhập tách riêng. Giữ các trang dữ liệu của 2.2.

Lưu lịch dùng [Firebase ETag / conditional PUT](https://firebase.google.com/docs/database/rest/save-data#section-conditional-requests): đọc mới quyền và dữ liệu gốc, giữ nguyên những nhánh không sửa, chỉ ghi nếu toàn bộ mốc dữ liệu vẫn khớp. Nếu ai đó sửa dữ liệu trong lúc lưu, lượt lưu bị từ chối thay vì ghi đè. Không tự lặp lại lượt lưu khi mất mạng. Cần làm mới để kiểm tra trạng thái. Kiểm tra khóa lịch và mốc lịch/tích lũy của bản xem trước trước khi ghi.

**Giới hạn:** Lập Hàng và gửi tự động qua Zalo PC vẫn trên app máy tính. Ảnh Quét AI chỉ được gửi Groq khi người dùng bấm Phân tích. Chưa chạy API AI với key thật hoặc ghi lịch vào Firebase sản xuất trong quá trình kiểm thử.

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
4. Khi Streamlit triển khai xong, menu phải ghi **Web 2.3 • Công cụ & dữ liệu nhân viên** và có **Tổng quan, Tích Lũy, Target Ngày, Danh Bạ**. Nếu vẫn ghi bản cũ, kiểm tra nhánh/commit triển khai trên Streamlit.
5. Dùng tài khoản nhân viên của một chi nhánh, so lịch, KPI và kết quả Target đã chốt trong app. Thay đổi thử một mục được phép trên app, lưu thành công rồi bấm Làm mới dữ liệu trên web.

Kho GitHub chứa mã nguồn triển khai. Kiểm tra commit và nhánh trong Streamlit Cloud để xác nhận website đã nhận đúng bản Web 2.3. Không gửi mật khẩu hoặc token vào chat.

## Kiểm tra đã thực hiện

- 61 kiểm thử tự động đạt (Streamlit AppTest và logic đồng bộ), dùng dữ liệu giả, chặn mạng thật.
- Nhân viên mở đủ trang có dữ liệu; không hiển thị bản ghi chi nhánh khác hoặc mật khẩu/khóa API.
- Lịch V2, lịch đã xóa/rỗng, lịch legacy, tích lũy, KPI app, Target Ngày có kết quả chốt.
- Làm mới nhận thay đổi, mất mạng giữ dữ liệu cũ kèm trạng thái lỗi, tài khoản bị xóa kết thúc phiên, nhịp đọc 30 giây.
- Kiểm tra lịch do hàm `_serialize_schedule_payload` trong HTCV 2.0.76 tạo ra được web đọc đúng.
- Đối chiếu hash: phần Lập Hàng của app nguyên vẹn.

Chưa kiểm thử dữ liệu sản xuất, thao tác đồng thời nhiều người, trình duyệt/điện thoại thật hoặc triển khai Streamlit Cloud. Kiểm thử tự động không chứng minh website hiện tại đã được cập nhật. Không kiểm tra hay sửa Firebase Rules trong bản này.

Chạy lại: `python -m pip install pytest` rồi `python -m pytest tests -q`.
