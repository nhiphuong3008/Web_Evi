# Workspace Rules for EVI Project

## 1. Quy tắc tóm tắt & tiết kiệm Quota (Project Summary First):
- **BẮT BUỘC ĐỌC ĐẦU TIÊN**: Trong mỗi phiên làm việc mới, AI phải tham chiếu ngay file [PROJECT_SUMMARY.md](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/PROJECT_SUMMARY.md) để nắm nhanh toàn bộ kiến trúc, CSDL và sơ đồ file mà không cần quét lại toàn bộ mã nguồn, giúp tiết kiệm tối đa quota.

## 2. Quy tắc ghi log lịch sử thay đổi (Changelog Logging):
- **BẮT BUỘC GHI LOG**: Mọi sửa đổi, cập nhật tính năng hay sửa lỗi sau khi hoàn thành **bắt buộc phải được ghi lại ngay vào file `changelog.md`** dưới phiên bản mới nhất.

## 3. Quy tắc lưu trữ CSDL khi Go-Live (DB-First Persistence):
- **LƯU DỮ LIỆU VÀO CSDL SQLITE (`database/evi_center.db`)**: Khi hệ thống Golive sẽ chạy **100% bằng CSDL SQLite (DB)**. Dữ liệu từ Google Sheets/Excel phi cấu trúc hiện tại chỉ dùng để test/migration ban đầu.
- **DỮ LIỆU PHI CẤU TRÚC & THAO TÁC THÊM/SỬA/XÓA**: Mọi dữ liệu phi cấu trúc từ Sheet/Excel hoặc thao tác Thêm, Sửa, Xóa từ Web/Script **bắt buộc phải được lưu trực tiếp / song song vào CSDL SQLite**.

## 4. Quy tắc lưu trữ file test:
- Tất cả các file test, script kiểm tra dữ liệu, script thử nghiệm (ví dụ: `inspect_sheets.py`, `test_parse.py`...) **bắt buộc phải được đặt trong thư mục `test/`** (`c:\Users\nhiph\OneDrive\Documents\Web_Evi\test\`).
- Tuyệt đối không tạo file script test tạm thời ngoài thư mục gốc dự án để tránh gây rác không gian mã nguồn.

## 5. Quy tắc bảo vệ các Module Cốt Lõi (Core Modules Protection):
- **BẢO VỆ TUYỆT ĐỐI TÍNH ỔN ĐỊNH KHÔNG ĐƯỢC LÀM ẢNH HƯỞNG**: Các chức năng hệ thống sau đây luôn phải giữ nguyên vẹn và ổn định:
  1. **Thêm Lớp Mới & Quản Lý Lớp**
  2. **Schedule (Thời khóa biểu)**
  3. **Syllabus (Giáo án / Tiến trình bài học 24 buổi)**
  4. **Báo Cáo Học Tập (Xuất Báo cáo Điểm danh, BTVN, PDF Report)**
  5. **Danh Sách Học Sinh (Hồ sơ 360° học sinh)**
- **THÔNG BÁO VÀ HỎI Ý KIẾN TRƯỚC**: Trừ khi có sự liên quan và liên kết bắt buộc, AI **bắt buộc phải thông báo và giải thích rõ sự liên quan với USER để xin xác nhận trước khi thực hiện bất kỳ chỉnh sửa nào** đụng chạm đến các mục trên.

## 6. Quy tắc Phân Tách Môi Trường (Local Debug vs Production Host):
- **Máy cá nhân (Local)**: Chỉ chạy trên `http://127.0.0.1:5001` phục vụ riêng cho việc phát triển, kiểm thử và debug của User. **Tuyệt đối KHÔNG mở tunnel public** (như Localtunnel, ngrok) trên máy cá nhân để tránh người dùng bên ngoài vào nhầm gây xung đột dữ liệu CSDL.
- **Production Host 24/7**: Toàn bộ người dùng chính thức (Admin, CM, Giáo viên) truy cập và làm việc 24/7 trên Cloud PythonAnywhere: `https://vicarecrm.pythonanywhere.com`.

## 7. Quy tắc Tự Động Đẩy Code Lên Host (Auto Push to Host & Deployment):
- Mỗi khi USER yêu cầu *"đẩy code lên host"*, *"cập nhật lên host"*, *"push code"*, AI **bắt buộc tự động thực hiện quy trình Git**:
  1. Tự động chạy `git add .` và `git commit -m "..."`.
  2. Tự động chạy `git push origin main` lên repo `https://github.com/nhiphuong3008/Web_Evi.git`.
  3. Cung cấp câu lệnh nhanh 1-dòng cho PythonAnywhere: `cd ~/Web_Evi/Web_Evi && git pull` kèm nhắc nhở bấm nút **Reload** trên tab Web.

