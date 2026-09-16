# HTCV Web 2.1 — Bản sửa trên quanlyCVLC

Dựa trên kho https://github.com/hayonha2023-hue/quanlyCVLC, commit `06a2ce3597767a8e27a2e397c0c8621c7bbceee8`.

## Thay đổi

- Giao diện chung mới: thanh điều hướng, màu nền/thẻ, nút thao tác rõ hơn, bố cục có điều chỉnh trên màn hình nhỏ; giữ đổi nền và giao diện sáng/tối.
- Giữ 8 chức năng Ecom, Quỹ Shop, Xem Lịch, KPI, Chia Target, Thị Trường, AI và Quản trị. Đây là bản web; không thêm tự động điều khiển Zalo PC.
- Nút làm mới dữ liệu dùng chung với HTCV. Phần web tiếp tục dùng các đường dẫn dữ liệu Firebase cũ.
- Lỗi HTTP hoặc mất kết nối dừng việc lưu và không báo thành công. Chỉ cập nhật bộ nhớ phiên sau khi máy chủ nhận ghi.
- Đổi mật khẩu/ảnh nền dùng PUT cho giá trị đơn; PATCH dùng cho đối tượng.
- Bỏ đăng nhập dự phòng bằng mật khẩu mặc định; chỉ chấp nhận mật khẩu trong tài khoản hiện có. Không tạo mới tài khoản admin khi đăng nhập.
- Chỉ quản trị tổng được chuyển chi nhánh. Nhân viên không thấy mục Quản trị; Ecom và ghi phiếu quỹ tuân theo quyền chỉnh sửa.
- Sửa ô Ecom giữ nhầm nội dung khi đổi chi nhánh. KPI không quét lẫn toàn bộ chi nhánh và không nhân sai số thập phân dạng số.
- Bổ sung đầy đủ thư viện chạy Streamlit và ảnh.

## Chạy thử trên máy

```bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Đăng nhập bằng tài khoản/mật khẩu thực tế đang được lưu. Không nhập mật khẩu vào mã nguồn hoặc gửi mật khẩu cho người khác.

## Cập nhật web đã có

1. Giữ bản sao mã đang chạy và bản sao dữ liệu trước khi triển khai.
2. Giải nén bộ mới. Đưa `app.py`, `requirements.txt`, các thư mục `services`, `views`, `.streamlit` vào đúng gốc kho `quanlyCVLC`; không tạo thêm một cấp thư mục bao ngoài.
3. Xem thay đổi rồi commit vào nhánh được Streamlit triển khai. Giữ entrypoint `app.py` và cấu hình Secrets hiện có.
4. Sau khi triển khai, kiểm tra đăng nhập, chi nhánh, các trang có dữ liệu thực tế và thử một thao tác lưu được phép. Không dùng dữ liệu thật để kiểm thử xóa.

Bộ giao này chưa được đẩy lên GitHub hoặc triển khai vào `htcvlc.streamlit.app`.

## Kiểm thử

```bat
python -m pip install pytest
python -m pytest tests -q
```

21 kiểm thử đạt: Streamlit AppTest mở đủ 8 trang, kiểm tra đăng nhập, ẩn chức năng quản trị cho nhân viên, quyền ghi Ecom/quỹ, chuyển chi nhánh, lỗi mạng/HTTP, PUT giá trị đơn, không báo lưu thành công giả, giữ dữ liệu cũ khi lưu lỗi và xử lý số KPI.

Kiểm thử dùng dữ liệu giả và chặn mạng. Không gọi Firebase thật hoặc API AI. Chưa kiểm tra bằng trình duyệt trên điện thoại, dữ liệu sản xuất, quy tắc bảo mật Firebase hoặc quá trình triển khai Streamlit Cloud. Không khẳng định mọi cấu trúc dữ liệu lịch sử đều đã được kiểm chứng. Cơ chế mật khẩu lưu trong trường `pass` được giữ để tương thích; đây không phải việc chuyển đổi sang Firebase Authentication.
