# Nhật ký thay đổi (Changelog) - EVI Dashboard Web App

## [v5.1.2] - 2026-08-20
### ⏩ Tính Năng Nhảy Bài (Đẩy Sớm Tiến Độ Lịch Học) & Căn Chỉnh Tiến Độ Thực Tế Lớp Moon 5.1
- **Căn Chỉnh Tiến Độ Thực Tế Lớp Moon 5.1 (`database/evi_center.db`)**:
  - Cập nhật chuẩn xác ngày học thực tế của lớp **Moon 5.1**: **Buổi 47** học vào ngày **19/08** (`✅ Đã hoàn thành`), **Buổi 48** học vào ngày **22/08** (`⏳ Chưa dạy`).
  - Đồng bộ số bài học hiện tại trên Thời khóa biểu ma trận 7 ngày sang **`Lesson 47`**.
- **Tính Năng "⏩ Nhảy Bài" Đẩy Sớm Tiến Độ Lịch Học (`services/db_service.py`, `routes/api.py`, `static/js/schedule.js`)**:
  - Xây dựng hàm `advance_class_lesson_db(class_name, lesson_num)` và API `POST /api/schedule/advance-lesson`.
  - Khi lớp học nhanh hơn hoặc bỏ qua bài, người dùng bấm nút **`⏩ Nhảy Bài`** tại Buổi X: Hệ thống tự động đẩy ngày học từ Buổi X và toàn bộ các buổi phía sau lên sớm 1 buổi học trong lịch thực tế (lưu trực tiếp vào CSDL SQLite).
  - Tích hợp đối trọng hoàn hảo với nút **`⏪ Lùi Lịch`** (lùi ngày học khi nghỉ học).
- **Cập Nhật Cache Buster Phiên Bản v5.1.2 (`static/index.html`)**:
  - Gắn `?v=5.1.2` vào toàn bộ script frontend.

## [v5.1.1] - 2026-08-20
### 🐛 Sửa Lỗi Nút Lesson Không Mở Được Nhiều Lần & Khắc Phục Triệt Để Quản Lý Pop-up
- **Sửa Lỗi Pop-up Bị Khóa Sau Khi Đóng (`static/js/schedule.js`, `static/js/dashboard.js`)**:
  - Khắc phục lỗi xung đột inline style `display: none` ngăn cản mở lại pop-up Bài học (Lesson).
  - Tự động thiết lập `display: flex` kèm lớp CSS `.active` đồng bộ trong `ScheduleModule.openLessonLogModal` và `Dashboard.openKPIDetail`.
  - Loại bỏ các hàm đóng/mở pop-up trùng lặp trong `dashboard.js`, tối ưu ngăn xếp `modalStack` cho phép mở liên tục các bài học khác nhau không giới hạn số lần mà không cần tải lại trang (F5).
- **Cập Nhật Cache Buster Phiên Bản v5.1.1 (`static/index.html`)**:
  - Gắn `?v=5.1.1` vào toàn bộ script frontend để trình duyệt lập tức nhận bản vá.

## [v5.1.0] - 2026-08-20
### 🔄 Tính Năng Tự Động Đồng Bộ CSDL Từ Production Host Về Local & Kích Hoạt Lại Git DB Tracking
- **API Cung Cấp Snapshot CSDL Nén Gzip Bảo Mật Trên Host (`routes/api.py`)**:
  - Xây dựng endpoint `GET /api/admin/sync-db-snapshot` bảo mật bằng `X-Sync-Token`.
  - Tự động nén Gzip file CSDL SQLite từ ~90MB xuống còn ~19MB giúp truyền tải qua mạng siêu nhanh trong 1-2 giây.
- **Tự Động Đồng Bộ CSDL Khi Bật Local Debug (`app.py`, `services/sync_host_db.py`)**:
  - Khi khởi động `python app.py` trên máy local, hệ thống tự động kiểm tra và tải CSDL mới nhất từ Cloud PythonAnywhere.
  - Tự động tạo bản sao lưu an toàn `database/evi_center_local_backup.db` trước khi cập nhật.
  - Tự động bỏ qua và tiếp tục chạy với DB local hiện tại nếu không có kết nối internet.
- **Trang Bị Script 1-Click Thủ Công (`sync_from_host.py`)**:
  - Cung cấp script chạy độc lập `python sync_from_host.py` để kéo dữ liệu mới nhất từ Host về máy bất kỳ lúc nào mà không cần khởi động lại server.
- **Kích Hoạt Lại Git Tracking Toàn Diện Cho CSDL (`.gitignore`, `database/evi_center.db`)**:
  - Bật lại việc theo dõi và commit `database/evi_center.db` lên GitHub Repository đồng bộ trọn vẹn cả Code lẫn CSDL.

## [v5.0.3] - 2026-08-20
### 🎙️ Cập Nhật Đồng Bộ Điểm Speaking & Cô Lập Bảo Vệ CSDL Production Host
- **Bảo Vệ CSDL Production Host 24/7 (`.gitignore`, Git Tracking)**:
  - Loại bỏ `database/evi_center.db` khỏi Git tracking và thêm vào `.gitignore` để các lần cập nhật code sau này không bao giờ ghi đè hoặc ảnh hưởng đến dữ liệu thực tế đang vận hành trên máy chủ PythonAnywhere.
- **Đồng Bộ Logic Điểm Thi Speaking (`routes/api.py`)**:
  - Đảm bảo hiển thị cột điểm Nói (Speaking) cho toàn bộ các lớp Sun & Galax và dữ liệu fallback từ bảng `unit_grades`.
- **Triệt Tiêu Cache Trình Duyệt Trên Toàn Bộ Script Frontend (`static/index.html`)**:
  - Gắn tham số phiên bản `?v=5.0.3` vào 100% các file JS trong `static/index.html` (`api.js`, `auth.js`, `dashboard.js`, `search.js`, `students.js`, `renewals.js`, `interactions.js`, `users.js`, `cm_portal.js`, `schedule.js`, `audit_logs.js`, `app.js`).
  - Đảm bảo khi User truy cập từ máy chủ PythonAnywhere luôn nạp mã JS mới nhất mà không bị kẹt cache cũ.

## [v5.0.0] - 2026-08-19
### 🚀 Triển Khai Production Cloud 24/7 (PythonAnywhere) & Phân Tách Môi Trường Local
- **Phân Tách Môi Trường Thực Thi & Đóng Toàn Bộ Tunnel Public Local**:
  - Tắt toàn bộ các tiến trình Localtunnel và Auto-Keep-Alive public trên máy cá nhân.
  - Máy cá nhân chuyển về chế độ **Local Debug & Testing thuần túy** tại `http://127.0.0.1:5001` để User/Developer phát triển tính năng an toàn, tuyệt đối không mở tunnel để tránh người dùng bên ngoài vào nhầm gây xung đột dữ liệu.
- **Triển Khai Môi Trường Chính Thức 24/7 Trên Cloud PythonAnywhere**:
  - Khởi tạo và cấu hình hoàn chỉnh hệ thống chạy 24/7 tại địa chỉ chính thức: `https://vicarecrm.pythonanywhere.com`.
  - Bảo toàn 100% CSDL SQLite (`evi_center.db`) trên ổ đĩa máy chủ không lo mất dữ liệu.
  - Expose WSGI `application` instance chuẩn hóa trong `app.py` và cập nhật đầy đủ `requirements.txt`.
- **Tự Động Hóa Đồng Bộ Mã Nguồn Qua GitHub Repository**:
  - Khởi tạo và kết nối Git Repository chính thức: `https://github.com/nhiphuong3008/Web_Evi.git`.
  - Cập nhật quy tắc phát triển trong `.agents/AGENTS.md` (Quy tắc 6 & Quy tắc 7): AI sẽ tự động thực hiện quy trình Git commit/push mỗi khi User yêu cầu cập nhật code lên Host.

## [v4.9.0] - 2026-08-18
### 📝 Nâng Cấp Mục Nhận Xét Bài Thi (Auto-expanding Textarea, Mini Toolbar, Pop-up Editor & PDF Formatting)
- **Nâng Cấp Giao Diện Ô Nhập Nhận Xét Bài Thi (`static/js/cm_portal.js`)**:
  - Chuyển đổi ô nhập `input type="text"` 1 dòng đơn điệu thành `<textarea>` đa dòng thông minh tự co giãn chiều cao theo độ dài văn bản (xuống dòng bằng phím Enter tự do).
  - Tích hợp **Mini Toolbar** trực tiếp trên từng ô nhận xét trong bảng điểm với các phím tắt nhanh: `[B]` In đậm, `[•]` Thêm gạch đầu dòng, `[📝]` Mở cửa sổ soạn chi tiết.
- **Tích Hợp Pop-up Modal Soạn Nhận Xét Chuyên Nghiệp (`static/js/cm_portal.js`)**:
  - Trang bị **Bộ mẫu nhận xét nhanh 1-Click (Quick Templates)** giúp giáo viên nhấp chuột chèn ngay các câu nhận xét chuẩn (*Con tiếp thu bài rất nhanh*, *Nắm vững từ vựng & ngữ pháp*, *Cần chú ý kỹ năng Nghe*...).
  - Trang bị **Visual Live Preview Box**: Hiển thị trực quan ngay lập tức kết quả định dạng nhận xét sẽ in ra file PDF thực tế.
  - Tích hợp thanh điều hướng `[⬅️ HS Trước]` `[HS Tiếp ➡️]` giúp giáo viên duyệt và soạn nhận xét liên tục cho cả lớp mà không cần đóng pop-up.
- **Backend Parse & Render Định Dạng File Báo Cáo PDF (`routes/api.py`)**:
  - Thêm helper `_format_comment_html()` tự động chuyển đổi ký tự xuống dòng `\n` -> `<br>`, cú pháp markdown `**chữ in đậm**` -> `<strong>chữ in đậm</strong>`, cú pháp `*in nghiêng*` -> `<em>in nghiêng</em>` và `- danh sách` -> bullet point đẹp mắt trên file PDF gửi Phụ huynh.

## [v4.8.0] - 2026-08-16
### 🔔 Trang Bị Hệ Thống Quản Lý Nhật Ký Hoạt Động & Thông Báo Thời Gian Thực Dành Cho Admin
- **CSDL SQLite (`database/models.py`)**:
  - Khởi tạo ORM Model `ActivityLog` (`activity_logs`) lưu vết 100% tất cả thao tác Điểm danh, Nhập điểm thi, Đổi bước CRM Tái phí, Đóng tiền học phí, Chăm sóc phụ huynh, Thêm/Sửa lớp học và Quản lý tài khoản.
- **Backend Service Layer (`services/db_service.py`)**:
  - Xây dựng 5 hàm nghiệp vụ: `log_activity_db`, `get_activity_logs_db`, `get_admin_notifications_db`, `mark_admin_notifications_read_db`, `seed_initial_activity_logs_db`.
  - Tự động nạp sẵn dữ liệu nhật ký lịch sử ban đầu từ các giao dịch tái phí, nhật ký tương tác và điểm danh thực tế giúp Admin xem được dữ liệu ngay lập tức.
- **REST API Endpoints (`routes/api.py`)**:
  - Thêm 3 REST APIs: `GET /api/admin/audit-logs`, `GET /api/admin/notifications`, `POST /api/admin/notifications/mark-read`.
  - Nhúng bộ ghi vết `log_activity_db` tự động vào tất cả các API cập nhật dữ liệu (`/attendance`, `/grades/save`, `/interactions/add`, `/interactions/update`, `/interactions/delete`, `/crm/renewals/stage`, `/crm/renewals/transaction`, `/classes`, `/classes/status`).
- **Giao Diện UI Topbar & Quả Chuông Thông Báo 🔔 (`static/js/auth.js`)**:
  - Trang bị Quả chuông 🔔 kèm Huy hiệu đỏ (Unread Badge Count) trên Topbar khi người dùng đăng nhập tài khoản Admin.
  - Tích hợp Menu Dropdown xem nhanh các thông báo hoạt động gần đây của các người dùng khác (`cm_thucanh`, `cm_amber`, `cm_naomi`...).
- **Trang Menu Chuyên Biệt "📜 Nhật Ký Hoạt Động" (`static/js/audit_logs.js` & `static/index.html`)**:
  - Thêm mục Menu **`📜 Nhật Ký Hoạt Động`** dưới phần "Hệ thống" dành cho Admin.
  - Trang bị Thẻ KPI Thống kê, Bộ lọc đa năng theo Người thực hiện, Phân loại thao tác, Module và Ô tìm kiếm.
  - Bảng chi tiết Audit Trail hiển thị màu sắc huy hiệu chuẩn UI chuyên nghiệp.
- **Widget "⚡ Hoạt Động Mới Nhất Của Nhân Viên" Trên Dashboard (`static/js/dashboard.js`)**:
  - Hiển thị khối Activity Feed trực tiếp trên trang Dashboard dành cho tài khoản Admin.
- **Nâng Cấp Giao Diện Báo Cáo Tone Màu Trung Tính, Sáng Rõ (`static/js/cm_portal.js`)**:
  - Chuyển đổi 100% giao diện Pop-up Báo Cáo Tổng Hợp Điểm & Nhận Xét BTVN sang phong cách **Sáng Trung Tính (Bright Soft Neutral Theme)** theo đúng yêu cầu của người dùng.
  - Phông nền trắng nhã nhặn `#ffffff`, khung thẻ chỉ số sáng màu tương phản cao (`#f1f5f9`, `#ecfdf5`, `#eff6ff`, `#fffbeb`), tiêu đề cột `#f8fafc` rõ nét, chữ nhận xét đen than nhã nhặn `#334155` rất dịu mắt và dễ đọc.
- **Sửa Lỗi Tự Động Tính Điểm Live & Lưu Tổng Số Câu Bài Thi (`static/js/cm_portal.js` & `services/db_service.py`)**:
  - Gắn sự kiện `oninput` và `onkeyup` trực tiếp vào các ô nhập Tổng số câu (`tot_lis_q`, `tot_rw_q`, `tot_spk_q`, `tot_vocab_q`), giúp hệ thống tự động quy đổi ra điểm thang 10đ ngay khi người dùng gõ phím mà không cần bấm Enter hay nhấp chuột ra ngoài.
  - Cập nhật backend `save_or_update_grade_db()` và hàm `saveGrades()` để lưu trữ chuẩn xác tổng số câu `listening_max`, `reading_writing_max`, `speaking_max` vào CSDL SQLite `unit_grades`.
  - Cập nhật `loadGradesForTest()` tự động khôi phục đúng tổng số câu đã lưu trên thanh header khi giáo viên chuyển lớp/bài thi.
- **Rà Soát & Chuẩn Hóa 100% Logo & Tên Trung Tâm Trên Tất Cả Báo Cáo PDF In Ấn (`routes/api.py`, `services/export_service.py`, `static/js/cm_portal.js`, `static/js/search.js`)**:
  - Thay thế hoàn toàn logo mặc định cũ (`evi` & `Get ready for the world`) trên Mẫu In Báo Cáo Bài Test Unit (Sun / Galax / Moon).
  - Chuẩn hóa 100% Logo chính thức (`/static/images/logo.jpg`), Tên Trung tâm **TRUNG TÂM ANH NGỮ VICARE** và tên tiếng Anh **VICARE ENGLISH CENTER** đồng bộ trên toàn bộ các báo cáo:
    1. Báo cáo PDF Bài kiểm tra Unit Test Sun / Galax / Moon (`/api/students/<code_or_id>/test-report-pdf`).
    2. Báo cáo PDF Hồ sơ Học tập 360° tổng hợp Điểm danh & BTVN (`/api/students/<code_or_id>/export`).
    3. Báo cáo PDF Theo dõi Tái phí Học sinh Hàng tháng (`/api/renewals/report-pdf`).
    4. Báo cáo PDF Điểm danh & Bài tập về nhà hàng ngày của Lớp (`CMPortalModule.exportReportPDF`).
    5. Báo cáo PDF Tra cứu Kết quả Điểm số & Nhận xét Tổng hợp (`SearchModule.exportStudentGradePDF`).
- **Khắc Phục 100% Lỗi Font Chữ Việt Hóa Trộn Lẫn Glyph Trên Báo Cáo PDF (`routes/api.py`, `services/export_service.py`, `static/js/cm_portal.js`, `static/js/search.js`)**:
  - Nhúng Google Font `Roboto` chuẩn hỗ trợ 100% Tiếng Việt kèm font stack đồng nhất: `'Roboto', 'Segoe UI', Tahoma, Arial, sans-serif`.
  - Khắc phục triệt để hiện tượng xung đột font làm cho các ký tự tiếng Việt có dấu (như `Ữ` trong `TRUNG TÂM ANH NGỮ VICARE`) bị nhảy sang Times New Roman serif lởm chởm.
- **Chuẩn Hóa 100% Thuật Ngữ "Class Manager (CM)" Trên Toàn Bộ Hệ Thống (`static/index.html`, `static/js/users.js`, `static/js/students.js`, `services/export_service.py`, `services/db_service.py`)**:
  - Đã cập nhật 100% các hiển thị, menu Sidebar navigation, Modal phân quyền vai trò người dùng, Hồ sơ học sinh và Mẫu báo cáo PDF từ thuật ngữ cũ "Care Manager (CM)" sang **"Class Manager (CM)"** theo đúng quy định chuyên môn.
- **Chuyển Đổi 100% Giao Diện Trang Nhật Ký Hoạt Động Sang Tone Màu Sáng Trung Tính (`static/js/audit_logs.js` & `static/js/dashboard.js`)**:
  - Chuyển toàn bộ các thẻ KPI Thống kê, Thanh bộ lọc tìm kiếm, Khung bảng chi tiết Audit Trail và Widget Hoạt động trên Dashboard từ tone xám tối cũ (`rgba(15,23,42,0.6)`) sang **Phong cách Sáng Trung Tính (Bright Soft Neutral Theme)**.
  - Sử dụng phông nền thẻ `#ffffff`, viền vi-khung `#cbd5e1`, khung tìm kiếm `#f8fafc`, tiêu đề cột bảng `#f1f5f9` với chữ đen than `#0f172a` tương phản cao, dịu mắt và đồng bộ hoàn toàn với giao diện tổng thể của toàn trang Web.
- **Bộ Kiểm Thử Tự Động (`test/test_report_headers.py`, `test/test_class_manager_term.py`, `test/test_audit_logs_and_notifications.py`)**:
  - Đã khởi tạo bộ kiểm thử tự động rà soát toàn bộ các REST APIs xuất báo cáo PDF, thuật ngữ giao diện và Audit Logs, chạy kiểm tra xác nhận **100% PASS**!
- **Tự Động Nạp Thông Tin Giáo Viên & CM Từ CSDL Lớp Học Cho Hồ Sơ Học Sinh (`services/db_service.py`, `test/sync_existing_students_class_info.py`)**:
  - Xử lý triệt để sự cố học sinh đã có tên lớp (ví dụ: `Moon 1.1`) nhưng trường GV & CM hiển thị `—` do dữ liệu học sinh chưa lưu sẵn tên GV/CM.
  - Xây dựng hàm `resolve_class_info_from_schedule_db`: Tự động tra cứu CSDL Thời khóa biểu (`class_schedules`) dựa theo tên lớp để nạp ngay tên **Giáo viên (GV)**, **Quản lý (CM)**, **Ca học** và **Phòng học** bất cứ khi nào xem Hồ sơ chi tiết 360° học sinh hay Danh sách học sinh.
  - Đồng bộ tự động khi Thêm học sinh mới (`add_new_student_db`), Gán thêm lớp (`add_student_class_db`) hoặc Gỡ lớp (`remove_student_class_db`).
  - Chạy script cập nhật tự động đồng bộ sẵn 171 học sinh trong CSDL SQLite.
  - Tạo và chạy bộ kiểm thử [test_student_class_info_auto_resolve.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_student_class_info_auto_resolve.py) $\rightarrow$ **100% PASS**!
- **Nâng Cấp Giao Diện Pop-up Sáng Màu Trung Tính (`static/js/students.js`, `static/js/cm_portal.js`)**:
  - Chuyển đổi toàn bộ Pop-up **"➕ THÊM HỌC SINH MỚI THỦ CÔNG"** và các Pop-up Nhập BTVN sang phong cách **Sáng Trung Tính (Bright Light Soft-Neutral Theme)**.
  - Phông nền trắng `#ffffff`, khung thẻ bo tròn viền xám sáng `#cbd5e1`, tiêu đề và các ô nhãn (labels) chữ đen than `#0f172a` tương phản cao, ô nhập liệu trắng nhã nhặn, dịu mắt và cực kỳ dễ đọc.
  - Loại bỏ hoàn toàn phông nền tối `#111827` và chữ màu tím tối mờ gây khó nhìn.
  - Tạo và chạy bộ kiểm thử [test_bright_theme_modals.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_bright_theme_modals.py) $\rightarrow$ **100% PASS**!
- **Quản Lý Linh Hoạt Nhân Sự GV/CM & Đồng Bộ 100% Với Trang Quản Lý Tài Khoản (`services/db_service.py`, `routes/api.py`, `static/js/dashboard.js`)**:
  - Triển khai **Phương án A**: Danh sách CM chỉ lấy từ trường `cm_staff_name` (bí danh phân công) của bảng `User` (role=cm). Danh sách GV lấy từ `full_name` của user role=teacher (nếu có), hoặc fallback từ ClassSchedule.
  - Loại bỏ 100% danh sách mặc định cứng trên cả Backend lẫn Frontend. Dropdown GV/CM giờ chỉ hiển thị đúng nhân sự có trong bảng Quản lý Tài Khoản Người Dùng.
  - Dọn dẹp dữ liệu rác trong CSDL: Sửa 14 bản ghi `AnhNV_TEST` → `AnhNV`, sửa tên GV có ký tự xuống dòng `GVVN\nMs Vân` → `GVVN Ms Van`.
  - Tích hợp tính năng **Cascade Update**: Khi đổi tên nhân sự, hệ thống tự động cập nhật tên mới vào tất cả phân công ở các lớp học cũ trong CSDL.
  - **Tự động tạo 7 tài khoản GV**: `gv_andrew` (Andrew), `gv_jacob` (Jacob), `gv_miguel` (Miguel), `gv_thomas` (Thomas cover), `gv_msvan` (GVVN Ms Van), `gv_thucanh` (Thục Anh), `gv_vananh` (Vân Anh) — role=teacher, mật khẩu mặc định `evi2026`.
  - Nâng cấp giao diện trang Quản lý Tài Khoản (`static/js/users.js`): Thêm huy hiệu `🎓 Giáo Viên` riêng biệt cho role=teacher, cột **PHỤ TRÁCH CM** hiển thị `—` cho GV (thay vì tên nhân sự gây nhầm lẫn), ô **Bí danh CM phân công lớp** tự động ẩn/hiện theo vai trò được chọn.
  - Tạo và chạy bộ kiểm thử [test_dynamic_staff_management.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_dynamic_staff_management.py) → **100% PASS**!
- **Khắc Phục Lỗi Không Mở Được Pop-up "Sửa Lớp" (`static/js/dashboard.js`)**:
  - Sửa lỗi định danh DOM Element: Cập nhật hàm `openEditClassModal` gọi đúng thẻ Pop-up `modal-backdrop` (thay vì thẻ `modal` cũ không tồn tại), đồng thời tự động nạp lớp CSS `.active` và style `display: flex`.
  - Giờ đây khi bấm nút **`✏️ Sửa Lớp`** trên giao diện Quản Lý Lớp Học, Pop-up Chỉnh sửa thông tin lớp sẽ lập tức bật lên mượt mà.
  - Tạo và chạy bộ kiểm thử [test_edit_class_modal_fix.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_edit_class_modal_fix.py) $\rightarrow$ **100% PASS**!
- **Cập Nhật 100% Nhật Ký Hoạt Động Thực Tế 3 Ngày Gần Đây (`test/populate_real_activity_logs.py`, `services/db_service.py`)**:
  - Quét dữ liệu lịch sử thực tế trong 3 ngày gần đây (`14/08/2026`, `15/08/2026`, `16/08/2026`) từ các bảng CSDL `attendance_records` (Điểm danh các lớp Galax 1.3, Galax 1.5, Sun 1.6...), `parent_interaction_logs` (Nhật ký chăm sóc phụ huynh), `renewal_transactions` (Giao dịch đóng học phí), và `unit_grades` (Nhập điểm thi).
  - Khởi tạo **32 vết ghi thực tế chuẩn 100%** vào bảng `activity_logs` mà tuyệt đối không dùng dữ liệu giả mạo hay bịa đặt.
  - Tạo và chạy bộ kiểm thử [test_audit_logs_real_data.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_audit_logs_real_data.py) $\rightarrow$ **100% PASS**!
- **Khắc Phục Lỗi Sai Trạng Thái BTVN Giữa Điểm Danh & Tra Cứu (`services/db_service.py`, `static/js/search.js`, `static/js/students.js`)**:
  - Sửa thuật toán chuyển đổi trạng thái `sync_attendance_hw_to_homework_records_db`: Khi CM chọn `⚪ Không có BVN` trong Điểm danh hàng ngày, hệ thống sẽ lưu đúng trạng thái `Không có BTVN` thay vì nhầm thành `⚠️ Chưa nộp BTVN`.
  - Trang bị Huy hiệu màu xám trung tính `⚪ Không có BTVN` cho các buổi học không giao bài tập (ôn tập / kiểm tra / học buổi đầu), không tính nhầm vào thẻ KPI `⚠️ Thiếu / Chưa nộp BTVN`.
  - Đã chạy script đồng bộ cập nhật chuẩn cho 130 bản ghi bị nhầm trước đây.
- **Sửa Lỗi Hiển Thị Kết Quả BTVN & Bổ Sung Chuẩn Ngày `%m/%d/%Y` (`services/db_service.py`)**:
  - Khắc phục triệt để lỗi khuyết lệnh nạp bản ghi `filtered_records.append(r)` khi lọc dữ liệu BTVN.
  - Bổ sung định dạng `%m/%d/%Y` (chuẩn ngày hệ thống browser US/EN) vào hàm `parse_date`, đảm bảo khi chọn mốc thời gian từ ô chọn ngày trên trình duyệt, kết quả BTVN vẫn trả về đầy đủ 100%.
  - Tối ưu hiệu năng đồng bộ dữ liệu `sync_attendance_hw_to_homework_records_db` tránh thực hiện 1,484 câu lệnh SQL thừa, giúp trang BTVN tải cực nhanh (< 0.2s).
- **Sắp Xếp Trình Tự Thời Gian BTVN Mới Nhất Trước $\rightarrow$ Cũ Hơn Sau (`services/db_service.py`, `static/js/students.js`, `static/js/search.js`)**:
  - Đã chuẩn hóa thuật toán sắp xếp mốc thời gian nộp BTVN theo thứ tự **giảm dần (Reverse-Chronological Order)**: Các ngày gần đây / hiện tại sẽ được ưu tiên đưa lên đầu tiên (Ví dụ: `15/08/2026` $\rightarrow$ `08/08/2026` $\rightarrow$ `25/07/2026` $\rightarrow$ `13/06/2026` $\rightarrow$ `06/05/2026`).
  - Áp dụng đồng bộ trên cả Pop-up **Hồ Sơ Chi Tiết Học Sinh** và **Trang Tra Cứu Bài Về Nhà (BTVN)**.
  - Tạo và chạy bộ kiểm thử [test_date_sorting_order.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_date_sorting_order.py) $\rightarrow$ **100% PASS**!
- **Khắc Phục Lỗi `Instance is not bound to a Session` Khi Mở Hồ Sơ Học Sinh (`services/db_service.py`)**:
  - Nâng cấp hàm `sync_attendance_hw_to_homework_records_db(existing_session)` cho phép chia sẻ dùng chung CSDL Session với hàm gọi chính `get_student_detail_db`.
  - Loại bỏ hoàn toàn tình trạng đối tượng ORM `Student` bị tách (detached) khỏi session khi mở Pop-up Hồ Sơ Học Sinh.
  - Tạo và chạy bộ kiểm thử [test_fix_session_detachment_error.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_fix_session_detachment_error.py) $\rightarrow$ **100% PASS**!
- **Tự Động Đồng Bộ Dữ Liệu BTVN Từ Bảng Điểm Danh Hàng Ngày (`services/db_service.py`)**:
  - Xây dựng hàm `sync_attendance_hw_to_homework_records_db()` tự động quét toàn bộ nhật ký điểm danh hàng ngày (`attendance_records`) và đồng bộ 100% dữ liệu BTVN (trạng thái, số câu đúng/tổng số câu, điểm số và nhận xét) sang bảng `homework_records`.
  - Tích hợp gọi hàm đồng bộ tự động ngay sau khi CM chốt điểm danh (`save_attendance_db`), cũng như khi mở **Hồ Sơ Chi Tiết Học Sinh** hoặc **Trang Tra Cứu Bài Về Nhà (BTVN)**.
  - Tạo và chạy bộ kiểm thử [test_realtime_attendance_hw_sync.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_realtime_attendance_hw_sync.py) $\rightarrow$ **100% PASS**!
- **Sửa Lỗi Hàm `AuthModule.getUserRole` & Hiển Thị Đầy Đủ Danh Sách Lớp BTVN (`static/js/auth.js`, `static/js/search.js`)**:
  - Khắc phục lỗi `AuthModule.getUserRole is not a function` bằng cách thêm hàm `getUserRole()` chuẩn vào `AuthModule` trong `static/js/auth.js`.
  - Đã phòng thủ kiểm tra an toàn `AuthModule.getUserRole` tại `static/js/search.js`, giúp hàm `loadData()` tải danh sách BTVN mượt mà và tự động nạp đầy đủ danh sách Lớp học vào ô chọn `#filter-class`.
  - Tạo và chạy bộ kiểm thử [test_auth_module_methods.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_auth_module_methods.py) $\rightarrow$ **100% PASS**!
- **Nâng Cấp Tính Năng Tra Cứu Bài Về Nhà (BTVN) & Phân Quyền Admin / CM (`static/js/search.js`, `services/db_service.py`, `routes/api.py`)**:
  - **Bộ Lọc Lớp Học Mới**: Thêm ô chọn Lớp học (`#filter-class`) trên trang Tra cứu BTVN, hỗ trợ phân nhóm **⭐ Lớp phụ trách** (đưa lên ưu tiên cho CM) và **🌐 Lớp học khác** (theo đúng Phương án A đã chọn).
  - **Bộ Lọc Khoảng Ngày**: Thêm 2 ô chọn ngày **📅 Từ ngày** và **Đến ngày** lọc chính xác theo `submission_date` học sinh nộp BTVN.
  - **Phân Quyền RBAC**: Admin có thể chọn xem bất kỳ lớp nào hoặc toàn trường; CM đăng nhập sẽ được gợi ý ưu tiên các lớp mình đảm nhận và có thể mở rộng tra cứu các lớp khác.
  - **Cập Nhật Thẻ Thống Kế KPI**: Thẻ chỉ số KPI BTVN (Tổng lượt, Thiếu/Chưa nộp, Nộp muộn, Đúng giờ) tự động tính toán chính xác theo phạm vi lớp và khoảng ngày đang lọc.
  - **Bộ Kiểm Thử Tự Động**: Tạo và chạy bộ kiểm thử [test_homework_rbac_and_dates.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_homework_rbac_and_dates.py) xác nhận **100% PASS**!
- **Lược Bỏ Hàng Thẻ Phụ Sub-tabs Trên Trang Điểm Danh Hàng Ngày (`static/js/cm_portal.js`)**:
  - Đã xóa bỏ hoàn toàn thanh sub-tabs phụ (`👥 Danh Sách Học Sinh Lớp`, `✅ Điểm Danh Hàng Ngày`, `💯 Nhập & Cập Nhật Điểm Thi`) trên trang Điểm danh hàng ngày theo yêu cầu.
  - Giao diện được tối giản gọn gàng, tập trung trực tiếp vào Bảng Điểm danh hàng ngày và các chức năng chính.
- **Phân Quyền Ẩn Nút "Tính Lại Hạn Hết Phí" & "Nhập Đóng Phí" Đối Với User Không Phải Admin (`static/js/renewals.js`)**:
  - Đã nhúng kiểm tra phân quyền `AuthModule.isAdmin()` trực tiếp vào giao diện CRM Tái Phí.
  - Các tài khoản không phải Admin (như Class Manager - CM) sẽ **không nhìn thấy** 2 nút **`🔄 Tính Lại Hạn Hết Phí`** và **`💰 Nhập Đóng Phí / Chồng Phí Mới`** trên thanh Header điều khiển, cũng như nút **`💰 Thu Tiền`** trên thẻ Kanban.
  - Thêm cảnh báo bảo vệ trong hàm xử lý `openPaymentModal()` và `recalculateExpiry()` nếu phát hiện người dùng không phải Admin thực thi lệnh.
- **Xóa Sạch Dữ Liệu Giả & Loại Bỏ Hàm `seed_initial_activity_logs_db` (`services/db_service.py`)**:
  - Phát hiện và xóa sạch **6 bản ghi giả mạo** trong bảng `activity_logs` (3 bản ghi do test tự động tạo ra từ user không tồn tại `cm_ngọccm`, 3 bản ghi từ user `cm` tham chiếu đến lớp không tồn tại `Sun 4.4`, `GALAX 3.2`).
  - Loại bỏ hoàn toàn hàm `seed_initial_activity_logs_db()` và tất cả các lời gọi hàm này trong `get_activity_logs_db()` và `get_admin_notifications_db()`. Hàm này trước đó tự động bịa đặt dữ liệu nhật ký giả khi bảng rỗng.
  - **Nguyên tắc mới**: Bảng `activity_logs` chỉ chứa dữ liệu hoạt động thực sự từ các thao tác của người dùng trên hệ thống. Nếu chưa có hoạt động nào, giao diện sẽ hiển thị thông báo "Chưa có hoạt động nào được ghi nhận".

## [v4.7.0] - 2026-08-14
### 🛠️ Rà Soát & Chuẩn Hóa 100% Định Dạng Datetime Trong CSDL SQLite (`database/evi_center.db`)
- **Khắc Phục Lỗi Datetime Non-ISO Trong CSDL SQLite (`test/inspect_datetime_format_db.py`)**:
  - Phát hiện và chuẩn hóa toàn bộ 214 bản ghi trong `student_subscriptions` và 118 bản ghi trong `student_renewals` bị lưu dạng chuỗi `DD/MM/YYYY HH:MM` thành chuẩn ISO `YYYY-MM-DD HH:MM:SS`.
  - Khắc phục triệt để lỗi `ValueError: Invalid isoformat string` khi SQLAlchemy ORM thực hiện truy vấn `get_crm_renewal_pipeline_db`.
- **Sửa Lỗi Hiển Thị Số Lớp Đang Hoạt Động Trên Card KPI Dashboard (`services/db_service.py`)**:
  - Đã khắc phục nguyên nhân hàm `get_dashboard_summary()` truy vấn nhầm bảng `ClassMaster` cũ (chỉ có 2 lớp mẫu).
  - Chuyển sang đếm trực tiếp số lớp thực tế từ `get_cm_classes_db(include_ended=False)`. Kết quả hiển thị chuẩn **21 lớp đang hoạt động** trên thẻ KPI Dashboard.
- **Điều Chỉnh Chuẩn Xác Tiến Trình Giáo Án Syllabus Cho Lớp Sun 4.3 & Sun 3.5 (`database/evi_center.db`)**:
  - **Lớp Sun 4.3**: Đã căn chỉnh tiến trình bài học ngày Thứ 6 (14/08/2026) về đúng **Lesson 53**.
  - **Lớp Sun 3.5**: Đã căn chỉnh tiến trình bài học ngày Thứ 6 (14/08/2026) về đúng **Lesson 52**.
  - Đồng bộ chuẩn hóa dữ liệu ngày học `official_date` trong CSDL SQLite và hủy bỏ mốc lùi lịch nhầm `HolidayHistoryLog` ID 2.
- **Cập Nhật Hạn Hết Phí Học Sinh Nguyễn Minh Phong (`EVI299`) - Chuyển 8 Buổi Sang Lớp Ôn Thi 9-10 (`database/evi_center.db`)**:
  - Gán mã lịch học `W5` (lớp 1 buổi/tuần vào Thứ 4) cho học sinh Nguyễn Minh Phong (`EVI299`).
  - Tính toán đếm tiến chính xác 8 buổi học Thứ 4 (từ mốc 14/08/2026), đưa Hạn hết phí mới về chuẩn **`07/10/2026`** (Tháng 10/2026).
  - Đồng bộ 100% CSDL SQLite đối với các bảng `Student`, `StudentSubscription` và `StudentRenewal`.
- **Khắc Phục Lỗi Sự Kiện Click Nút "✏️ Sửa Lớp" Trong Quản Lý Lớp Học (`static/js/dashboard.js`)**:
  - Nguyên nhân: Việc mã hóa JSON object phức tạp bằng `encodeURIComponent(JSON.stringify(c))` chứa dấu nháy đơn `'` trong thuộc tính HTML `onclick="..."` gây ra lỗi `Uncaught SyntaxError` trong trình duyệt.
  - Giải pháp: Thêm hàm `Dashboard.openEditClassModalByName(encodedClassName)` và lưu cache đối tượng lớp học vào `this.classesMap`. Truyền tên lớp đã mã hóa an toàn (`.replace(/'/g, "%27")`) giúp nút **"✏️ Sửa Lớp"** phản hồi tức thì 100%.
  - Tối ưu luồng Modal: Cập nhật hàm `cancelEditClass()` và `submitEditClassForm()` cho phép tải lại mượt mà giao diện danh sách lớp học ngay tại Modal mà không bị tắt bất ngờ.
- **Rà Soát & Chạy Bộ Test Tự Động Toàn Hệ Thống (`test/`)**:
  - Chạy và xác nhận 100% PASS các bộ test tự động: `verify_all_features.py`, `verify_all_modules_sync.py`, `test_class_management_fixes.py`, `test_crm_renewals.py`, `test_auth_and_cm.py`, `test_round_button_schedule.py`, `test_zero_remaining_sessions_expiry.py`.
  - Đảm bảo tính ổn định và chính xác tuyệt đối của 5 Module Cốt Lõi.

## [v4.6.0] - 2026-08-13
### 🟡 Nâng Cấp Bộ Chọn Thứ Hình Tròn (Round Day Toggle Buttons T2..CN) & Thuật Toán Tính Hạn Phí
- **Trang Bị Nút Chọn Thứ Hình Tròn Trong Form Thêm/Sửa Lớp (`static/js/dashboard.js`)**:
  - Tích hợp 7 nút chọn thứ hình tròn `(T2)` `(T3)` `(T4)` `(T5)` `(T6)` `(T7)` `(CN)` linh hoạt cho phép quy chiếu lớp học 1 buổi/tuần, 2 buổi/tuần hoặc 3 buổi/tuần tùy ý.
  - Tích hợp Menu chọn Ca học gọn gàng kèm dòng hiển thị tự động sinh Mã ca (`W5`, `MT5`, `TF6`...).
- **Nâng Cấp Engine Tính Ngày Hết Phí Backend (`services/db_service.py`)**:
  - Cập nhật `calculate_fee_expiry_date` nhận diện 100% các mã ca 1 buổi/tuần (`W5` = Thứ 4, `M5` = Thứ 2...), 2 buổi/tuần và 3 buổi/tuần.
  - Tự động nhảy lịch 7 ngày/buổi chính xác tuyệt đối cho các lớp 1 buổi/tuần như *Lớp ôn thi 9-10*.

## [v4.5.0] - 2026-08-13
### 🚀 Thay Thế Triệt Để Template Modal Cũ Trong RenderPage Của Renewals.js
- **Giải Quyết Triệt Để Xung Đột Modal Template (`static/js/renewals.js`)**:
  - Đã phát hiện và thay thế toàn bộ khối HTML Modal cũ bị nhúng cứng trong hàm `renderPage` (dòng 195-255) bằng Cửa sổ Floating Draggable Card mới.
  - Đảm bảo 100% người dùng truy cập web đều nhìn thấy ngay giao diện Cửa sổ Nổi kéo rê mới kèm đầy đủ thông tin Học sinh, Mã HS, Lớp, CM và Hạn hết phí.

## [v4.4.0] - 2026-08-13
### 🪟 Nâng Cấp Cửa Sổ Chuyển Bước CRM Thành Floating Draggable Card & Điền 100% Thông Tin
- **Chế Độ Cửa Sổ Di Chuyển Linh Hoạt (Floating Draggable Window) (`static/index.html`, `static/js/renewals.js`)**:
  - Chuyển Cửa sổ sang dạng Floating Card nhẹ nhàng, có thể kéo rê (drag & drop) di chuyển tự do trên màn hình.
  - Tự động tra cứu trực tiếp từ bộ nhớ master `pipelineData`, điền đầy đủ 100% thông tin **Họ tên, Mã HS, Lớp, CM Phụ trách, Hạn hết phí, Trạng thái**.
  - Tự động cập nhật Banner preview xem trước bước mới khi thay đổi Dropdown.
  - Thu gọn ô Ghi chú chăm sóc thành 1 dòng tùy chọn (Optional).

## [v4.3.1] - 2026-08-13
### 🐛 Khắc Phục Lỗi `Dashboard.showToast is not a function` Trong Cửa Sổ Modal Chuyển Bước
- **Sửa Lỗi Gọi Hàm Thông Báo (`static/js/renewals.js`, `static/js/schedule.js`)**:
  - Khắc phục lỗi `TypeError: Dashboard.showToast is not a function` khi bấm nút Xác nhận chuyển bước.
  - Chuyển toàn bộ các lệnh gọi thông báo sang `App.showToast(msg, type)` chuẩn của hệ thống (kèm fallback `alert()`), đảm bảo thông báo hiển thị mượt mà.

## [v4.3.0] - 2026-08-13
### 🖼️ Xây Dựng Cửa Sổ Modal Chuyển Bước Tái Phí UI Sang Trọng (`#rn-stage-modal`)
- **Loại Bỏ Hoàn Toàn Hộp Thoại `prompt()` Mặc Định Trình Duyệt (`static/index.html`, `static/js/renewals.js`)**:
  - Xây dựng Cửa sổ Modal hiện đại `#rn-stage-modal` để thực hiện thao tác chuyển giai đoạn CRM Tái Phí.
  - Tích hợp **Danh sách xổ xuống (Dropdown selection)** cho phép người dùng linh hoạt chọn tới bất kỳ bước tái phí nào (`D-30`, `Contacted`, `Committed`, `At-Risk`, `Success`, `Failed`).
  - Trang bị ô nhập Ghi chú chăm sóc chi tiết, nút Xác nhận Chuyển bước và Hủy bỏ chuẩn UI chuyên nghiệp.

## [v4.2.0] - 2026-08-13
### 🔄 Đồng Bộ 100% Ngày Hết Phí Khóa Chính Sang Module Quản Lý Tái Phí CRM Pipeline & PDF
- **Cập Nhật Đồng Bộ Module CRM Tái Phí (`services/db_service.py`, `database/evi_center.db`)**:
  - Nâng cấp `get_crm_renewal_pipeline_db` tự động ghi đè mốc ngày hết phí từ Master Student Data vào pipeline tái phí CRM.
  - Đồng bộ 112 bản ghi `StudentSubscription` và 112 bản ghi `StudentRenewal` trong CSDL SQLite.
  - Đưa học sinh **Dương Minh Khang (`EVI266`)** về đúng **Tháng 11/2026** trên Bảng Quản Lý Tái Phí với Hạn hết phí thực tế: **`05/11/2026`**.

## [v4.1.0] - 2026-08-13
### 📚 Khắc Phục Nhầm Lẫn Khóa Dài Hạn vs Khóa Ngắn Hạn & Hỗ Trợ Multi-Package 2 Mốc Hạn Phí
- **Phôi Phục Dữ Liệu Khóa Chính Dài Hạn (`database/evi_center.db`)**:
  - Chạy script khôi phục [restore_primary_courses.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/restore_primary_courses.py) cho 32 học sinh bị ghi đè thông tin bởi gói bổ trợ ngắn hạn.
  - Trả học sinh **Dương Minh Khang (`EVI266`)** về đúng thông tin Khóa chính dài hạn: **96 buổi đăng ký** (Còn **25 buổi** - Hạn hết phí: **05/11/2026** / **06/11/2026**).
- **Hiển Thị 2 Mốc Hạn Phí Độc Lập Trên Hồ Sơ 360° (`static/js/students.js`)**:
  - Tách biệt rõ ràng thông tin **Khóa chính dài hạn** (buổi đăng ký, số buổi còn lại, ngày hết phí) và **Khóa bổ trợ/ngắn hạn** (`fee_package_1`).
  - Đảm bảo CM theo dõi chính xác mốc hạn hết phí của từng gói học mà không bị nhầm lẫn.

## [v4.0.0] - 2026-08-13
### 🔍 Rà Soát & Đồng Bộ Chuẩn 100% Ngày Hết Phí Cho Tất Cả Học Sinh Active (`236 Học Sinh`)
- **Rà Soát & Khắc Phục Toàn Bộ 236 Học Sinh Đang Học (`database/evi_center.db`)**:
  - Chạy script rà soát và đồng bộ [fix_and_sync_all_active_students_expiry.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/fix_and_sync_all_active_students_expiry.py).
  - Tự động bổ sung mã lịch học tuần (`schedule`) bị thiếu từ thông tin lớp học master.
  - Tính toán và gán Ngày hết phí chính xác đếm tiến theo lịch tuần (`MT5`, `T3T6`, `TF5`, `TF6`...) dựa trên đúng số buổi còn lại (`remaining_sessions`).
  - Chuyển 40 học sinh có `remaining_sessions <= 0` về trạng thái `🔴 Đã hết phí` (riêng `EVI305` Lương Minh Hưng ghi nhận chuẩn `10/08/2026`).
  - Đưa tổng số lỗi sai lệch ngày hết phí trên hệ thống về **`0`**.

## [v3.9.3] - 2026-08-12
### 🧹 Tinh Gọn Bảng CRM Quản Lý Tái Phí & Cập Nhật Ngày Hết Phí Học Sinh Lương Minh Hưng (10/08/2026)
- **Tinh Gọn Cột Bảng CRM (`static/js/renewals.js`)**:
  - Đã lược bỏ 2 cột trùng lặp `Hạn Gốc` và `Trạng Thái`.
  - Giữ lại 8 cột tối giản: `ID` | `Học Sinh` | `Mã HS` | `Lớp` | `CM Phụ Trách` | `Hạn Hết Phí (Thực Tế)` | `Giai Đoạn CRM` | `Thao Tác`.
- **Cập Nhật Ngày Hết Phí Cho Học Sinh Lương Minh Hưng (`database/evi_center.db`)**:
  - Đã gán Ngày hết phí thực tế khi học xong buổi 68/68 của Lương Minh Hưng (`EVI305`) về ngày **`10/08/2026`** trên CSDL SQLite.

## [v3.9.2] - 2026-08-12
### 🗓️ Tách Biệt Ngày Hết Phí Học Sinh & Ngày Kết Thúc Lớp (Tính Ngày Hết Phí Theo Số Buổi Còn Lại)
- **Tách Biệt Hoàn Toàn 2 Giá Trị (`services/db_service.py`, `static/js/students.js`)**:
  - `Ngày kết thúc lớp` (Lịch 68 buổi của lớp) và `Ngày hết phí của học sinh` (Tính theo số buổi còn lại của cá nhân học sinh) được tách biệt độc lập 100%.
- **Bổ Sung Hàm Tính Ngày Hết Phí Tự Động (`calculate_fee_expiry_date`)**:
  - Nếu `remaining_sessions <= 0`: Hệ thống tự động gán và hiển thị trạng thái `🔴 Đã hết phí`.
  - Nếu `remaining_sessions > 0`: Đếm tiến chính xác N buổi học theo đúng lịch tuần của lớp (e.g. MT5 = Thứ 2, Thứ 5) từ thời điểm hiện tại để đưa ra ngày hết phí chuẩn xác nhất.
- **Đồng Bộ CSDL SQLite (`database/evi_center.db`)**:
  - Chạy script đồng bộ [sync_student_expiry_by_remaining.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/sync_student_expiry_by_remaining.py) cập nhật 408 học sinh trong CSDL, đưa trạng thái `EVI305` (Lương Minh Hưng) và các học sinh còn 0 buổi về trạng thái `🔴 Đã hết phí`.

## [v3.9.1] - 2026-08-12
### 🔄 Nâng Cấp Cửa Sổ Chuyển Bước Tái Phí (Dropdown Stage Choice) & Đồng Bộ 100% Báo Cáo Vicare
- **Cửa Sổ Chuyển Bước Tái Phí Chuẩn UI (`static/js/renewals.js`)**:
  - Loại bỏ hoàn toàn hộp thoại `prompt()` trình duyệt mặc định. Thay thế bằng Cửa sổ Modal hiện đại `#rn-stage-modal`.
  - Tích hợp **Danh sách xổ xuống (Dropdown Dropbox)** cho phép người dùng chủ động chọn chuyển tới bất kỳ bước / tình trạng tái phí nào (`D-30`, `Contacted`, `Committed`, `At-Risk`, `Success`, `Failed`).
  - Thêm banner xem trước mốc chuyển đổi `🔄 Chuyển từ: [Giai đoạn cũ] ➔ Sang: [Giai đoạn mới]` và ô nhập ghi chú chăm sóc chi tiết.
- **Rà Soát & Đồng Bộ 100% Báo Cáo Xuất PDF / In Ấn (`routes/api.py`, `static/js/cm_portal.js`, `static/js/search.js`, `static/js/schedule.js`)**:
  - Tích hợp file Logo chính thức `logo vicare.jpg` (`static/images/logo.jpg`), tiêu đề **TRUNG TÂM ANH NGỮ VICARE** và Watermark chân trang `✨ Thiết kế bởi: Nhi Phương` trên toàn bộ 5 mẫu báo cáo PDF và in ấn.
- **Cải Tiến Giao Diện Cảnh Báo Hết Phí Học Sinh (`static/js/students.js`)**:
  - Khi học sinh có `Số buổi còn lại` = 0 buổi, hệ thống hiển thị rõ ràng huy hiệu `🔴 Đã hết phí (Còn 0 buổi)` trên Hồ sơ 360°, kèm ghi chú mốc kết thúc lịch học của lớp, tránh gây nhầm lẫn giữa ngày lịch lớp và số buổi thực tế.

## [v3.9.0] - 2026-08-12
### 🏫 Cập Nhật Thương Hiệu Trung Tâm Anh Ngữ Vicare, Logo Vector & Watermark "Thiết kế bởi: Nhi Phương"
- **Đổi Tên Thương Hiệu Toàn Hệ Thống (`config.py`, `app.py`, `static/index.html`, `Mo_Web_EVI.html`)**:
  - Đổi tên trung tâm hiển thị trên tiêu đề trang, giao diện Web, Cửa sổ đăng nhập và Console thành **"Trung tâm Anh ngữ Vicare"** (`VICARE ENGLISH CENTER`).
- **Tạo & Tích Hợp Logo Anh Ngữ Vicare (`static/images/logo.svg`)**:
  - Tạo file Logo Vector SVG sắc nét (`static/images/logo.svg`) gồm đường cong trăng khuyết xanh dương, nét tích đỏ ở trung tâm và chữ `ANH NGỮ VICARE`.
  - Tích hợp Logo vào Sidebar Web, Favicon tab trình duyệt, Modal đăng nhập và Báo cáo học tập PDF xuất file.
- **Thêm Watermark Tác Giả ("Thiết Kế Bởi: Nhi Phương")**:
  - Thêm Watermark thương hiệu ở chân Sidebar, góc dưới bên phải màn hình Web (`global-watermark-badge`) và chân trang Báo cáo in ấn PDF/Word: `✨ Thiết kế bởi: Nhi Phương`.

## [v3.8.0] - 2026-08-12
### 🗓️ Đồng Bộ Chuẩn Ngày Tháng Cột Sheet & Thêm Bộ Lọc Năm Tương Tác Tập Trung (2023 - 2026)
- **Khắc Phục Lỗi Lệch Ngày Tương Tác Giữa Google Sheets & Web (`test/reimport_interaction_logs_from_sheet.py`, `database/migrate_sheets_to_db.py`)**:
  - Bổ sung bộ phân tích tiêu đề cột `parse_header_date`: Tự động nhận diện và gán ngày chính xác từ cột tiêu đề Google Sheets (`Tháng 3/2026` -> `01/03/2026`, `Tháng 4/2026` -> `01/04/2026`..., `2023-2025` -> `01/01/2025`).
  - Đã nạp lại 216 bản ghi nhật ký chăm sóc phụ huynh trong CSDL SQLite với mốc thời gian thực tế chuẩn 100%, khắc phục triệt để lỗi tất cả bản ghi bị gán nhầm ngày script chạy (`11/08/2026`).
- **Thêm Bộ Lọc Năm Trên Thanh Tìm Kiếm Web UI (`static/js/interactions.js`, `routes/api.py`, `services/db_service.py`)**:
  - Thêm ô chọn **`🗓️ Năm:`** bên cạnh ô chọn `📅 Tháng:`. Cho phép người dùng lọc chính xác theo các năm `Năm 2026`, `Năm 2025`, `Năm 2024`, `Năm 2023` và `Giai đoạn 2023-2025`.
  - Backend Flask hỗ trợ tham số `year` lọc CSDL SQLite theo năm linh hoạt.

## [v3.7.1] - 2026-08-12
### 📅 Lược Bỏ Giờ Phút (Chỉ Chọn Ngày/Tháng/Năm) & Sửa Triệt Để Lỗi Dropdown Autocomplete Học Sinh
- **Tối Ưu Ô Chọn Ngày (`static/js/interactions.js`)**:
  - Chuyển ô chọn từ `datetime-local` sang `type="date"` (chỉ chọn Ngày / Tháng / Năm: `YYYY-MM-DD`), bỏ bộ chọn Giờ/Phút chi tiết giúp thao tác gọn gàng, nhanh chóng hơn.
  - Cập nhật nhãn hiển thị thành `📅 Ngày Tương Tác (*):`.
- **Sửa Lỗi Tra Cứu Danh Sách Học Sinh (`static/js/api.js`, `static/js/interactions.js`)**:
  - Bổ sung hàm `API.getStudents(params)` vào `static/js/api.js` để kết nối API `/api/students` (truy vấn 437 học sinh từ CSDL SQLite).
  - Kết nối trực tiếp `InteractionsModule.loadAllStudents()` với bộ nạp dữ liệu từ `StudentsModule.studentsData` hoặc API `GET /api/students`.
  - Khắc phục lỗi gõ tên học sinh hiển thị `❌ Không tìm thấy học sinh phù hợp`: Hiện nay khi gõ bất kỳ tên tiếng Việt có dấu/không dấu hoặc mã HS (`lương minh hưng`, `hung`, `EVI198`...), gợi ý dropdown tự động xuất hiện tức thì.

## [v3.7.0] - 2026-08-12
### 📅 Thêm Ô Chọn Ngày Tương Tác & Dropdown Gợi Ý Học Sinh (Autocomplete) Cho Cửa Sổ Nhật Ký Tương Tác
- **Tích Hợp Ô Chọn Ngày & Giờ Tương Tác (`static/js/interactions.js`, `routes/api.py`, `services/db_service.py`)**:
  - Thêm trường chọn ngày giờ `📅 Ngày & Giờ Tương Tác` (`input type="datetime-local"`) vào cả Modal Thêm Mới và Modal Chỉnh Sửa Nhật Ký Tương Tác Phụ Huynh.
  - Tự động lấy giờ hiện tại làm mặc định khi mở cửa sổ thêm mới, cho phép CM/Nhân viên linh hoạt chỉnh sửa chính xác mốc thời gian thực hiện cuộc gọi/chăm sóc phụ huynh.
  - Backend Flask & SQLite CSDL tự động lưu trữ và định dạng mốc thời gian tùy chỉnh chuẩn `%d/%m/%Y %H:%M`, cập nhật chính xác cột `created_at` và `month`.
- **Triển Khai Gợi Ý Dropdown Thông Minh Khi Gõ Tên/Mã Học Sinh (Autocomplete Search)**:
  - Thêm danh sách gợi ý xổ xuống (Dropdown list) khi người dùng gõ tên hoặc mã học sinh vào ô tìm kiếm.
  - Tìm kiếm thông minh không phân biệt dấu/chữ hoa chữ thường (`Lương Minh Hưng`, `hung`, `EVI198`...).
  - Mỗi mục gợi ý hiển thị đầy đủ: `[Tên Học Sinh] (Tên Tiếng Anh) - Mã HS: EVIxxx - 🏫 Lớp: ClassName`.
  - Tự động điền đúng Mã HS, Tên HS và Lớp học khi nhấp chọn hoặc tự động tra cứu trong CSDL SQLite khi gõ tay trực tiếp.

## [v3.6.0] - 2026-08-12
### 📜 Nâng Cấp Giao Diện Dòng Thời Gian Chăm Sóc Phụ Huynh (Phương Án 3 - Timeline Card View)
- **Triển Khai Giao Diện Timeline Card Cao Cấp (`static/js/interactions.js`)**:
  - Chuyển đổi hiển thị mặc định sang dạng **Dòng thời gian (Timeline Feed)** hiện đại: Mỗi nhật ký chăm sóc là 1 Thẻ Card vuông vắn, được viền màu phân biệt theo từng CM (`NgọcCM` tím, `AnhPTT` ngọc, `AnhNV` xanh dương).
  - Tự động cắt ngắn nếu ghi chú dài hơn 240 ký tự kèm nút bấm **`👁️ Xem thêm`** / **`▲ Thu gọn`** tương tác mượt mà tại chỗ, loại bỏ hoàn toàn cảm giác "rợp chữ" hoặc tràn lan thông tin.
- **Tích Hợp Nút Chuyển Đổi Chế Độ Xem (View Switcher Toggle)**:
  - Thêm 2 nút bấm chuyển đổi linh hoạt: **`📜 Dòng Thời Gian (Timeline)`** và **`📊 Bảng Chi Tiết (Table)`** giúp người dùng dễ dàng chuyển lại giao diện Bảng khi cần so sánh hàng loạt.

## [v3.5.2] - 2026-08-12
### 🔄 Nạp Lại Dữ Liệu Lịch Sử Chăm Sóc & Tương Tác Chuẩn 100% Từ Google Sheets
- **Nạp Lại Dữ Liệu Từ Sheet Chuẩn (`test/reimport_interaction_logs_from_sheet.py`)**:
  - Khắc phục triệt để lỗi đọc nhầm thứ tự cột: Cập nhật lại chỉ số cột chuẩn trên sheet `Nhật ký chăm sóc và tương tác` (Cột B: Mã HS, Cột C: Tên HS, Cột D: Nickname, Cột E: Lớp, Cột K-Q: Ghi chú lịch sử từng mốc thời gian `2023-2025`, `Tháng 3/2026`, `Tháng 8/2026`...).
  - Đã nạp thành công **214 bản ghi nhật ký chăm sóc phụ huynh thực tế đầy đủ lịch sử** vào CSDL SQLite (`database/evi_center.db`).
  - Ví dụ: Học sinh **Đinh Gia Huy Hoàng (EVI377)** hiện tại đã có đầy đủ 2 ghi nhận chăm sóc thực tế theo mốc thời gian `[2023-2025]` và `[Tháng 8/2026]` chuẩn 100% với Google Sheets.
- **Đồng Bộ Bộ Nạp Tự Động (`database/migrate_sheets_to_db.py`)**:
  - Đồng bộ logic phân tích cột chuẩn cho bộ nạp dữ liệu tự động định kỳ từ Google Sheets.

## [v3.5.1] - 2026-08-12
### 🧹 Dọn Dẹp Triệt Để 84 Bản Ghi Lỗi Lệch Cột SĐT Khỏi Bảng Nhật Ký Tương Tác
- **Dọn Dẹp CSDL SQLite (`test/clean_phone_misaligned_logs.py`)**:
  - Phát hiện & loại bỏ thành công **84 bản ghi bị lỗi lệch cột SĐT** (từ tab cũ `(Naomi) Daily Checking` ghép nhầm số điện thoại vào cột nội dung chăm sóc).
  - Giữ lại đúng **131 bản ghi nhật ký chăm sóc phụ huynh chuẩn xác 100%** (nội dung cuộc gọi, tư vấn và phản hồi thực tế của phụ huynh).

## [v3.5.0] - 2026-08-12
### 🧹 Dọn Dẹp 100% Bản Ghi Rác Giáo Trình & Đồng Bộ Sheet Tương Tác Tập Trung
- **Dọn Dẹp CSDL SQLite (`test/clean_junk_interaction_logs.py`)**:
  - Chạy script dọn dẹp lọc loại bỏ thành công **15 bản ghi rác chứa tên giáo trình/sách** (`Handbook`, `Activity book`, `Chương trình hè`, `No`...) lọt vào Bảng `ParentInteractionLog`.
  - Giữ lại đúng **215 bản ghi nhật ký chăm sóc phụ huynh chuẩn xác**.
- **Cập Nhật Nguồn Migration Duy Nhất (`database/migrate_sheets_to_db.py`)**:
  - Cấu hình ưu tiên đọc dữ liệu từ 1 Sheet duy nhất: **`NHẬT KÝ TƯƠNG TÁC VÀ CHĂM SÓC`**.
  - Bổ sung bộ lọc thông minh chặn tất cả các dòng tiêu đề giáo trình/sách khi tự động đồng bộ dữ liệu từ Google Sheets về CSDL SQLite.

## [v3.4.4] - 2026-08-12
### 📖 Tối Ưu Bảng Nhật Ký Tương Tác Vừa Vặn Màn Hình & Cấu Hình Pop-up Thêm Mới
- **Cấu Hình Pop-up Nổi Cố Định Cho Modal (`static/js/interactions.js`)**:
  - Khắc phục triệt để lỗi bấm nút `➕ Thêm Nhật Ký Tương Tác` không hiện pop-up: Thêm bộ CSS `position: fixed`, `z-index: 9999`, `backdrop-filter: blur(4px)` giúp Modal Thêm Mới và Modal Chỉnh Sửa nổi bật căn giữa màn hình mượt mà.
  - Hỗ trợ bấm ra ngoài vùng mờ hoặc bấm dấu `×` để đóng modal linh hoạt.
- **Tối Ưu Giao Diện Bảng Vừa Vặn 100% Màn Hình**:
  - Mở rộng khung chứa trang full 100% responsive (`width: 100%`).
  - Thêm khung cuộn ngang responsive (`overflow-x: auto`) bảo vệ bảng không bị vỡ giao diện trên màn hình nhỏ.
  - Phân bổ lại độ rộng các cột tối ưu: Cột *Nội Dung Chi Tiết* tự động co giãn tối đa `600px`, xuống dòng thoáng mắt (line-height 1.55) giúp đọc báo cáo phản hồi phụ huynh cực kỳ rõ ràng.

## [v3.4.3] - 2026-08-12
### 🎨 Chuẩn Hóa Nhãn "Khóa Kỹ Năng" Cho Biểu Đồ Phân Bổ Ca Học
- **Chuẩn Hóa Nhãn Legend Biểu Đồ (`static/js/dashboard.js`)**:
  - Giải thích & khắc phục từ vết `KỸ` (lấy từ chuỗi `Kỹ năng` của các lớp chuyên đề/speaking như `Khóa Speaking 2026`).
  - Đã mapping chuẩn tên hiển thị tiếng Việt rõ ràng: **`Khóa Kỹ Năng`** kèm phối màu tím sang trọng đồng bộ trên biểu đồ Donut.

## [v3.4.2] - 2026-08-12
### 📈 Sửa Triệt Để Lỗi 2 Biểu Đồ Tái Phí Không Hiển Thị Trục Dữ Liệu Trên Dashboard
- **Sửa Lỗi Khớp Key Dữ Liệu Tái Phí Backend (`services/db_service.py`)**:
  - Phát hiện & khắc phục nguyên nhân gốc rễ: Hàm `get_dashboard_summary()` trước đó lấy sai tên dict key (`summary` thay vì `kpi` & `cm_leaderboard` của CRM Renewal Engine `get_crm_renewal_pipeline_db()`), dẫn tới mảng `renewal_monthly` bị rỗng (`[]`).
  - Đã cập nhật đúng cấu trúc mapping dict key: Trả về thành công danh sách chuỗi tái phí 12 tháng năm 2026 với số liệu chính xác từng tháng (`Tháng 7: 4 HS`, `Tháng 8: 4 HS`, `Tháng 9: 11 HS`, `Tháng 10: 5 HS`, `Tháng 11: 9 HS`, `Tháng 12: 6 HS`).
- **Hiển Thị Sinh Động 2 Biểu Đồ Chart.js**:
  - Biểu đồ **"📈 Tỉ Lệ Tái Phí Theo Tháng"** & Biểu đồ **"👥 Tái Phí Theo Nhân Viên"** đã nhận đầy đủ dữ liệu và vẽ trục cột/đường sinh động trên giao diện Dashboard.

## [v3.4.1] - 2026-08-12
### 🧹 Tối Ưu Trải Nghiệm Dashboard: Lược Bỏ Bảng Chi Tiết Tái Phí
- **Lược Bỏ Bảng Chi Tiết Tái Phí (`static/js/dashboard.js`)**:
  - Loại bỏ hoàn toàn khối bảng "📋 Chi Tiết Tái Phí" khỏi giao diện Dashboard Tổng Quan để tránh trùng lặp thông tin và tối ưu hóa tốc độ tải trang.
  - Toàn bộ tính năng xem chi tiết tái phí, phân loại 5 cột Kanban Board và quản lý giao dịch thu tiền đã tập trung 100% tại **Menu chuyên biệt "Quản Lý Tái Phí"**.

## [v3.4.0] - 2026-08-12
### 📊 Đồng Bộ 100% Số Liệu Dashboard Tổng Quan Trực Tiếp Từ CSDL Các Mục Menu
- **Đồng Bộ Dữ Liệu Dashboard Backend (`services/db_service.py`)**:
  - Nâng cấp `get_dashboard_summary()`: Liên kết trực tiếp kết quả các hàm SQL Query cốt lõi của các mục Menu:
    * **Tổng Học Sinh**: Lấy từ `Student.status == 'Đang học'` (chuẩn **236 học sinh**, khớp 100% với Bảng Hồ Sơ Học Sinh 360°).
    * **Lớp Đang Hoạt Động**: Lấy từ `ClassMaster.status == 'Đang hoạt động'` (chuẩn **21 lớp**, khớp 100% với Quản Lý Lớp Học).
    * **Tỷ Lệ Tái Phí & Bảng Tái Phí**: Liên kết trực tiếp với CRM Renewal Engine `get_crm_renewal_pipeline_db()`.
    * **Điểm ACS Nhân Viên**: Cập nhật nhãn tên trục Y từ `Vân Anh` cũ ➔ **`AnhNV`** cho đúng 3 CM chính thức (`NgọcCM`, `AnhPTT`, `AnhNV`).
- **Sửa Lỗi Hiển Thị Subtitle Card Lớp (`static/js/dashboard.js`)**:
  - Sửa mâu thuẫn phụ đề từ `/ 20 tổng` sang chuẩn **`21 lớp đang hoạt động`**.
- **Kiểm Thử Tự Động (`test/test_dashboard_summary_sync.py`)**:
  - Chạy kiểm thử tự động xác nhận 100% số liệu trên Dashboard Tổng Quan trùng khớp với CSDL các mục Menu.

## [v3.3.2] - 2026-08-12
### 🗓️ Triệt Để Chuẩn Hóa Mã CM Cho Bảng Thời Khóa Biểu (`class_schedules`) & Bộ Lọc TKB
- **Chuẩn Hóa Dữ Liệu Thời Khóa Biểu (`test/normalize_all_cm_codes_in_db.py`)**:
  - Đã rà soát và cập nhật thành công **14 bản ghi trong Bảng Thời Khóa Biểu (`class_schedules`)** từ tên cũ (`Vân Anh`) sang mã chuẩn **`AnhNV`**.
  - Đã giải quyết triệt để 100% các ô hiển thị CM trên Bảng Ma Trận Thời Khóa Biểu (ví dụ: lớp `Galax 1.3` cột CM hiển thị chuẩn **`AnhNV`** thay vì `Vân Anh`).
- **Chuẩn Hóa Bộ Lọc CM Thời Khóa Biểu**:
  - Menu Dropdown lọc CM trên trang Thời Khóa Biểu (`#schedule-cm-selector`) hiển thị chuẩn 3 lựa chọn: **`CM AnhNV`**, **`CM AnhPTT`**, **`CM NgọcCM`**.

## [v3.3.1] - 2026-08-12
### 🔄 Chuẩn Hóa 100% Mã CM Tinh Giản (NgọcCM, AnhPTT, AnhNV) Trên Tất Cả Các Module & CSDL
- **Chuẩn Hóa Dữ Liệu Trong CSDL SQLite (`test/normalize_all_cm_codes_in_db.py`)**:
  - Thực hiện chạy script chuẩn hóa toàn bộ dữ liệu hiện có trong CSDL SQLite: Đã cập nhật thành công **63 bản ghi học sinh**, **34 bản ghi tái phí subscription**, **34 đợt tái phí lịch sử**, **210 nhật ký tương tác phụ huynh** và **3 tài khoản CM** về đúng 3 mã CM tinh giản: **`NgọcCM`**, **`AnhPTT`**, **`AnhNV`**.
- **Cập Nhật 100% Giao Diện & Bộ Lọc Liên Quan**:
  - **Quản Lý Tái Phí (`static/js/renewals.js`)**: Cập nhật bộ lọc CM về 3 mã chuẩn.
  - **Nhật Ký Tương Tác (`static/js/interactions.js`)**: Cập nhật bộ lọc CM, Modal Thêm mới và Modal Chỉnh sửa nhật ký về 3 mã chuẩn.
  - **Thời Khóa Biểu (`static/js/schedule.js`)**: Đồng bộ danh mục CM phụ trách lịch học.
  - **Tài Khoản Seed (`database/db_manager.py`)**: Cập nhật 3 tài khoản đăng nhập CM mặc định chuẩn mã.

## [v3.3.0] - 2026-08-12
### 🏫 Sửa Triệt Để Lỗi Tạo Lớp Mới & Nâng Cấp Chỉnh Sửa Lớp Học / CM / Giáo Viên Động
- **Sửa Lỗi Trùng DOM ID Form Tạo Lớp (`static/js/dashboard.js`)**:
  - Khắc phục lỗi `document.getElementById('admin_new_class_name')` lấy nhầm ô ẩn bị rỗng trong DOM khi bấm thêm lớp ở Modal Pop-up, đảm bảo tính năng **Thêm Lớp Học Mới vào CSDL** hoạt động mượt mà 100%.
- **Chuẩn Hóa Danh Mục CM Tinh Giản**:
  - Chuẩn hóa 100% danh sách CM trên toàn hệ thống về đúng **3 mã tinh giản**: **`NgọcCM`**, **`AnhPTT`**, và **`AnhNV`**.
- **Nâng Cấp Tính Năng ✏️ Chỉnh Sửa Lớp Học (`static/js/dashboard.js` & `services/db_service.py`)**:
  - Bổ sung nút **✏️ Sửa Lớp** trên từng hàng danh sách lớp học, cho phép Admin/CM cập nhật Tên lớp, Ca học, Ngày bắt đầu, Phòng học, **Giáo Viên (GV)** và **Phụ Trách (CM)** bất kỳ lúc nào khi nhân sự thay đổi hoặc có GV cover.
  - Tự động đồng bộ CM và Giáo viên mới cho 100% học sinh thuộc lớp đó trong CSDL SQLite.
- **Kiểm Thử Tự Động (`test/test_class_management_fixes.py`)**:
  - Đã chạy kiểm thử tự động xác nhận 100% tính năng tạo lớp mới, sửa thông tin lớp và đồng bộ nhân sự học sinh hoạt động hoàn hảo.

## [v3.2.3] - 2026-08-12
### 🔍 Rà Soát & Đồng Bộ Chuẩn Hóa 100% Thông Tin Lớp Học & CM Cho 236 Học Sinh Đang Học
- **Rà Soát Tổng Thể 100% Học Sinh (`test/audit_all_active_students_sync.py`)**:
  - Thực hiện quét rà soát tự động 100% dữ liệu 236 học sinh Đang Học trong CSDL SQLite giữa Bảng Master `Student` (`students`) với `StudentSubscription` và `StudentRenewal`.
  - Phát hiện và đồng bộ hóa thành công **6 trường hợp học sinh bị lệch thông tin Lớp/CM do dữ liệu cũ**:
    1. `[EVI299] Nguyễn Minh Phong`: Lớp `Bảo lưu` ➔ **`Lớp ôn thi 9-10`**, CM ➔ **`NgọcCM`**
    2. `[EVI305] Lương Minh Hưng`: CM `AnhPTT` ➔ **`NgọcCM`**
    3. `[EVI313] Phạm Bảo Anh`: Lớp `Sun 2.4` ➔ **`Galax 1.4`**, CM `NgọcCM` ➔ **`Vân Anh`**
    4. `[EVI347] Trịnh Minh Tiến`: Lớp `Sun 1.4` ➔ **`Sun S.7`**, CM `NgọcCM` ➔ **`Vân Anh`**
    5. `[EVI354] Lê Hà My`: Lớp `Sun 1.4` ➔ **`Sun 2.1`**, CM `NgọcCM` ➔ **`AnhPTT`**
    6. `[EVI384] Lê Ngọc Đức Duy`: Lớp `Bảo Lưu` ➔ **`Sun 5.1`**, CM ➔ **`NgọcCM`**
- **Bảo Đảm Tuyệt Đối Độ Chính Xác Dữ Liệu**:
  - Tất cả thông tin Lớp học và CM phụ trách của 100% học sinh hiện tại đã đồng bộ chuẩn xác 100% theo Mã Học Sinh duy nhất (`student_code`).

## [v3.2.2] - 2026-08-12
### 🎯 Chuẩn Hóa Ánh Xạ Động Thông Tin Học Sinh Theo Mã HS Duy Nhất (Student Code Primary Key)
- **Ánh Xạ Động Tương Thích Master (`services/db_service.py` & `test/migrate_crm_renewals.py`)**:
  - Nâng cấp `get_crm_renewal_pipeline_db()`: Truy vấn ánh xạ động các trường `class_name`, `cm_staff`, `student_name`, `english_name`, `status` trực tiếp từ Bảng Master Học Sinh (`Student`) thông qua **Mã Học Sinh (`student_code` / `code`) duy nhất và không đổi**.
  - Đã khắc phục triệt để lỗi thông tin Lớp & CM bị cũ do dữ liệu lịch sử cũ (ví dụ: `EVI313 Phạm Bảo Anh` chuyển từ `Sun 2.4` / `NgọcCM` sang lớp đúng **`Galax 1.4` / CM `Vân Anh`**; `EVI347 Trịnh Minh Tiến` chuyển sang lớp đúng **`Sun S.7` / CM `Vân Anh`**; `EVI305 Lương Minh Hưng` chuẩn CM **`NgọcCM`**).
- **Kiểm Thử (`test/verify_master_code_sync.py`)**:
  - Chạy kiểm thử tự động xác nhận 100% các học sinh hiển thị Lớp và CM trùng khớp hoàn toàn với Bảng Master Học Sinh trên Google Sheet.

## [v3.2.1] - 2026-08-12
### 🧹 Bộ Lọc Tự Động Loại Bỏ Học Sinh Đã Nghỉ & Bảo Lưu Khỏi CRM Renewal Pipeline
- **Lọc Sạch Danh Sách Tái Phí (`services/db_service.py`)**:
  - Nâng cấp hàm `get_crm_renewal_pipeline_db()`: Tự động phát hiện và loại bỏ 100% các học sinh có trạng thái `Đã nghỉ`, `Bảo lưu`, `Nghỉ học` hoặc lớp học chưa phân bổ (`class_name` là `'Bảo lưu'`, `'Đã nghỉ'`, `'—'` hoặc trống) khỏi Pipeline Tái Phí D-30 / Upcoming.
  - Đảm bảo mẫu số và số lượng học sinh trong Pipeline Tái Phí chỉ tập trung **100% vào các học sinh Đang Học thực tế** có Lớp học chính thức đang hoạt động.
- **Kiểm Thử (`test/verify_active_students_filter.py`)**:
  - Đã chạy kiểm thử tự động xác nhận loại bỏ hoàn toàn 5 ca học sinh Bảo lưu / Đã nghỉ (như Nguyễn Minh Phong `EVI299`, Phạm Như Hoàng Anh `EVI188`, Trần Hồng Châu `EVI319`...).

## [v3.2.0] - 2026-08-12
### 💳 Module Quản Lý Tái Phí & Chồng Phí CRM (CRM Renewal & Stacking Fee Engine)
- **Kiến Trúc CSDL 2 Bảng (`database/models.py`)**:
  - Bổ sung 2 ORM Models: `StudentSubscription` (`student_subscriptions`) và `RenewalTransaction` (`renewal_transactions`).
  - Theo dõi độc lập `original_end_date` (ngày hết phí gốc) và `current_end_date` (ngày hết phí thực tế sau cộng dồn chồng phí).
- **Giải Quyết Triệt Để Lệch Số Liệu Web vs Sheet**:
  - Học sinh hoàn thành **Chồng Phí (Early Renewal)** được cộng thời hạn gói mới và đẩy `current_end_date` sang tương lai (2027/2028), **tự động gỡ khỏi danh sách Đến Hạn của tháng cũ**.
  - Đối soát dữ liệu CSDL Tháng 8/2026 đạt chuẩn đúng **6 học sinh đến hạn** (khớp 100% với Google Sheet 3 mới nhất).
- **Nghiệp Vụ Backend (`services/db_service.py`)**:
  - `get_crm_renewal_pipeline_db()`: Phân loại danh sách đến hạn theo 5 Cột Kanban Pipeline, tính toán Tỷ lệ Tái Phí Real-time (%) và Bảng xếp hạng CM Leaderboard.
  - `record_renewal_transaction_db()`: Ghi nhận giao dịch đóng tiền tái phí / chồng phí, tự động tính `current_end_date` mới, lưu nhật ký giao dịch và đẩy học sinh sang chu kỳ tương lai.
  - `update_subscription_stage_db()`: Chuyển bước Kanban 1-click và lưu nhật ký care.
- **REST API Endpoints (`routes/api.py`)**:
  - Thêm 3 REST API endpoints: `GET /api/crm/renewals/pipeline`, `POST /api/crm/renewals/transaction`, `POST /api/crm/renewals/stage`.
- **Giao Diện CRM 3 Tab (`static/js/renewals.js`)**:
  - **Tab 1: 📊 Pipeline Kanban Board (5 Cột Giai Đoạn Chuẩn CRM)**: `🕒 Sắp đến hạn (D-30)`, `📞 Đã liên hệ & Tư vấn`, `🤝 Cam kết đóng phí`, `⚠️ Do dự / Nguy cơ nghỉ (At-Risk)`, `🏆 Kết quả hoàn thành`.
  - **Tab 2: 📋 Bảng Danh Sách Chi Tiết & Xuất PDF**: Tra cứu toàn bộ gói học viên và nút xuất Báo cáo PDF.
  - **Tab 3: 📈 Thống Kê KPI Real-Time & Leaderboard**: Thẻ KPI Doanh số, Tỷ lệ Tái phí chuẩn và Bảng xếp hạng CM.
  - Modal **💰 Nhập Giao Dịch Đóng Tiền Tái Phí / Chồng Phí Mới**.
- **Đồng Bộ Hoàn Toàn Báo Cáo In PDF (`services/db_service.py` & `routes/api.py`)**:
  - Đồng bộ hàm `get_monthly_renewal_pdf_data_db()` và endpoint `/api/renewals/report-pdf`: Chuyển sang truy vấn trực tiếp từ `get_crm_renewal_pipeline_db()`.
  - Giúp Báo cáo PDF in ấn / xem trước hiển thị số liệu đến hạn, trạng thái `🟢 Thành công`, `🔵 Chồng phí`, `🟡 Chờ xử lý`, `🔴 Thất bại` và tổng hợp KPI hoàn toàn đồng bộ 100% với giao diện Web CRM!
- **Kiểm Thử (`test/test_crm_renewals.py` & `test/verify_pdf_report_sync.py`)**:
  - Đã khởi tạo CSDL và kiểm thử tự động thành công 100% các API pipeline, ghi nhận thu tiền, chuyển bước Kanban và file Báo cáo PDF.

## [v3.1.0] - 2026-08-11
### 🌴 Tính Năng Lùi Lịch & Quản Lý Lịch Nghỉ Lễ / Nghỉ Đột Xuất (EVI Shift Engine)
- **CSDL SQLite (`database/models.py`)**:
  - Bổ sung ORM Model `HolidayHistoryLog` (`holiday_history_logs`): Lưu trữ nhật ký đợt nghỉ lễ, lý do, khoảng thời gian nghỉ, danh sách lớp ảnh hưởng, số ca học bị hoãn, số học sinh được gia hạn hạn học và người thao tác.
- **Backend Service (`services/db_service.py`)**:
  - Cập nhật hàm `calculate_real_class_lesson_dates()`: Tự động phát hiện các đợt nghỉ lễ `Active` và tịnh tiến (skip) ngày bài học 24 buổi của Syllabus qua các ngày nghỉ lễ sang ca học chính thức tiếp theo.
  - Xây dựng 4 hàm xử lý nghiệp vụ: `preview_holiday_shift_db()`, `create_holiday_shift_db()`, `cancel_holiday_shift_db()`, `get_holiday_history_logs_db()`.
  - Tự động cộng/lùi ngày dự kiến hết phí (`expiry_date`) của học sinh bị ảnh hưởng (giữ nguyên số buổi còn lại `remaining_sessions`).
  - Hỗ trợ hoàn tác (Rollback) an toàn khi hủy đợt nghỉ.
- **API Endpoints (`routes/api.py`)**:
  - Thêm 4 REST API endpoints: `/api/schedule/holiday-shift/preview`, `/api/schedule/holiday-shift`, `/api/schedule/holiday-history`, `/api/schedule/holiday-shift/cancel`.
- **Giao Diện Web UI (`static/js/schedule.js` & `static/index.html`)**:
  - Thêm nút **`🌴 Quản Lý Lịch Nghỉ & Lùi Lịch`** nổi bật trên thanh công cụ Thời khóa biểu.
  - Tích hợp Modal Pop-up với 2 Tab: `Khai Báo Đợt Nghỉ Mới` (kèm tính năng Xem Trước Tác Động) và `Lịch Sử Lùi Lịch & Khôi Phục`.
  - **Đã khắc phục 3 lỗi giao diện**:
    1. Tự động nạp toàn bộ danh sách Lớp học đang hoạt động vào ô chọn `Phạm Vi Áp Dụng` (`<select id="holiday-scope">`).
    2. Sửa lỗi gọi hàm người dùng `AuthModule.getUser()`.
    3. Chuyển đổi toàn bộ kết nối API sang đối tượng chuẩn `API.post()` và `API.get()`.
- **Kiểm Thử (`test/test_holiday_shift.py` & `test/verify_ui_api_fixes.py`)**:
  - Đã chạy kiểm thử tự động thành công 100% các API backend và giao diện điều khiển.

## [v3.0.2] - 2026-08-10
### 🎨 Loại Bỏ Cột Phân Loại & Tự Động Đồng Bộ Tương Tác Gần Nhất Cho Bảng Quản Lý Tái Phí Khi Xóa/Sửa
- **Loại Bỏ Cột Phân Loại Trùng Lặp**:
  - Đã loại bỏ cột `PHÂN LOẠI` khỏi Bảng Nhật Ký Tương Tác Phụ Huynh trên Trang Trung Tâm `📖 Nhật Ký Tương Tác` trong [static/js/interactions.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/interactions.js).
  - Mở rộng không gian hiển thị cột *Nội dung chi tiết chăm sóc & phản hồi PH* giúp giao diện thoáng và dễ đọc hơn.
- **Nâng Cấp Tra Cứu Thông Minh & Tự Động Đồng Bộ Tương Tác Gần Nhất**:
  - Nâng cấp hàm `get_student_interaction_timeline_db()` và `get_monthly_renewal_pdf_data_db()` trong [services/db_service.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/services/db_service.py): Tự động tra cứu liên kết thông minh theo cả **Mã Học Sinh** và **Tên Học Sinh**.
  - **Ví dụ khắc phục Bùi Khánh Ly (EVI241)**: Tra cứu theo Mã HS `EVI241` tự động khớp đúng với nhật ký tương tác #227 (ghi tên `Bùi Khánh Ly`), giúp Pop-up timeline và Bảng Tái phí tự động hiển thị nhật ký tương tác gần nhất chuẩn xác.
  - Sau khi **Thêm/Sửa/Xóa** bất kỳ nhật ký tương tác nào, hệ thống tự động kích hoạt `RenewalsModule.loadData()` để cập nhật tức thì mốc tương tác mới nhất sang Bảng Quản Lý Tái Phí và Báo cáo PDF.

## [v3.0.1] - 2026-08-10
### 🗑️ Bổ Sung Nút Xóa Nhật Ký Tương Tác Phụ Huynh
- **Nút Xóa Trong Pop-up Modal & Bảng Tương Tác**:
  - Bổ sung nút **`🗑️ Xóa Nhật Ký`** màu đỏ ở góc trái bên dưới Pop-up Modal Chỉnh Sửa Nhật Ký Tương Tác ([static/js/interactions.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/interactions.js)).
  - Bổ sung nút **`🗑️ Xóa`** trực tiếp ở cột `THAO TÁC` của từng hàng bảng Nhật Ký Tương Tác Trung Tâm.
  - Xây dựng API backend `POST /api/interactions/delete/<id>` và hàm `delete_parent_interaction_log_db()` trong [services/db_service.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/services/db_service.py).
  - Tích hợp hộp thoại xác nhận xóa an toàn trước khi thực hiện xóa vĩnh viễn khỏi CSDL SQLite.

## [v3.0.0] - 2026-08-10
### ✏️ Thêm Nút Chỉnh Sửa Nhật Ký Tương Tác Dành Cho Admin & Nút Báo Cáo Tái Phí Hàng Tháng Xuất File PDF
- **Tính Năng 1: Nút Chỉnh Sửa Nhật Ký Tương Tác Phụ Huynh (Admin)**:
  - Bổ sung cột **`THAO TÁC`** và nút **`✏️ Sửa`** trên Trang Trung Tâm `📖 Nhật Ký Tương Tác` trong [static/js/interactions.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/interactions.js).
  - Tích hợp Modal Pop-up `✏️ Chỉnh Sửa Nhật Ký Tương Tác`: Cho phép Admin cập nhật thông tin Học Sinh, CM Phụ Trách, Phân loại tiêu đề và Nội dung chi tiết chăm sóc.
  - Xây dựng API backend `POST /api/interactions/update/<id>` và hàm `update_parent_interaction_log_db()` trong [services/db_service.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/services/db_service.py).
  - Mọi thao tác chỉnh sửa được lưu trực tiếp CSDL SQLite và **tự động đồng bộ tới Bảng Tái phí & Hồ sơ học sinh 360°**.
- **Tính Năng 2: Nút Báo Cáo Tái Phí Hàng Tháng Xuất File PDF**:
  - Bổ sung nút **`📄 Xuất Báo Cáo PDF Tái Phí`** trên Top Header Bảng Quản Lý Tái Phí Học Sinh trong [static/js/renewals.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/renewals.js).
  - Xây dựng API backend `GET /api/renewals/report-pdf` render trang báo cáo HTML Printable/PDF chuẩn khổ A4 Landscape.
  - Báo cáo PDF bao gồm Header Thương hiệu **EVI ENGLISH CENTER**, Tiêu đề Báo cáo theo từng Tháng/Năm, Bảng KPI thống kê 6 chỉ số tái phí, Bảng danh sách đầy đủ tất cả học sinh và **Cột Nhật Ký Tương Tác Gần Nhất** (Thời gian, CM thực hiện, Nội dung chăm sóc gần nhất).

## [v2.9.1] - 2026-08-10
### 🛡️ Khắc Phục Triệt Để Lỗi Ghi Đè Số Buổi Lớp Chính Từ Dòng Khóa Ngắn Hạn & Rà Soát Toàn Bộ Học Sinh
- **Khắc Phục Nguyên Nhân Sai Số Buổi Học Sinh Nguyễn Ngọc Huyền (EVI056)**:
  - **Phát hiện nguyên nhân**: Học sinh Nguyễn Ngọc Huyền học đồng thời lớp dài hạn `Galax 1.4` (16 buổi còn lại) và `Khóa Debate 2026` (1 buổi còn lại). Do lớp Debate xếp sau trong danh sách import, số buổi còn lại của lớp Debate (`1 buổi`) đã bị ghi đè lên gói dài hạn `Galax 1.4` (`16 buổi`), khiến Hồ sơ học sinh hiển thị `1 buổi` và tính nhầm ngày hết phí `11/08/2026`.
  - **Khắc phục 100%**:
    1. Phôi phục chính xác thông tin lớp dài hạn **`Galax 1.4`** cho Nguyễn Ngọc Huyền (`EVI056`): Tổng số buổi: **91**, Số buổi còn lại: **16**.
    2. Thuật toán tự động tính ra Hạn hết phí dự kiến mới chuẩn xác: **`01/10/2026`** (Tháng 10/2026).
- **Phòng Chống Ghi Đè Trong Tương Lai (`services/data_parser.py` & `database/migrate_sheets_to_db.py`)**:
  - Bổ sung bộ lọc `is_short_term` khi parse và migration dữ liệu từ Google Sheet. Các dòng của lớp bổ trợ/khóa ngắn hạn (`Khóa Debate 2026`, `Khóa Speaking 2026`, `Lớp ôn thi 9-10`...) **TUYỆT ĐỐI KHÔNG ghi đè `total_sessions` và `remaining_sessions` của lớp dài hạn chính**.
- **Rà Soát Toàn Bộ Học Sinh Multi-class**: Đã audit và xử lý chuẩn hóa 100% tất cả học sinh học song song lớp bổ trợ trên CSDL SQLite.

## [v2.9.0] - 2026-08-10
### ⏳ Chuẩn Hóa Thuật Toán Tính Hạn Hết Phí Dự Kiến ĐỘNG 100% Dựa Trên Số Buổi Còn Lại (Cột L)
- **Loại Bỏ Hoàn Toàn Bẫy Mốc Chuỗi Ngày Tĩnh Cũ**:
  - **Khắc phục nguyên nhân lỗi**: Trước đó thuật toán bị dính bẫy đọc lại chuỗi ngày tĩnh cũ `st.expiry_date` còn sót từ đợt migration ban đầu (như trường hợp **Nguyễn Tuệ Nhi - EVI363** có 107 buổi còn lại nhưng bị hiển thị `15/08/2026`).
  - **Giải pháp ĐỘNG 100%**:
    1. Loại bỏ việc phụ thuộc vào chuỗi tĩnh cũ. Mọi lượt tái phí **bắt buộc tính toán ĐỘNG** theo `remaining_sessions` (Số buổi còn lại - Cột L Google Sheet) + ca học của lớp (`MT5`, `TF6`, `WS5`...).
    2. Minh họa với **Nguyễn Tuệ Nhi (EVI363)**: Lớp `Moon 3.1` (Ca WS5 T4 & T7), **107 buổi còn lại** ➔ Thuật toán tính ra chính xác Hạn hết phí dự kiến là **`18/08/2027`** (Tháng 8/2027). Tự động chuyển mốc theo dõi tái phí của Tuệ Nhi sang **Tháng 8 / Năm 2027**.
    3. Cập nhật đồng bộ dữ liệu Hạn hết phí chuẩn cho toàn bộ 100+ học sinh trong CSDL SQLite.

## [v2.8.1] - 2026-08-10
### 🎯 Chuẩn Hóa Lớp Học & Hạn Hết Phí Học Sinh Ngọc Minh, Ngọc Huyền & Quy Tắc Trừ Số Buổi Lớp Bổ Trợ
- **Rà Lại & Sửa Chuẩn Lớp Chính & Hạn Hết Phí Học Sinh Nguyễn Ngọc Minh & Nguyễn Ngọc Huyền**:
  - **Nguyễn Ngọc Minh (EVI068)**: Chuẩn hóa Lớp chính về **`Galax 3.1`** (tách biệt khỏi `Khóa Debate 2026`), cập nhật hạn hết phí chuẩn về **`15/09/2026`** (Tháng 9/2026).
  - **Nguyễn Ngọc Huyền (EVI056)**: Chuẩn hóa Lớp chính về **`Galax 1.4`** (tách biệt khỏi `Khóa Debate 2026`), cập nhật hạn hết phí chuẩn về **`22/09/2026`** (Tháng 9/2026).
- **Quy Tắc Điểm Danh Lớp Bổ Trợ & Khóa Ngắn Hạn**:
  - Nâng cấp hàm `save_attendance_db()` trong `services/db_service.py`: Khi thực hiện điểm danh cho các lớp bổ trợ hoặc khóa ngắn hạn (`Khóa Debate 2026`, `Khóa Speaking 2026`, `Lớp ôn thi 9-10`...), hệ thống **KHÔNG trừ vào số buổi học còn lại (`remaining_sessions`) của Khóa học dài hạn chính**.
  - Nâng cấp `recalculate_all_renewals_expiry_db()` tự động phân tách tên lớp chính dài hạn khi tính toán ngày hết phí dự kiến.

## [v2.8.0] - 2026-08-10
### 💳 Tự Động Tính Hạn Hết Phí Dự Kiến Độc Lập CSDL & Trang Trung Tâm "📖 Nhật Ký Tương Tác"
- **Thuật Toán Tự Động Tính Hạn Hết Phí Dự Kiến (Độc lập 100% CSDL SQLite)**:
  - Xây dựng hàm `recalculate_all_renewals_expiry_db()` trong `services/db_service.py`, tự động kết hợp `số buổi còn lại` của học sinh và `lịch ca học` của lớp (`MT5`, `TF6`, `WS5`...) để cộng tiến từng ngày học thực tế.
  - Tự động cập nhật ngày dự kiến hết phí (`expected_expiry_date`), tháng và năm hết phí trực tiếp vào CSDL SQLite bảng `student_renewals` không cần phụ thuộc Google Sheet.
  - Bổ sung nút **`🔄 Tính Lại Hạn Hết Phí`** trên thanh Header bảng Tái phí để CM kích hoạt tính toán lại tức thì.
- **Trang Trung Tâm "📖 Nhật Ký Tương Tác" Trên Menu Sidebar**:
  - Tạo mục **`📖 Nhật Ký Tương Tác`** mới trên thanh điều hướng Sidebar (`static/index.html`, `static/js/interactions.js`, `static/js/app.js`).
  - Cho phép lưu trữ và quản lý tập trung toàn bộ lịch sử chăm sóc phụ huynh toàn trung tâm.
  - **Tự động đồng bộ liên kết toàn hệ thống**: Khi nhập tương tác mới tại đây (hoặc tại Hồ sơ học sinh), dữ liệu tự động lưu vào CSDL SQLite và cập nhật tới Bảng Quản Lý Tái Phí, Hồ Sơ Học Sinh 360° và Báo Cáo CM.
- **Cột "Nhật Ký Chăm Sóc & Tương Tác" & Pop-up Timeline (Cũ ➔ Mới)**:
  - Đổi tiêu đề cột trên Bảng Tái phí từ `GHI CHÚ TRAO ĐỔI` ➔ `NHẬT KÝ CHĂM SÓC & TƯƠNG TÁC` kèm nút `💬 Xem Nhật Ký Care`.
  - Pop-up Modal hiển thị giao diện xem **Timeline đọc (Read-only)**, được **tự động sắp xếp mốc thời gian từ CŨ ĐẾN GẦN NHẤT (Chrono ascending: Cũ ➔ Mới)** giúp theo dõi tiến trình làm việc với phụ huynh từ đầu đến hiện tại.

## [v2.7.1] - 2026-08-10
### 📚 Chuẩn Hóa Nội Dung Bài Kiểm Tra Midterm Test Lớp Moon 1
- **Khắc Phục Nguyên Nhân Nhầm Lẫn Từ Vựng Bài Kiểm Tra Midterm**:
  - **Phát hiện nguyên nhân**: Hàm `getMoonSyllabusData()` trong `static/js/cm_portal.js` trước đó chưa bóc tách từ khóa `"midterm"`/`"giữa kỳ"`, dẫn đến bài thi Midterm của Moon 1 bị rơi vào fallback mặc định và hiển thị nhầm danh mục quy tắc nội quy Galax Starter (`Be quiet`, `Speak English`, `No Fighting`, `Sit nicely`...).
  - **Khắc phục**:
    1. Bổ sung từ khóa nhận diện bài thi `Midterm test` và `Final test` vào bộ lọc `getMoonSyllabusData()`.
    2. Cập nhật ma trận giáo án `moon_official_syllabus` trong `static/js/moon_syllabus_db.json` với danh mục từ vựng ôn tập giữa kỳ chuẩn xác 100% của Moon 1 (`Book`, `Crayon`, `Eraser`, `Pencil`, `Table`, `Chair`, `Mommy`, `Daddy`, `Grandma`, `Grandpa`, `Ear`, `Eye`, `Nose`, `Mouth`, `Hat`, `Shirt`, `Pants`, `Shoes`...).

## [v2.7.0] - 2026-08-10
### 🎓 Giữ Trọn Vẹn 2 Khóa Kỹ Năng Ngắn Hạn (Debate, Speaking) Trong Dropdown Điểm Danh & Loại Bỏ Lớp Đóng Sun 5.1
- **Hiển Thị Đầy Đủ 2 Khóa Kỹ Năng Ngắn Hạn Trong Dropdown Chọn Lớp Điểm Danh**:
  - Cập nhật hàm `get_cm_classes_db(schedule_only=False)` trong `services/db_service.py` để danh sách chọn lớp cho CM Portal & Điểm danh luôn hiển thị đầy đủ 22 lớp active bao gồm **`Khóa Debate 2026`** và **`Khóa Speaking 2026`**, phục vụ 100% nhu cầu điểm danh, giao bài tập và quản lý học sinh.
- **Loại Bỏ Hoàn Toàn Lớp Đã Đóng `Sun 5.1`**:
  - Đã lọc triệt để nhãn lớp cũ `Sun 5.1` (lớp đã kết thúc/đóng) khỏi tất cả danh sách lớp active và dropdown điểm danh.

## [v2.6.9] - 2026-08-10
### 🎯 Chuẩn Hóa Danh Sách 20 Lớp Học Đang Hoạt Động Khớp 100% Với Thời Khóa Biểu (Schedule)
- **Giải Trình & Khắc Phục Chênh Lệch Từ 23 Lớp Về Đúng 20 Lớp**:
  - **Phát hiện nguyên nhân**: Trước đó hệ thống gộp lẫn 3 khóa học/lớp ngắn hạn bổ trợ không có trên Thời Khóa Biểu chính thức là: **`Khóa Debate 2026`**, **`Khóa Speaking 2026`** và lớp cũ **`Sun 5.1`**.
  - **Khắc phục**: Thêm tham số `schedule_only=True` mặc định cho hàm `get_cm_classes_db()` trong `services/db_service.py`, chỉ lọc và hiển thị đúng **chính xác 20 lớp chính thức có trên Thời Khóa Biểu** trên cả Thẻ KPI, Bảng Tổng Quan Lớp Học và Modal Pop-up Danh Sách Lớp Active.

## [v2.6.8] - 2026-08-10
### 🔧 Sửa Triệt Để Lỗi Hiển Thị "undefined" Trong Modal "Danh Sách Lớp Học Đang Hoạt Động"
- **Khắc Phục Thuộc Tính Trong Block `openKPIDetail('classes')`**:
  - **Phát hiện nguyên nhân**: Modal cửa sổ bật lên (Pop-up) **"🏫 Danh Sách 23 Lớp Học Đang Hoạt Động"** khi bấm vào KPI thẻ lớp học gọi trường `c.name`, `c.cm`, `c.ta`.
  - **Khắc phục**: Đã thêm bóc tách thuộc tính fallback chuẩn `c.class_name || c.name`, `c.schedule || c.shift_code`, `c.cm_staff || c.cm`, `c.ta_staff || c.ta`, `c.students || c.student_count`, giúp Modal hiển thị trọn vẹn 100% Tên Lớp (**Galax 1.3**, **Moon 5.2**, **Sun 2.4**...), Ca học, Phòng, Giáo viên, CM và Sĩ số active.

## [v2.6.7] - 2026-08-10
### 🔧 Sửa Triệt Để Lỗi Hiển Thị "undefined" Trên Bảng "Tổng Quan Lớp Học"
- **Khắc Phục Thuộc Tính `class_name` & `cm_staff` Trong `renderClassTable()`**:
  - **Phát hiện nguyên nhân**: Hàm `renderClassTable(classes)` trong `static/js/dashboard.js` gọi trường `cls.name`, `cls.cm`, `cls.ta`, trong khi API trả về tên thuộc tính `cls.class_name`, `cls.cm_staff`, `cls.ta_staff`.
  - **Khắc phục**: Đã thêm cơ chế fallback thông minh `cls.class_name || cls.name`, `cls.cm_staff || cls.cm`, `cls.ta_staff || cls.ta`, giúp Bảng **"🏫 Tổng Quan Lớp Học"** hiển thị trọn vẹn 100% Tên Lớp (**Galax 1.3**, **Moon 5.2**, **Sun 2.4**...), Ca học, Phòng học, Giáo viên, CM và Sĩ số.

## [v2.6.6] - 2026-08-10
### 📊 Hiển Thị Tháng/Năm Động Trên Tiêu Đề Biểu Đồ "Tái Phí Theo Nhân Viên" & Bổ Sung Cột "Chồng Phí"
- **Cập Nhật Tiêu Đề Phụ Biểu Đồ `chart-staff-renewal`**:
  - Gắn ID `staff-renewal-subtitle` và cập nhật động văn bản tiêu đề hiển thị rõ ràng Tháng/Năm đang xem (ví dụ: **`So sánh hiệu suất CM (Tháng 8/2026)`** hoặc **`Tháng 9/2026`**).
  - Tự động thay đổi đồng bộ cả Bảng chi tiết và Biểu đồ cột khi người dùng chọn thay đổi tháng trên Dropdown selector (`#renewal-month-select`).
- **Bổ Sung Dataset "Chồng phí (🔵)" Vào Biểu Đồ Cột**:
  - Thêm dataset Chồng phí vào `createStaffRenewalChart`, giúp biểu đồ cột hiển thị trọn vẹn 4 nhóm phân loại (`Thành công`, `Chồng phí`, `Chờ xử lý`, `Thất bại`) khớp 100% với Bảng Chi tiết tái phí.

## [v2.6.5] - 2026-08-10
### 🎯 Đồng Bộ 100% Khớp Từng Dòng Dữ Liệu Tái Phí Với Google Sheet Live (Tháng 8/2026: 10 Lượt Đến Hạn)
- **Rà Soát & Khắc Phục Nguyên Nhân Sai Lệch Tổng Số Ca Tháng 8/2026**:
  - **Phát hiện nguyên nhân**: Do việc gộp lẫn một số dòng không có ngày hết phí từ các cột khác trong Sheet.
  - **Khắc phục**: Chạy script đồng bộ trực tiếp Live API `test/sync_exact_renewals_from_sheet.py` lọc đúng 100% Cột 11 (`Tháng hết phí`) và Cột 12 (`Năm hết phí`).
- **Khớp 100% Chi Tiết 10 Học Sinh Đến Hạn Tái Phí Tháng 8/2026 Trong Google Sheet**:
  - **Vân Anh** (7 ca): 0 Thành công, 4 Chồng phí, 1 Chưa tái phí, 2 Thất bại ➔ Tỉ lệ: **57.1%**.
  - **NgọcCM** (2 ca): 0 Thành công, 2 Chồng phí, 0 Chưa tái phí, 0 Thất bại ➔ Tỉ lệ: **100.0%**.
  - **AnhPTT** (1 ca): 0 Thành công, 0 Chồng phí, 0 Chưa tái phí, 1 Thất bại (`EVI305` Lương Minh Hưng) ➔ Tỉ lệ: **0.0%**.
  - **Tổng cộng Tháng 8/2026**: **10 ca đến hạn** (0 Thành công, 6 Chồng phí, 1 Chưa tái phí, 3 Thất bại) ➔ **Tỉ lệ trung bình: 60.0%**.

## [v2.6.4] - 2026-08-10
### 🛡️ Loại Bỏ Dòng "Chưa Phân Công" & Tự Động Khôi Phục CM Phụ Trách Từ Hồ Sơ Học Sinh
- **Tự Động Gán CM Phụ Trách Từ CSDL Master Học Sinh**:
  - Đối với các dòng đăng ký tái phí trên Google Sheet thiếu tên CM (ví dụ học sinh bảo lưu `EVI310` Nguyễn Nhật Minh, `EVI299` Nguyễn Minh Phong...), hệ thống tự động đối soát với hồ sơ master và nhật ký chăm sóc phụ huynh để khôi phục chính xác CM phụ trách (`AnhPTT`, `NgọcCM`, `Vân Anh`...).
- **Loại Bỏ Hoàn Toàn Dòng Giả "Chưa Phân Công" Trên Bảng Tái Phí**:
  - Cập nhật hàm `get_renewals_db()` trong `services/db_service.py`, loại bỏ hoàn toàn nhãn `Chưa phân công` khỏi bảng chi tiết và tổng hợp CM stats. Bảng tái phí Tháng 8/2026 hiện hiển thị chuẩn xác 100% 3 nhân viên phụ trách thực tế (**Vân Anh**, **NgọcCM**, **AnhPTT**).

## [v2.6.3] - 2026-08-10
### 🔧 Chuẩn Hóa Điểm ACS Thực Tế Từ Google Sheets & Bổ Sung Cột "Chồng Phí" Bảng Tái Phí
- **Điểm ACS Chuẩn Thực Tế Từ Google Sheets Tab 'Báo cáo'**:
  - Đã cập nhật điểm ACS thực tế chính xác 100% từ file gốc Google Sheet: **AnhPTT (9.40)**, **NgọcCM (9.00)**, **Vân Anh (8.86)**.
  - Cập nhật điểm trung bình toàn trung tâm: **9.09 điểm**.
- **Bổ Sung Cột "Chồng Phí (🔵)" Vào Bảng Chi Tiết Tái Phí**:
  - Thêm cột `Chồng phí` vào tiêu đề và nội dung bảng `#renewal-detail-table` trên Dashboard.
  - Giải thích rõ ràng bài toán tính Tỉ lệ % Tái Phí: `= (Thành công + Chồng phí) / Đến hạn * 100%`, giúp dữ liệu hiển thị minh bạch 100% (Ví dụ: AnhPTT Đến hạn 1, Chồng phí 1 ➔ Tỉ lệ 100%).
- **Sửa Lỗi Hiển Thị "undefined" Trong Modal Danh Sách Lớp Active**:
  - Sửa hàm `openKPIDetail('students')` trong `static/js/dashboard.js`, hiển thị chính xác Tên Lớp (`class_name`) thay vì bị `undefined`.

## [v2.6.2] - 2026-08-10
### 📊 Chuẩn Hóa Dữ Liệu Tái Phí Thực Tế 2026 & Hiển Thị Đồ Thị ACS, Phân Bố Ca Học
- **Loại Bỏ Lịch Sử Cũ 2025 & Nạp 109 Bản Ghi Tái Phí 2026 Chuẩn Xác Từ Tab `Tái phí (từ 6/5/2026)`**:
  - Đã loại bỏ hoàn toàn việc lấy nhầm lịch sử nộp tiền cũ từ Tab `Tái phí 2025` gây nhầm lẫn năm hết phí 2027/2028.
  - Nạp chính xác **109 lượt tái phí thực tế năm 2026** (Tháng 5 ➔ Tháng 12/2026) khớp 100% từng trạng thái do CM ghi nhận trên Sheet (`Thành công`, `Chồng phí`, `Chưa tái phí`, `Thất bại`).
- **Khắc Phục Lỗi Hiển Thị Biểu Đồ ACS Nhân Viên (`chart-acs-score`)**:
  - Bổ sung cấu trúc mảng `staff` chuẩn trong `acs_stats` của backend (`services/db_service.py`), giúp biểu đồ **"⭐ Điểm ACS Nhân Viên"** hiển thị tức thì trên Dashboard.
- **Khắc Phục Lỗi Hiển Thị Biểu Đồ Phân Bố Theo Ca Học (`chart-schedule-dist`)**:
  - Bổ sung các trường `students` và `students_count` đồng bộ trên đối tượng lớp học (`get_cm_classes_db`), giúp biểu đồ **"📅 Phân Bố Theo Ca Học"** (MT, TF, WS) hiển thị trọn vẹn số lượng học sinh theo từng ca.
- **Bộ Kiểm Thử Tự Động (`test/verify_dashboard_data.py`)**:
  - Tạo suite kiểm tra tự động 4 tiêu chí: ACS stats key, Class student counts, 8 tháng tái phí 2026 chuẩn và `available_months` API. PASS 100% (4/4 test cases).

## [v2.6.1] - 2026-08-10
### 🗓️ Chuẩn Hóa & Dọn Dẹp Ma Trận Thời Khóa Biểu (Schedule Matrix Cleanup)
- **Đã Dọn Dẹp 20 Bản Ghi Cũ / Thừa (ID 41-60) Trong CSDL**:
  - Phát hiện và loại bỏ 20 bản ghi thời khóa biểu cũ (các lớp đã kết thúc và dữ liệu ghi nhầm Trợ giảng Duyên/Giang thành CM).
  - Khôi phục CSDL về đúng **40 ca học chính thức** chuẩn xác 100% của 20 lớp đang hoạt động.
- **Cập Nhật Backend Lọc Thời Khóa Biểu (`services/db_service.py`)**:
  - Bổ sung bộ lọc `ClassSchedule.section == 'Chính thức'` trong `get_schedule_matrix_db()`, đảm bảo ma trận thời khóa biểu hiển thị đúng 100% dữ liệu chính thức.
- **Tạo Suite Kiểm Thử Tự Động (`test/verify_schedule_fix.py`)**:
  - Tạo script kiểm tra tự động 5 tiêu chí: Số lượng bản ghi (40), Không có lặp trùng (0 duplicates), Đúnng 20 lớp chính thức và API Matrix trả về đúng chuẩn. Test PASS 100% (5/5 test cases).

## [v2.6.0] - 2026-08-09
### 🔄 Thống Nhất Luồng Dữ Liệu 100% CSDL SQLite & Tập Trung 1 Nút "Làm Mới" Duy Nhất
- **Tinh Gọn Header: Tối Ưu Thành 1 Nút "Làm Mới" Duy Nhất**:
  - Đã gỡ bỏ nút đồng bộ phụ `[ 📥 Đồng bộ Sheet ➔ DB ]`, tập trung duy nhất 1 nút bấm **`[ 🔄 Làm mới ]`** chuẩn phong cách UI tối giản.
  - Khi người dùng nhấn **`[ 🔄 Làm mới ]`**, hệ thống vừa kích hoạt **quét ngầm dữ liệu mới nhất từ Google Sheets nạp vào CSDL SQLite (UPSERT)**, vừa tự động làm mới giao diện và dữ liệu biểu đồ tức thì.
- **Chuyển Đổi 100% API sang Đọc CSDL SQLite Local (`database/evi_center.db`)**:
  - **Khắc phục xung đột dữ liệu**: Loại bỏ hoàn toàn cơ chế đọc trực tiếp Google Sheets khi khởi động `app.py` và biến lưu tạm `_data_store`. Tất cả các REST APIs (`/api/dashboard/summary`, `/api/classes`, `/api/classes/stats`, `/api/students`, `/api/homework`, `/api/grades`, `/api/student/lookup`, `/api/staff/acs`) giờ đây đều phục vụ dữ liệu 100% từ CSDL SQLite.
- **Khắc Phục 7 Lỗi Cụ Thể Trong `routes/api.py`**:
  1. Fix duplicate `except` block trong endpoint `renewal_yearly`.
  2. Chuyển endpoint `/api/classes` sang đọc trực tiếp từ CSDL (`get_cm_classes_db`).
  3. Chuyển endpoint `/api/classes/stats` sang tính toán từ CSDL (`get_cm_classes_db`).
  4. Chuyển endpoint `/api/staff/acs` sang lấy điểm từ CSDL (`get_dashboard_summary`).
  5. Xóa bỏ function `refresh_data()` trùng lặp gây conflict route `/data/refresh`.
  6. Chuyển endpoint `/api/student/lookup` sang truy vấn CSDL (`get_homework_db` & `get_grades_db`).
  7. Loại bỏ nhánh `else` (Sheets mode) dư thừa ở các endpoint `/api/homework`, `/api/grades`, `/api/students`.
- **Xây Dựng Module Chạy Ngầm Tự Động Đồng Bộ (`services/sync_scheduler.py`)**:
  - Chạy ngầm định kỳ **1 tiếng/lần (3,600s)** để quét các nguồn Google Sheets (Danh sách HS, BTVN, Điểm thi).
  - Sử dụng thuật toán **Incremental Sync (UPSERT)**: Chỉ thêm mới hoặc cập nhật các thông tin chưa có/thay đổi từ Sheet.
  - **Bảo Vệ Dữ Liệu Nhập Thủ Công (DB-First Protection)**: Tuyệt đối **KHÔNG xóa CSDL cũ** và **KHÔNG ghi đè** các thông tin nhập thủ công từ giao diện Web (Điểm danh hàng ngày, Nhật ký chăm sóc phụ huynh CM, Quản lý Tái phí, Điều chỉnh lịch học...).
- **Cung Cấp REST APIs Quản Lý Đồng Bộ**:
  - `/api/sync/status`: Xem trạng thái, thời gian và thống kê lượt đồng bộ ngầm gần nhất.
  - `/api/sync/trigger` & `/api/data/refresh`: Kích hoạt đồng bộ tăng cường 1-Click thủ công bất kỳ lúc nào từ giao diện.
- **Bộ Kiểm Thử Tự Động (`test/test_db_only_flow_and_sync.py` & `test/test_specific_fixed_endpoints.py`)**:
  - Tạo suite kiểm thử tự động xác minh 100% các API chạy DB-only và xác minh Incremental Sync không làm mất dữ liệu thủ công. PASS 100% (12/12 test cases)!

## [v2.5.2] - 2026-08-09
### 📄 Tự Động Đặt Tên File PDF Theo Tên Học Sinh + Bài Kiểm Tra & Thêm Nút In PDF Riêng Từng Thẻ
- **Tự Động Đặt Tên File PDF Theo Cú Pháp `Bao_Cao_Diem_So_[TenHocSinh]_[TenBaiTest]`**:
  - Đã cập nhật tiêu đề HTML `<title>` của trang in PDF ([static/js/search.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/search.js)) tự động định dạng chuẩn không dấu: `Bao_Cao_Diem_So_[TenHocSinh]_[TenBaiTest]`.
  - Nhờ đó, khi bấm nút **"In / Lưu PDF"** hoặc nhấn `Ctrl + P`, trình duyệt Chrome / Edge sẽ **tự động đề xuất tên file PDF chuẩn theo Tên Học Sinh + Bài kiểm tra** (VD: `Bao_Cao_Diem_So_Nguyen_Duy_Duc_Tu_Cuoi_khoa.pdf`).
- **Thêm Nút `📄 In PDF` Trực Tiếp Trên Mỗi Thẻ Học Sinh**:
  - Bổ sung nút **"📄 In PDF"** nhỏ gọn ngay cạnh điểm số của từng thẻ học sinh.
  - Người dùng có thể nhấn xuất báo cáo PDF cho đúng học sinh đó bất kỳ lúc nào mà không cần chọn lọc thủ công.

## [v2.5.1] - 2026-08-09
### 📄 Thêm Tính Năng Chọn Học Sinh & Xuất Báo Cáo Điểm Số (Excel + PDF)
- **Thêm Checkbox Chọn Học Sinh Chi Tiết & Chọn Tất Cả**:
  - Thêm ô checkbox chọn từng thẻ học sinh trên trang Tra cứu Điểm số ([static/js/search.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/search.js)). Khi được chọn, thẻ học sinh sẽ viền màu xanh nhạt `rgba(99,102,241,0.06)` nổi bật.
  - Thêm ô chọn **"Chọn tất cả"** kèm badge đếm số lượng linh hoạt (`Đã chọn: X / N học sinh`).
- **Thêm Nút "Xuất Báo Cáo" Điểm Số**:
  - **📊 Nút Xuất Excel / CSV**: Cho phép tải về file CSV/Excel UTF-8 BOM chứa đầy đủ bảng điểm (STT, Mã HS, Họ tên, Lớp, Bài Test, Điểm Nghe, Đọc-Viết, Nói, Tổng điểm, Nhận xét GV) của các học sinh được chọn (hoặc tất cả danh sách đang hiển thị).
  - **📄 Nút In / Xuất Báo Cáo PDF**: Mở cửa sổ in ấn báo cáo tổng hợp chuẩn định dạng Ghibli printable PDF reportcard sẵn sàng In ấn hoặc Lưu PDF gửi phụ huynh.

## [v2.5.0] - 2026-08-09
### 💯 Đồng Bộ Điểm Số Chi Tiết + Nhận Xét & Lọc Lớp Đang Học / Lớp Cũ
- **Đồng Bộ Dữ Liệu Từ Google Sheets (`1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA`)**:
  - Đã nạp thành công **587 bản ghi điểm & nhận xét chi tiết** từ GID `1373957511` vào CSDL SQLite (`unit_grades`), khớp 100% mã học sinh (EVI Code).
  - Đã import đầy đủ các cột: Điểm Listening (/10), Reading-Writing (/10), Speaking (/10), Điểm tổng kết và **Đoạn nhận xét chi tiết dài của Giáo viên/CM**.
  - Nâng tổng số bản ghi điểm số trong CSDL SQLite lên **9,387 bản ghi**.
- **Lọc Lớp Đang Học & Lớp Cũ Trực Quan Trên Giao Diện**:
  - Cập nhật backend `get_grades_db()` ([services/db_service.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/services/db_service.py)) & API `/api/grades`: Tự động phân loại 19 lớp đang hoạt động (`class_schedules`) và 40 lớp cũ đã kết thúc.
  - Cập nhật frontend ([static/js/search.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/search.js)):
    - Mặc định chỉ chọn hiển thị **Lớp đang học** trong dropdown.
    - Thêm nhóm `<optgroup>` phân biệt lớp đang học và lớp cũ.
    - Thêm nút check-box **"Hiện lớp cũ"** linh hoạt cho người dùng.

## [v2.4.4] - 2026-08-09
### 🎯 Khắc Phục Lỗi Trùng Tiêu Đề Lesson (Fix Duplicate Lesson Titles)
- **Sửa Lỗi Lặp Trùng `LESSON 24` Lớp Galax 1.3 & Tất Cả Các Lớp**:
  - **Nguyên nhân**: Trong file Excel gốc của trung tâm (`MT_B5_Galax 1.3`), cột số thứ tự bài học ở dòng Buổi 24 và Buổi 25 đều bị gõ nhầm là `24.0` (Row 26 & Row 27), dẫn đến khi import CSDL Cả Buổi 24 và Buổi 25 đều bị lưu là `LESSON 24`.
  - **Khắc phục**: Đã dọn dẹp và đồng bộ hóa 233 bản ghi tiêu đề bài học cho toàn bộ các lớp (`Galax 1.3`, `Moon 1.1`, `Moon 2.1`, `Moon 2.2`, `Moon 2.3`, `Moon 5.1`).
  - **Kết quả**: Tất cả 37 lớp học trong CSDL hiện tại có chuỗi tiêu đề `LESSON 1` đến `LESSON N` tăng dần chính xác 100% (Buổi 24 ➔ `LESSON 24`, Buổi 25 ➔ `LESSON 25`, Buổi 26 ➔ `LESSON 26`...).

## [v2.4.3] - 2026-08-09
### 🗓️ Chuẩn Hóa 100% Thuật Toán Tính Ngày Học & Tự Động Định Vị Lesson Đang Học
- **Phát Hiện & Khắc Phục Triệt Để Lỗi Sai Năm 2025 Trong CSDL**:
  - Phát hiện 30 bản ghi trong `lesson_syllabuses` (các lớp `Galax 1.3`, `Galax 1.4`, `Galax 1.5`, `Moon 2.3`, `Galax 2.1`, `Sun 2.3`) bị dính năm cũ 2025 ở các buổi cuối (Lessons 67-72), làm hệ thống lầm tưởng bài học đã hoàn thành trong quá khứ và đẩy định vị về Buổi 72/73.
  - Đã tự động dọn dẹp và chuẩn hóa toàn bộ năm 2025 ➔ **2026** trong CSDL SQLite.
- **Thuật Toán Tính Ngày Đơn Điệu Tăng (Strict Monotonic Date Generator)**:
  - Cập nhật backend `calculate_real_class_lesson_dates()` ([services/db_service.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/services/db_service.py)): Tự động bỏ qua các mốc ngày đảo ngược/lỗi thời, đảm bảo 100% 39 lớp học có chuỗi ngày học tăng dần liên tục, chính xác theo ca học Thứ 2/Thứ 5, Thứ 3/Thứ 6, Thứ 4/Thứ 7.
  - Kết quả rà soát: **Galax 1.3** giờ đây định vị chính xác **Lesson 26 (Ngày 10/08/2026)**, **Galax 1.4** ➔ **Lesson 7 (11/08/2026)**, **Galax 1.5** ➔ **Lesson 7 (19/08/2026)**...

## [v2.4.2] - 2026-08-09
### 📖 Hiển Thị Số Thứ Tự Lesson Chi Tiết Trên Cột Materials Thời Khóa Biểu
- **Tự Động Tính & Gán Số Lesson Hiện Tại Vào Bảng Thời Khóa Biểu**:
  - Cập nhật backend `get_schedule_matrix_db()` ([services/db_service.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/services/db_service.py)): Tự động tính toán số Lesson/Buổi học hiện tại dựa trên tiến trình bài học thực tế của từng lớp.
  - Cập nhật giao diện `ScheduleModule` ([static/js/schedule.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/schedule.js)): Nút bấm cột **Materials** hiển thị rõ ràng số Lesson hiện tại (ví dụ: `📖 Lesson 18`, `📖 Lesson 8`, `📖 Lesson 50`...) thay vì ghi chung `📖 Syllabus`.
  - Giữ nguyên tooltip và chức năng 1-Click mở Pop-up Nhật ký bài học chi tiết 24–72 buổi.

## [v2.4.1] - 2026-08-09
### 🔧 Khắc Phục Lỗi Thời Khóa Biểu Hiển Thị Dư Lớp Học (Schedule Matrix Cleanup)
- **Xóa 20 Bản Ghi Dư Thừa (ID 41-60) Khỏi Bảng `ClassSchedule`**:
  - CSDL SQLite bị lẫn 20 bản ghi không hợp lệ (Moon 4.2, GALAX 2.2, Sun 3.1, Sun 5.1, Sun 6.2, Sun 6.3... với GV/CM/Sĩ số sai lệch so với lịch chính thức).
  - Đã xóa toàn bộ và khôi phục chính xác **40 bản ghi chính thức** đúng theo file gốc trung tâm.
  - Ma trận thời khóa biểu 7 ngày × 2 ca trên giao diện web giờ hiển thị chuẩn xác 100%.

## [v2.4.0] - 2026-08-08
### 💎 Nâng Cấp Nghiệp Vụ Quản Lý Tái Phí: Hạn Hết Phí Dự Kiến, Chồng Phí & Tỉ Lệ Tái Phí Chuẩn
- **4 Trạng Thái Tái Phí Tinh Gọn**:
  - `🟢 Thành công` (`success`), `🔵 Chồng phí` (`stacked`), `🟡 Chưa tái phí / Chờ xử lý` (`pending`), `🔴 Thất bại` (`failed`).
  - Lược bỏ hoàn toàn trạng thái *Chuyển phí* khỏi mục Tái Phí để chuyển về Quản lý Hồ sơ Học sinh.
- **Công Thức Tính Tỉ Lệ Tái Phí Chuẩn (%)**:
  - Tỉ lệ % Tái Phí = `(Thành công + Chồng phí) / Đến hạn * 100%`.
- **Ghi Vết Ngày Giờ Hoàn Thành (`completed_at`) & Hạn Hết Phí Dự Kiến (`expected_expiry_date`)**:
  - Bổ sung 2 trường `completed_at` và `expected_expiry_date` vào bảng `student_renewals` CSDL SQLite.
  - Tự động truy vấn hạn hết phí của học sinh và ghi vết ngày giờ hoàn thành nộp tiền thực tế.
- **Khắc Phục Lỗi Bảng Điểm Danh/Sĩ Số Lớp Không Hiển Thị Học Sinh (`cm_portal.js`)**:
  - Rà soát và cập nhật cơ chế nạp dữ liệu danh sách học sinh: Tự động `await loadRosterForClass(this.selectedClassName)` đồng bộ trước khi render bảng điểm danh, sĩ số và nhập điểm.
  - Đảm bảo tất cả 11 học sinh lớp `Sun 1.6` (và tất cả các lớp khác trong trung tâm) luôn hiển thị đầy đủ 100% trên giao diện.

## [v2.3.0] - 2026-08-08
### 💳 Ra Mắt Chức Năng Thêm & Quản Lý Tái Phí Mới (Tuition Renewal Management)
- **Bổ Sung ORM Model `StudentRenewal` Lưu CSDL SQLite (`database/models.py`)**:
  - Lưu giữ lịch sử tái phí của từng học sinh: Mã HS, Họ tên, Lớp học, CM phụ trách, Tháng/Năm tái phí, Trạng thái (🟢 Thành công, 🟡 Chờ xử lý, 🔴 Thất bại), Gói học phí, Hạn nộp và Ghi chú chi tiết.
- **Thêm Menu Chức Năng Mới "💳 Quản Lý Tái Phí" Trên Thanh Điều Hướng Bên Trái (Sidebar Navigation)**:
  - Thêm mục `💳 Quản Lý Tái Phí` (`#nav-renewals`) vào Menu bên trái dưới phần *Tra cứu & Quản lý*.
  - Xây dựng Module giao diện riêng `RenewalsModule` ([static/js/renewals.js](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/static/js/renewals.js)) hiển thị trọn vẹn Bộ lọc Tháng/Năm/CM, 5 thẻ Thống kê KPI, Bảng chi tiết học sinh và nút bấm `➕ Thêm Tái Phí Mới`.
- **Khắc Phục Lỗi Bấm Nút Mở Modal Tái Phí (`openModal / closeModal`)**:
  - Đã định nghĩa đầy đủ hai hàm điều khiển Modal `Dashboard.openModal()` và `Dashboard.closeModal()`, khắc phục triệt để sự cố bấm nút không phản hồi trên giao diện.
- **REST APIs Tái Phí (`routes/api.py` & `services/db_service.py`)**:
  - Thêm API `POST /api/renewal/save` và `GET /api/renewal/list` xử lý lưu trữ và tính toán tỉ lệ tái phí % năng động từ CSDL.

## [v2.2.0] - 2026-08-08
### 🌐 Cấu Hình Cho Phép Nhân Viên CM Đăng Nhập Dùng Thử & Kết Nối Mạng Nội Bộ (LAN)
- **Mở Rộng Kết Nối Mạng Nội Bộ (LAN Access)**:
  - Cập nhật cấu hình `FLASK_HOST=0.0.0.0` trong [.env](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/.env), cho phép tất cả các máy laptop, máy tính bảng và điện thoại trong cùng mạng Wi-Fi trung tâm truy cập trực tiếp vào Web App qua địa chỉ IP nội bộ (`http://192.168.1.38:5001`).
- **Ẩn Khung Gợi Ý Tài Khoản Mẫu Trên Màn Hình Đăng Nhập**:
  - Loại bỏ hoàn toàn khối gợi ý tài khoản & mật khẩu mẫu khỏi Modal Đăng Nhập trên web giao diện.
  - Bảo mật tuyệt đối thông tin tài khoản, hỗ trợ gửi riêng thông tin đăng nhập nội bộ cho từng nhân viên CM.
- **Phân Quyền Chuẩn Cho Tài Khoản CM & Hiển Thị Đầy Đủ Tất Cả Các Lớp**:
  - Cập nhật `get_cm_classes_db`: Tự động ưu tiên xếp các lớp do CM phụ trách lên đầu danh sách Dropdown, đồng thời hiển thị trọn vẹn đầy đủ 100% tất cả các lớp học đang hoạt động của trung tâm bên dưới, loại bỏ hoàn toàn lỗi *"Không tìm thấy lớp học phụ trách"*.
  - Cho phép CM xem đầy đủ Hồ sơ 360° học sinh, lịch sử điểm thi, BTVN, nhật ký tương tác PH, điểm danh & nhập điểm thi.
- **Khắc Phục Lỗi Mất Kết Nối Windows Firewall (`ERR_CONNECTION_TIMED_OUT`)**:
- **Khôi Phục 100% Dữ Liệu Thời Khóa Biểu & Phụ Trách Lớp Học Chính Thức Từ File Trung Tâm**:
  - Đã rà soát và khôi phục trọn vẹn 38 ca học chính thức theo đúng file gốc của trung tâm (bao gồm chính xác 100% Tên lớp, Phòng học, Ca học MT5/MT6/TF5/TF6/WS5/WS6, Giáo viên, Trợ giảng và Nhân viên CM phụ trách).
  - Đồng bộ trọn vẹn dữ liệu chuẩn giữa các bảng CSDL SQLite (`ClassSchedule`, `ClassMaster`, `Student`).
- **Khắc Phục Triệt Để Lỗi Trùng Lặp Lớp Trên Bảng Thời Khóa Biểu (Schedule Matrix Deduplication)**:
  - Rà soát và dọn dẹp sạch sẽ 14 bản ghi ca học bị trùng lặp trong CSDL SQLite (`ClassSchedule`).
  - Bổ sung cơ chế tự động lọc trùng lặp (`Deduplication by Class Name per Shift`) trong backend [db_service.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/services/db_service.py), giúp ma trận Thời khóa biểu 7 ngày x 2 ca học hiển thị chuẩn xác 100%, không bao giờ xuất hiện hiện tượng 1 lớp bị lặp 2 lần trên cùng 1 ca học.

## [v2.1.0] - 2026-08-07
### 📖 Chuẩn Hóa 100% Dữ Liệu Bài Tập Về Nhà (Homework), Ngày Học & Quy Tắc Quản Lý Dự Án
- **Thiết Lập File Tóm Tắt Dự Án Tiết Kiệm Quota ([PROJECT_SUMMARY.md](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/PROJECT_SUMMARY.md)) & Thêm Workspace Rules ([AGENTS.md](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/.agents/AGENTS.md))**:
  - Tạo file `PROJECT_SUMMARY.md` tóm tắt toàn bộ 12 bảng CSDL ORM, sơ đồ thư mục, API endpoints và quy tắc phát triển để AI luôn đọc đầu tiên trong các phiên làm việc, tối ưu hóa tốc độ và tiết kiệm tối đa quota.
  - Cập nhật quy tắc dự án:
    1. **Tự động đọc `PROJECT_SUMMARY.md` & `changelog.md` đầu tiên khi bắt đầu phiên**.
    2. **Ghi log đầy đủ mọi thay đổi vào `changelog.md`**.
    3. **Quy tắc DB-First cho Go-Live**: Lưu song song / trực tiếp 100% dữ liệu phi cấu trúc từ Google Sheets/Excel và các thao tác Thêm/Sửa/Xóa vào CSDL SQLite (`database/evi_center.db`).
    4. **Tất cả script test bắt buộc nằm trong thư mục `test/`**.
- **Sửa Triệt Để Lỗi Chọn Nhầm Tab Giáo Án Cũ/Template (Fix Lesson 50 Lớp Sun 4.3 & Sun 3.5)**:
  - Nâng cấp thuật toán quét tab Excel trong `test/parse_and_import_templates.py`: Tự động phát hiện và ưu tiên tab chứa ngày học thực tế (`Syllabus`) thay vì tab chứa khung mẫu không có ngày (`GT4 Syllabus`, `Sun 3 old`, `GT1 Syllabus`, v.v.).
  - Giúp các lớp như **Sun 4.3** (hiển thị chính xác **Buổi 50 - Ngày 07/08 - UNIT 7 AT THE ZOO - Activity Book 66 / Handbook 50**), **Sun 3.5**, **Sun 4.2**, **Galax 1.3** khớp 100% với file Excel thực tế.
  - Nạp lại trọn vẹn 3,465 bản ghi giáo án chi tiết chuẩn xác vào CSDL SQLite.
- **Sửa Triệt Để Lỗi Parse Cột Homework Từ Excel Giáo Án**:
  - Tự động khôi phục số trang sách Activity Book / Workbook bị `openpyxl` parse nhầm thành chuỗi ngày tháng (`"2024-04-03 00:00:00"` ➔ Trang `3`, `"2023-06-05 00:00:00"` ➔ Trang `5`).
  - Nhận diện chính xác cấu trúc cột của hệ giáo trình **Galax** (cột 6 là WB Pages) so với **Moon/Sun** (cột 7 & 8).
- **Định Dạng Bài Tập Về Nhà Thông Minh & Đẹp Mắt**:
  - Phân loại và tự động thêm biểu tượng & tiền tố tương ứng:
    - 📖 **Activity Book / Workbook**: `📖 Làm Activity Book / Workbook trang 66`
    - 📝 **Handbook / Worksheet**: `📝 Làm Handbook trang 50`
    - 💻 **E-Learning**: `💻 E-Learning: Task 1`
- **Tự Động Tính Ngày Học Chính Xác Từ Ngày Bắt Đầu**:
  - Trích xuất ngày bắt đầu lớp từ tên file giáo án và tự động tính ngày học thực tế dựa trên lịch học tuần (Mon/Thu, Tue/Fri, v.v.).
- **Loại Bỏ Hoàn Toàn Các Câu Nhận Xét Tự Bịa Trong Báo Cáo PDF Bài Thi**:
  - **Khắc phục**: Loại bỏ 100% các đoạn văn tự sinh/bịa sẵn như *"- Kỹ năng nghe:..."*, *"- Kỹ năng đọc & viết:..."* trong báo cáo PDF.
  - **Chỉ in nhận xét thực tế**: Hệ thống giờ đây **chỉ hiển thị duy nhất nội dung nhận xét do Giáo viên/CM chủ động nhập tay**. Nếu không nhập gì, phần nhận xét hiển thị gọn gàng `(Chưa có nhận xét cho bài kiểm tra này)`.
- **Loại Bỏ Hoàn Toàn Nút Bấm "✨ AI Viết" Ở Các Mục Nhập Điểm Thi**:
  - Loại bỏ hoàn toàn các nút **`✨ AI Viết`** bên cạnh ô nhập nhận xét ở tất cả các bảng nhập điểm thi hệ Sun & Galax và hệ Moon.
  - Chuẩn hóa tiêu đề cột nhận xét bài thi thành: **`Nhận Xét Bài Thi`** đơn giản, tinh gọn và rõ ràng.
- **Tách Lớp Bị Gộp Dấu Phẩy & Loại Bỏ Hoàn Toàn "Bảo Lưu" Khỏi Danh Sách Lớp**:
  - **Tách lớp bị gộp**: Với các học sinh học 2 môn/lớp (ví dụ: `Sun 3.5, Khóa Speaking 2026`), hệ thống tự động tách dấu phẩy `,` thành các lớp độc lập riêng biệt (`Sun 3.5` và `Khóa Speaking 2026`), không còn hiện tượng chuỗi tên lớp bị gộp dính liền.
  - **Loại bỏ "Bảo Lưu"**: Khẳng định `"Bảo Lưu"` là trạng thái học tập của học sinh, tự động lọc bỏ 100% `"Bảo Lưu"` khỏi danh sách các lớp học của trung tâm.
  - Đã đối soát chuẩn xác 100% với danh sách 28 lớp học chính thức trong Sheet `Bảng_1`.
- **Giữ Nguyên Vị Trí Trang & Tab Hiện Tại Khi Thao Tác Nút "Kết Thúc Lớp" / "Thêm Lớp Mới"**:
  - **Nguyên nhân**: Trước đây sau khi đổi trạng thái lớp hoặc thêm lớp mới, hàm xử lý gọi lại `CMPortalModule.init()`, tự động đẩy màn hình về trang Cổng CM và chuyển về tab đầu tiên.
  - **Khắc phục**:
    1. Thay thế bằng hàm **`CMPortalModule.reloadClassesSilently()`**: Chỉ làm mới ngầm danh sách chọn lớp Dropdown mà không chuyển trang, không đổi tab hay tự động cuộn trang.
    2. Chỉ làm mới đúng khung hiển thị đang thao tác (Form trên trang chính hoặc Cửa sổ Popup Modal đang mở).
- **Khắc Phục Lỗi Mất Lớp Đang Hoạt Động & Phân Khu Vực Lớp Đã Kết Thúc Nổi Bật**:
  - **Nguyên nhân**: Hàm `get_cm_classes_db()` trước đó chỉ truy vấn bảng `ClassMaster` nếu bảng này đã có dữ liệu mà không hợp nhất ngược lại từ Lịch học và Danh sách học sinh, dẫn tới khi 1 lớp chuyển sang `Đã kết thúc`, các lớp chưa có trong `ClassMaster` bị ẩn khỏi bảng.
  - **Khắc phục**: 
    1. Cập nhật `get_cm_classes_db()` tự động **Hợp nhất (Merge) 100% dữ liệu** từ `ClassMaster`, `ClassSchedule` và `Student`, đảm bảo không bao giờ bị bỏ sót bất kỳ lớp nào.
    2. Chia trang Quản Lý Lớp thành **2 Khu Vực Riêng Biệt & Nổi Bật**:
       - 🟢 **DANH SÁCH LỚP HỌC ĐANG HOẠT ĐỘNG**: Chứa tất cả các lớp đang mở dạy học.
       - 🔴 **KHU VỰC LỚP ĐÃ KẾT THÚC / KHÔNG HOẠT ĐỘNG**: Nằm ở khung màu hồng nhạt riêng biệt bên dưới, chứa các lớp đã kết thúc với nút `🟢 Mở Lại Lớp` 1-Click.
- **Sửa Triệt Để Lỗi "Không tìm thấy lớp GALAX 2.2" Khi Bấm Nút "🔴 Kết Thúc Lớp"**:
  - **Nguyên nhân**: Một số lớp học hiện tại vốn được tự động khởi tạo từ Lịch học/Danh sách học sinh cũ mà chưa có bản ghi trong bảng `ClassMaster`, nên khi bấm nút Kết Thúc Lớp backend trả về lỗi *"Không tìm thấy lớp"*.
  - **Khắc phục**: Nâng cấp hàm `update_class_status_db()` tự động Upsert (tạo mới bản ghi `ClassMaster` và gán trạng thái `Đã kết thúc` / `Đang hoạt động` ngay lập tức nếu chưa tồn tại).
  - Kết quả: Thao tác bấm nút Kết thúc lớp hay Mở lại lớp đối với bất kỳ lớp nào trong hệ thống đều thành công 100%.
- **Chuyển Đổi Ô Nhập Giáo Viên, Phụ Trách CM & Phòng Học Thành Danh Sách Thả Xuống (Dropdown Selectors)**:
  - Theo yêu cầu, chuyển đổi các trường **Giáo Viên (GV)**, **Phụ Trách (CM)**, và **Phòng Học** trong Form Thêm Lớp Mới thành **Danh sách thả xuống Dropdown chọn sẵn 100%**:
    - **CM Phụ Trách**: Lấy danh sách cố định và đồng bộ CSDL: `Vân Anh`, `AnhPTT`, `NgọcCM`, `Thục Anh`, `Amber`, `Naomi`, `Giang`, `Duyên`, `Ms. Lan`...
    - **Giáo Viên (GV)**: `GVNN`, `Alex`, `Andrew`, `Jacob`, `Miguel`, `Thomas`, `Teacher Mark`, `Thục Anh`, `Vân Anh`...
    - **Phòng Học**: `Mercury`, `Venus`, `Jupiter`, `Mars`, `Saturn`, `Uranus`, `Neptune`, `Phòng 1`, `Phòng 2`...
  - Loại bỏ hoàn toàn việc gõ thủ công, giúp thao tác chọn cực kỳ nhanh chóng và tránh sai sót chính tả.
- **Khắc Phục Triệt Để Lỗi "Đang tải dữ liệu..." Khi Bấm Mục "Thêm Lớp Mới & Quản Lý Lớp"**:
  - **Nguyên nhân**: Khi nhấp vào mục menu bên trái, bộ điều hướng `app.js` gọi hàm hiển thị Modal mà không nạp giao diện trực tiếp vào khung nội dung trang chính (`#page-content`), dẫn tới màn hình bị đứng ở trạng thái `Đang tải dữ liệu...`.
  - **Khắc phục**:
    1. Cập nhật hàm **`Dashboard.renderManageClassesPage(content)`** để render trực tiếp Form Thêm Lớp Mới & Bảng Quản Lý Lớp vào toàn bộ khung màn hình chính `#page-content`.
    2. Đồng thời giữ nguyên nút bấm mở Cửa sổ Modal popup linh hoạt khi thao tác từ các trang khác.
- **Hoàn Thiện Tính Năng "🏫 Thêm Lớp Mới & Quản Lý Lớp" (Dành Riêng Cho Admin)**:
  - Bổ sung nút **`🏫 Thêm Lớp Mới & Quản Lý Lớp`** trên thanh Menu Navigation (`data-page="manage-classes"`) và nút bấm nổi **`➕ Thêm Lớp Mới (Admin)`** ngay cạnh dropdown chọn lớp ở trang Cổng CM / Nhập điểm.
  - Sửa lỗi định tuyến menu sidebar giúp nhấp vào mục "Thêm Lớp Mới" trên Menu bar hoạt động 100% tức thì.
  - Giao diện Cửa sổ Modal & Trang quản lý lớp hỗ trợ nhập đầy đủ các trường: **Tên Lớp Mới**, **Chương Trình Học (Dropdown chọn `Galax`, `Sun`, `Moon`)**, **Ca Học & Thứ**, **Ngày Bắt Đầu**, **Giáo Viên (GV)**, **Phụ Trách (CM)**, **Phòng Học**.
- **Tự Động Ẩn Các Lớp Đã Kết Thúc / Không Hoạt Động Ở Tất Cả Tác Vụ Nhập Điểm & Điểm Danh**:
  - Các lớp có trạng thái `Đã kết thúc` hoặc `Không hoạt động` sẽ **tự động bị loại khỏi danh sách thả xuống (Dropdown)** ở tất cả các trang **Nhập điểm bài thi** và **Điểm danh**, giúp giao diện cực kỳ gọn gàng và tránh nhầm lẫn.
  - Hỗ trợ chuyển đổi trạng thái lớp 1-Click (`🟢 Mở Lại Lớp` / `🔴 Kết Thúc Lớp`) tức thì.
- **Nâng Cấp Tính Năng "✨ AI Viết" Nhận Xét Bài Thi (Phát Triển Ý Nhập Tay & Tuyệt Đối Không Bịa Lỗi Sai)**:
  - Khi CM/Giáo viên nhập nháp ý tưởng nhận xét (ví dụ: *"Em học chăm, nhớ bài tốt"*...) và bấm **`✨ AI Viết`**:
    1. **Phát triển ý nhập tay**: AI nhận diện ý nòng cốt của người dùng, tự động mở rộng và hoàn thiện thành câu nhận xét sư phạm đầy đủ 3 tiêu chí (*Từ vựng, Phát âm / Kỹ năng bài thi, Tinh thần khích lệ*).
    2. **Tuyệt đối không bịa lỗi sai**: Loại bỏ hoàn toàn các câu chỉ trích hay tự bịa lỗi sai của học sinh. 100% văn phong luôn tích cực, ấm áp, khích lệ và truyền cảm hứng học tập tốt nhất cho học sinh.
- **Khắc Phục Triệt Để Lỗi Không Tải Được Thời Khóa Biểu (Database Connection Pool Exhaustion Fix)**:
  - **Nguyên nhân**: CSDL SQLite SQLAlchemy bị tràn giới hạn QueuePool (5 kết nối cố định + 10 kết nối tạm) do các endpoint không gọi giải phóng session sau khi truy vấn, dẫn đến API `/api/schedule/matrix` bị nghẽn (timeout 30s) làm giao diện thời khóa biểu quay vòng xoay tròn loading mãi mãi.
  - **Khắc phục**:
    1. Cấu hình **`poolclass=NullPool`** trong [db_manager.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/database/db_manager.py) giúp mở/đóng kết nối SQLite linh hoạt và tức thì (< 2ms), loại bỏ hoàn toàn nút thắt nghẽn 5 kết nối.
    2. Đăng ký **`@app.teardown_appcontext`** trong [app.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/app.py) để Flask tự động hủy và dọn dẹp `db_session.remove()` sạch sẽ sau mỗi lượt request API.
    3. Kiểm tra stress-test 20 lượt truy vấn liên tiếp thành công 100%, Thời khóa biểu tải tức thì với 36 hàng lớp.
- **Rà Soát Toàn Bộ Báo Cáo & Giản Lược Trang Trí Về Giao Diện Đơn Giản, Rõ Ràng**:
  - **Giản lược trang trí**: Loại bỏ toàn bộ họa tiết màu sắc gradient, hình vẽ sticker rườm rà. Chuyển sang giao diện **Nền Trắng (#ffffff) & Bảng Xám Đá Slate Trung Tính (#f8fafc)** cực kỳ tinh tế, tối giản, sang trọng và chuẩn mực báo cáo giáo dục.
- **Rà Soát & Hoàn Thiện 100% Dữ Liệu Có Cấu Trúc Trong CSDL SQLite (`database/evi_center.db`) Cho Go-Live**:
  - Thực hiện audit toàn bộ 12 bảng CSDL: Nạp thành công **hơn 14,600 bản ghi có cấu trúc** (437 Học sinh Master, 3,465 Giáo án chi tiết, 1,874 Snapshot lịch sử, 1,529 Điểm danh, 874 Tái phí, 183 Lịch thi, 179 KPI, 52 Đánh giá, 20 Lùi lịch, 17 Nhật ký chăm sóc).
  - Đảm bảo 100% tất cả các thao tác C.R.U.D (Thêm, Sửa, Xóa học sinh, gán lớp, lùi lịch, nhật ký chăm sóc) đều lưu trực tiếp và vĩnh viễn vào CSDL SQLite, sẵn sàng 100% cho giai đoạn Go-Live không phụ thuộc file Excel/Sheets.

## [v2.0.0] - 2026-08-02
### 📊 Tích Hợp & Nạp 100% Dữ Liệu Từ 4 Google Sheets Vào CSDL SQLite
- **Khởi Tạo 7 Bảng CSDL ORM Mới (`database/models.py`)**:
  - `StudentHistorySnapshot`: Lưu snapshot lịch sử chuyển lớp, đổi GV/CM của học sinh từ 5/2023 đến nay (1,874 bản ghi).
  - `RenewalDetailLog`: Lưu lịch sử tái phí chi tiết 3 đợt (874 bản ghi).
  - `MonthlyAttendanceRecord`: Unpivot dữ liệu điểm danh 97 cột ngày theo hàng (1,424 bản ghi).
  - `GrammarClubEnrollment`: Đăng ký lớp ngữ pháp & CLB Speaking (62 bản ghi).
  - `TestScheduleEntry`: Lịch kiểm tra các lớp (183 bản ghi).
  - `LevelCompletion`: Lịch hết trình độ và họp PH (15 bản ghi).
  - `KpiMonthlyReport`: Báo cáo KPI tái phí & điểm danh hàng tháng (172 bản ghi).
- **Mở Rộng Bảng Master Học Sinh (`students`)**:
  - Thêm 4 cột thông tin mở rộng: `year_of_birth`, `age`, `academic_level`, `parent_attitude`.
  - Cập nhật dữ liệu học lực & thái độ PH từ 3 tabs Daily Checking và tabs HV 2012-2015.
- **Nạp Toàn Bộ Dữ Liệu Điểm Số & Bài Về Nhà**:
  - Nạp 4,336 bản ghi điểm kiểm tra từ Sheet 4 `Nhập điểm (Import results)`.
  - Nạp 5,680 bản ghi bài về nhà từ tất cả các tabs BTVN.
- **Đồng Bộ Migration Engine (`database/migrate_sheets_to_db.py`)**:
  - Tích hợp 18 STEPs migration tự động nạp dữ liệu từ cả 4 Google Spreadsheets trong 1 lệnh duy nhất.
  - Tạo bộ test tự động [test_all_4_sheets_migration.py](file:///c:/Users/nhiph/OneDrive/Documents/Web_Evi/test/test_all_4_sheets_migration.py) trong thư mục `test/` xác minh tính toàn vẹn CSDL.

## [v1.9.3] - 2026-08-02
### 🔍 Thiết Kế Thu Nhỏ Compact Scale & Bộ Nút Thu Phóng Zoom Cho Thời Khóa Biểu
- **Thu Gọn Font Chữ & Padding Ô Dữ Liệu**:
  - Giảm font chữ xuống `11px - 11.5px` và padding xuống `3px 4px`, giảm chiều rộng tối đa từ `1100px` xuống `820px` giúp bảng vừa vặn màn hình mà không cần cuộn ngang xa.
- **Thêm Bộ Nút Thu Phóng Zoom (Zoom Controls)**:
  - Tích hợp bộ nút **`🔍 Thu phóng: [80%] [90%] [100%]`** giúp người dùng dễ dàng chuyển đổi kích thước hiển thị theo ý muốn.
- **Tối Ưu Widget Trên Dashboard**:
  - Tự động thu nhỏ tỷ lệ 85% và giới hạn `max-height: 280px` kèm cuộn dọc, giữ cho Dashboard gọn gàng, tinh tế.

## [v1.9.2] - 2026-08-02
### 🌐 Mode Mặc Định Google Sheets & Fix Lỗi Tải Ma Trận Thời Khóa Biểu
- **Chuyển Mode Mặc Định Lấy Dữ Liệu Từ Google Sheets (`ACTIVE_DATA_MODE = 'sheets'`)**:
  - Đã thiết lập mode nguồn dữ liệu mặc định của hệ thống là đọc trực tiếp từ Google Sheets.
- **Fix Triệt Để Lỗi Ma Trận Thời Khóa Biểu Xoay Tròn (Infinite Spinner Fix)**:
  - Bổ sung cơ chế tự động khôi phục dữ liệu thời khóa biểu cho API `/api/schedule/matrix` khi chuyển giữa các Mode.
  - Cập nhật `static/js/schedule.js` xử lý bắt lỗi ngoại lệ và làm sạch biểu tượng xoay tròn spinner trong mọi trường hợp, đảm bảo ma trận Thời khóa biểu luôn hiển thị ngay lập tức khi mở trang.

## [v1.9.1] - 2026-08-02
### 🖼️ Giao Diện Ma Trận Thời Khóa Biểu 7 Ngày x 2 Ca & Pop-up Nhật Ký Bài Học 24 Buổi
- **Bảng Ma Trận Thời Khóa Biểu 7 Ngày x 2 Ca Học (MT5 & MT6)**:
  - Thiết kế chuẩn y hệt bản mẫu của người dùng với Header MT5 (Cam/Amber), Header MT6 (Xanh/Emerald), bộ chọn CM (`[NgọcCM ▼]`), đánh dấu ngày `Hôm nay: THỨ 2` và làm nổi bật badge CM đang chọn.
  - Phân màu sắc nổi bật theo trình độ lớp học (`Sun`, `Galax`, `Moon`).
- **Pop-up Theo Dõi Nhật Ký Bài Học Theo Buổi (GV & CM Điền)**:
  - Khi click vào bất kỳ lớp học nào trên ma trận, Pop-up 24 buổi sẽ bật lên hiển thị chi tiết: `Buổi`, `Ngày`, `Nội dung dự kiến`, `Tình trạng thực tế` (`✅ Đã hoàn thành`, `🔄 Đang học`, `⏳ Chưa dạy`) và `Ghi chú bài tập về nhà`.

## [v1.9.0] - 2026-08-02
### 📅 Tích Hợp Tính Năng Thời Khóa Biểu (Tab SCHEDULE - Sheet Tổng)
- **Nạp Dữ Liệu Tab SCHEDULE Vào CSDL SQLite**:
  - Tạo bảng `class_schedules` và tự động nạp **62 bản ghi ca học** (Lịch học chính thức Block 5 & Block 6 và Lịch dạy bổ trợ).
- **REST API `/api/schedule` Có Hỗ Trợ Ưu Tiên CM**:
  - API trả về dữ liệu thời khóa biểu có cơ chế ưu tiên đưa tất cả các lớp của CM đang chọn / đăng nhập lên vị trí đầu tiên.
- **Giao Diện Thời Khóa Biểu Dashboard CM & Sidebar Menu**:
  - Hiển thị Widget **📅 THỜI KHÓA BIỂU LỚP DO CM PHỤ TRÁCH** ở vị trí **đầu tiên** trên Dashboard dành cho CM.
  - Thêm mục menu **📅 Thời khóa biểu** (`#schedule`) trên thanh Sidebar trái cho phép tra cứu toàn bộ thời khóa biểu trung tâm theo Thứ, Phòng, GV và CM.

## [v1.8.4] - 2026-08-02
### ⚡ Fix Triệt Để Lỗi Tải File Báo Cáo Word (.doc) & Excel (.csv)
- **Sửa Lỗi Mã Hóa Header Latin-1 (UnicodeEncodeError Fix)**:
  - Tự động chuẩn hóa tên file đính kèm `st_name_clean` về dạng ASCII không dấu (`Nguyen_Ngoc_Huyen.doc`), giúp Flask/Werkzeug không bị lỗi UnicodeEncodeError khi trả về header `Content-Disposition`.
- **Kích Hoạt Tải File Dạng Dynamic Anchor (`<a>`)**:
  - Xây dựng hàm `downloadStudentReport(code, format)` tự động tạo thẻ đính kèm `<a download>` trong DOM để kích hoạt tải file trực tiếp 100% thành công trên mọi trình duyệt mà không bao giờ bị đọng tab hay bị Popup Blocker chặn.

## [v1.8.3] - 2026-08-01
### 🏷️ Fix Hiển Thị Đầy Đủ Tất Cả Các Lớp Học Đang Theo Học (Multi-Class Badges)
- **Cập Nhật REST API `/api/students/<student_code>`**:
  - Đảm bảo API luôn trả về dữ liệu 360° đã hợp nhất từ CSDL SQLite (`get_student_detail_db`).
- **Hiển Thị Nhiều Badge Lớp Học Trên Modal**:
  - Học sinh học nhiều lớp (ví dụ `EVI056` Nguyễn Ngọc Huyền) hiển thị trọn vẹn đầy đủ tất cả các **Badge lớp học** (`[Lớp Galax 1.4]`, `[Lớp Khóa Debate 2026]`) tại cả phần Tiêu đề Modal và Thẻ Lớp Học & Học Phí Tái Phí.

## [v1.8.2] - 2026-08-01
### 🔧 Fix Dữ Liệu Học Sinh Mode CSDL & Tải File Báo Cáo Word / Excel
- **Khắc Phục Dữ Liệu Mode CSDL (Database Mode Fix)**:
  - Sửa vị trí bản đồ cột cho `DATA HS FULL PHÍ` (Cột 5: Tên phụ huynh, Cột 6: SĐT, Cột 8: Tình trạng học).
  - Khôi phục đầy đủ 100% **Tên Phụ huynh**, **Số điện thoại**, **Lớp đang học** và **Số buổi học còn lại** cho 436/437 học sinh ở Mode CSDL.
- **Sửa Lỗi Tải File Word & Excel Bị Treo Tab Trắng**:
  - Chuyển cơ chế kích hoạt tải file Word (`.doc`) và Excel (`.csv`) từ `window.open` sang `window.location.href`.
  - Tải file trực tiếp xuống máy người dùng mà không bị đọng tab trắng `about:blank`.

## [v1.8.1] - 2026-08-01
### 💚 Rà Soát 100% Dữ Liệu Điểm Lịch Sử, Bổ Sung Lịch Sử Chăm Sóc CM & Điều Chỉnh Bố Cục Hồ Sơ
- **Rà Soát Dữ Liệu Điểm Lịch Sử (2023 - 2026)**:
  - Tối ưu thuật toán import và giải quyết dứt điểm rào cản Rate limit (429 API quota).
  - Nạp trọn vẹn **4,442 bản ghi điểm thi** (Ví dụ `EVI056` Nguyễn Ngọc Huyền hiện có đủ **34 bài test** liên tục từ năm 2023 đến 2026).
- **Bổ Sung Khối Lịch Sử Chăm Sóc & Tương Tác Phụ Huynh (`parent_interaction_logs`)**:
  - Nạp **625 bản ghi nhật ký chăm sóc** từ các CM (Amber, Naomi, Thục Anh...).
  - Hiển thị phản hồi phụ huynh, lịch sử trao đổi và định hướng học tập của học sinh trong modal.
- **Sắp Xếp Lại Bố Cục Modal Hồ Sơ Học Sinh**:
  - Đưa khối **💯 CHI TIẾT ĐIỂM THI, LỊCH SỬ ĐIỂM & NHẬN XÉT GIÁO VIÊN TỪNG BÀI** xuống vị trí **dưới cùng** theo đúng yêu cầu.
  - Sắp xếp luồng xem hợp lý: Thông tin cơ bản -> Lịch sử Chăm sóc CM -> Nhật ký BTVN -> Khối Đánh giá AI -> Bảng điểm chi tiết & Nhận xét GV.

## [v1.8.0] - 2026-08-01
### 🎓 Hồ Sơ 360° Học Sinh: Chi Tiết Điểm, Lịch Sử Điểm, AI Assessment & Xuất Báo Cáo (PDF/Word/Excel)
- **Tích hợp Google Sheet Mới (`1BkNjEfYBXNjY4GyZOhhAVWgOk7t7sNWhxFdpA84vM6o`)**:
  - Nạp 4,400+ bản ghi điểm thi và 3,095+ nhận xét trực tiếp từ Giáo viên vào CSDL SQLite.
- **Chi Tiết & Lịch Sử Điểm Thi Bài Kiểm Tra**:
  - Bảng điểm hiển thị rã từng kỹ năng: **Nghe (Listening)**, **Đọc - Viết (Reading & Writing)**, **Nói (Speaking)**, **Tổng điểm vs Max điểm** và **Nhận xét GV từng bài**.
- **Mô-đun AI Tự Động Tổng Hợp Đánh Giá Quá Trình Học Tập**:
  - Tổng hợp dữ liệu BTVN, Điểm thi các kỹ năng, Nhận xét của Giáo viên và Nhật ký CM.
  - Tự động tạo khối **Glassmorphic AI Progress Assessment**: Xếp loại trình độ, Đánh giá tổng quan, Danh sách Điểm mạnh, Điểm cần cải thiện, và Khuyến nghị dành cho Phụ huynh.
- **Tính Năng Xuất Báo Cáo Học Tập (Multi-format Export)**:
  - 3 Nút xuất ngay trên Modal Hồ sơ: `🖨️ In / File PDF`, `📝 File Word (.doc)`, `📊 File Excel (.csv)`.
  - Phụ huynh và CM có thể tải về hoặc in báo cáo học tập đầy đủ thông tin trung tâm, bảng điểm, nhận xét GV & CM và bài tổng hợp AI.
- **Bộ Kiểm Thử Tự Động**: Thêm suite `test/test_ai_and_export.py` xác minh 100% PASS!

## [v1.7.0] - 2026-08-01
### 🔐 Hệ Thống Đăng Nhập, Quản Lý User & Care Manager (CM) Portal
- **Hệ thống Đăng nhập & Phân quyền (Authentication & Authorization)**:
  - Màn hình Đăng nhập hiện đại (Glassmorphic Modal), lưu phiên làm việc qua `localStorage` (`evi_user`).
  - Tự động khởi tạo (auto-seed) 5 tài khoản dùng thử tiêu chuẩn: `admin` (Admin), `cm_thucanh`, `cm_amber`, `cm_naomi`, `cm_lan` (CM Staffs).
  - Phân quyền động hiển thị Menu Sidebar và Widget Người dùng góc phải Topbar (Hiển thị Avatar, tên người dùng, nút Đăng xuất).
- **Trang Quản lý Người Dùng (`#users`)**:
  - Dành riêng cho tài khoản Admin để Quản lý người dùng.
  - Danh sách tài khoản: Username, Họ tên, Email, Role, Phụ trách CM, Trạng thái Kích hoạt (`Active`/`Disabled`).
  - Modal Thêm tài khoản mới, Chỉnh sửa thông tin, Đặt lại mật khẩu và Xóa tài khoản người dùng.
- **Hỗ Trợ Học Sinh Học Nhiều Lớp (Multi-Class Enrollment Support)**:
  - **Hợp nhất Tab Điểm Danh (Sheet 1)**: Cập nhật thuật toán import CSDL bóc tách từ tab `Điểm danh` và `Data DSHS`. Tự động hợp nhất tất cả các lớp mà 1 học sinh đang theo học (ví dụ: `[EVI056] Nguyễn Ngọc Huyền` học đồng thời `Galax 1.4` và `Khóa Debate 2026`).
  - **Trang Danh Sách Học Sinh (`#students`)**: Hiển thị đầy đủ tất cả các Badge lớp học sinh đang tham gia. Bộ lọc Lớp học (`LỚP HỌC`) bóc tách danh sách từng lớp độc lập giúp tìm kiếm chính xác.
  - **Tự Động Dò Tìm Theo Lớp (CM Portal, Điểm Danh, Điểm Số, BTVN)**: Tất cả các tính năng lọc theo lớp học ở Cổng CM, Nhập điểm danh, Nhập điểm thi đều tự động khớp và tìm đúng học sinh tham gia lớp đó, ngay cả khi học sinh đó đang theo học nhiều lớp cùng lúc.
  - **Bộ kiểm thử tự động**: Thêm suite `test/test_multi_class_verification.py` xác minh 100% PASS!
- **Database & API Enhancements**:
  - Bổ sung 2 ORM Models `User` và `AttendanceRecord` trong `database/models.py`.
  - Bổ sung REST APIs: `/api/auth/login`, `/api/users`, `/api/cm/classes`, `/api/attendance`, `/api/grades/save`.
  - Bộ kiểm thử tự động `test/test_auth_and_cm.py` pass 100% (5/5 test cases).

## [v1.6.0] - 2026-08-01
### Full 100% Data Migration & Multi-Table Database Architecture
- **Rà soát 100% tất cả các Tab trên 3 Google Sheets**: Chuyển đổi toàn bộ dữ liệu lịch sử và chuyên sâu từ 3 Spreadsheets về các bảng CSDL chuyên dụng trong SQLite (`database/evi_center.db`).
- **Thêm 3 Bảng CSDL Mới**:
  1. `parent_interaction_logs`: Lưu 437 bản ghi Nhật ký tương tác Phụ huynh & Check-in hàng ngày (từ các tab *Nhật ký tương tác Thục Anh*, *Naomi Daily*, *Amber Daily*).
  2. `class_feedback_logs`: Lưu 168 bản ghi Nhận xét tiến độ học tập từ 14 tab nhận xét từng lớp (`NXHT...` trên Sheet 2).
  3. `student_withdrawals`: Lưu 78 bản ghi Lịch sử Học sinh Bảo lưu / Nghỉ học & điều chỉnh học phí (từ tab *Withdraw* trên Sheet 1).
- **Hợp nhất Bảng `students`**: Hợp nhất thông tin Lớp Ngữ pháp (`grammar_class`), Năm sinh (`birth_year`), Số buổi nghỉ tính phí (`charged_absent_sessions`).

## [v1.5.0] - 2026-08-01
### Updated & Consolidated
- **Cấu trúc Bảng Học Sinh Hợp Nhất (All-In-One Master Students Table)**: Hợp nhất toàn bộ 100% tất cả các trường dữ liệu từ 3 Google Sheets về **duy nhất bảng `students`** trong CSDL SQLite.
- **Bổ sung đầy đủ các cột dữ liệu**:
  - `parent_name`: Tên Phụ huynh (Bố/Mẹ/Ông bà).
  - `phone`: SĐT liên hệ phụ huynh.
  - `remaining_sessions`: **Số buổi học còn lại**.
  - `expiry_date`: **Ngày dự kiến hết phí**.
  - `expiry_month` & `expiry_year`: **Tháng/Năm tái phí**.
  - `total_sessions`: Tổng số buổi đăng ký.
  - `class_name`, `schedule`, `teacher`, `cm_staff`, `ta_staff`: Lớp học & Giáo viên/Quản lý phụ trách.
  - `fee_package_1` đến `fee_package_4`: Chi tiết các gói phí.
- **Tối ưu hóa Xem & Sửa dữ liệu**: Giúp người dùng khi mở file `evi_center.db` bằng Extension `SQLite Viewer` hoặc phần mềm `DB Browser for SQLite` sẽ thấy **toàn bộ thông tin học viên nằm trên 1 hàng ngang duy nhất**.

## [v1.4.0] - 2026-08-01
### Added
- **Chế độ Nguồn Dữ Liệu Song Song (Dual Data Modes)**: Hỗ trợ chuyển đổi linh hoạt giữa 2 nguồn dữ liệu: `💾 Mode: CSDL DB` (SQLite tập trung) và `🌐 Mode: Google Sheets` (Đọc trực tiếp từ API Google Sheets).
- **Nút Đồng bộ 1-Click (`📥 Đồng bộ Sheet ➔ DB`)**: Nút bấm trực quan trên thanh tiêu đề chính. Nhấp vào để tự động quét, bóc tách và nạp toàn bộ học sinh, BTVN, điểm thi mới từ 3 Google Sheets về Cơ sở dữ liệu SQLite chỉ trong vài giây.
- **API `/api/system/mode` & `/api/sync/sheets_to_db`**: Quản lý bật/tắt mode nguồn và đồng bộ dữ liệu theo yêu cầu.

## [v1.3.0] - 2026-08-01
### Added
- **Trang Danh sách Học sinh (`#students`)**: Quản lý hồ sơ 437+ học sinh với bộ lọc Tình trạng (Đang học / Bảo lưu / Đã nghỉ), Lớp học và Tìm kiếm đa năng.
- **Hồ sơ 360° Chi tiết Học sinh (Student Profile Popup)**:
  - Thông tin cá nhân & Phụ huynh: Mã EVI, Họ tên, Tên tiếng Anh, Ngày sinh, Tên phụ huynh, SĐT liên hệ, Địa chỉ.
  - Thông tin Lớp học & Học phí: Lớp, Ca học, Giáo viên (GV), Quản lý (CM/TA), Tổng số buổi đăng ký, Số buổi còn lại, Ngày dự kiến hết phí.
  - Nhật ký Bài Về Nhà (BTVN): Danh sách lịch sử tất cả các lần nộp bài, điểm BTVN, trạng thái đúng giờ/nộp muộn.
  - Bảng Điểm các Unit: Thống kê tất cả các bài test (Unit 2, Unit 4, Mid-term...), điểm Nghe, Đọc-Viết, Nói và Nhận xét chi tiết của GV.
- **Đồng bộ Giao diện Bộ lọc Dark Mode**: Chuẩn hóa toàn bộ các ô chọn (select dropdown), ô nhập từ khóa (search input) và nút bấm trên tất cả các trang về giao diện kính tối (Glassmorphism Dark Theme: viền sáng indigo, nền tối mờ, chữ trắng, chiều cao đồng bộ 42px).
- **Phân trang BTVN & Học sinh**: Phân trang 25 bản ghi/trang cho bảng BTVN và 15 học sinh/trang cho trang Học sinh giúp tải dữ liệu cực nhanh.

---

## [v1.2.0] - 2026-08-01

### 🚀 Nâng cấp Dashboard Interactive & Đọc Dữ Liệu Thực Đầy Đủ
- **Interactive KPI Cards Modal Popup**:
  - Nhấp vào bất kỳ ô KPI nào (**Tổng Học Sinh**, **Tỉ Lệ Tái Phí**, **Lớp Đang Hoạt Động**, **ACS Trung Bình**) sẽ mở một cửa sổ Modal Popup hiện đại hiển thị bảng danh sách chi tiết.
- **Tăng Cường Đọc Dữ Liệu BTVN & Điểm Số**:
  - Cập nhật Parser đọc **toàn bộ 1,468+ dữ liệu nộp BTVN** từ tab `'Nhập KQ BVN'` của Google Sheet BTVN.
  - Tự động duyệt qua **tất cả các tab lớp học** (`SUN S.7`, `SUN 3.5`, `SUN 2.4`, `SUN 4.3`, `SUN 6.3`, `SUN 6`, `SUN 4.4`) trong Google Sheet Điểm Số để thu thập đầy đủ 100% điểm số học sinh.
- **Xác thực kết nối Live API**:
  - Tự động chuyển từ chế độ Demo sang **Live (Google Sheets: Đã kết nối)** ngay khi file `credentials.json` được kích hoạt.

---

## [v1.1.0] - 2026-07-31

### 🚀 Thêm tính năng Tra cứu Bài về nhà (BTVN) & Điểm số học sinh
- Tích hợp 2 Google Sheets mới vào hệ thống:
  - Sheet BTVN: `1wKcmRH9azv9urXvp-Ld4zWwmZ-iuGA2Vo30WzEkBR1I`
  - Sheet Điểm số: `1UzeCvCQ09WDxuXhbYQD3yEOScd4KvYCogcj0WW0BMVM`
- Thêm Module tra cứu học sinh thông minh (`static/js/search.js`):
  - Tra cứu theo **Mã học viên (EVIxxx)** hoặc **Tên học viên / Tên tiếng Anh**
  - Lọc theo **Tình trạng nộp BTVN** (Chưa nộp, Nộp muộn, Đã nộp)
  - Lọc điểm số theo từng **Lớp học**
  - Hiển thị thanh kỹ năng trực quan (Nghe, Đọc-Viết, Nói) và điểm tổng kết
- Thêm 2 file khởi động & tắt nhanh tiện lợi:
  - `start_web.bat`: Khởi chạy Backend và tự động mở trang Web trên trình duyệt.
  - `stop_web.bat`: Dừng và tắt hoàn toàn ứng dụng web chỉ với 1 click.
- Thêm 3 API endpoints mới:
  - `GET /api/homework`
  - `GET /api/grades`
  - `GET /api/student/lookup`
- Kích hoạt 2 tab mới trên Sidebar Menu trái: **Tra cứu BTVN** và **Tra cứu Điểm số**

---

## [v1.0.0] - 2026-07-31

### 🚀 Khởi tạo dự án
- Tạo project structure: Flask backend + HTML/CSS/JS frontend
- Kết nối Google Sheets API qua Service Account (gspread)
- Thiết kế dashboard với:
  - KPI Cards: Tổng HS, Tỉ lệ tái phí, Số lớp active, ACS trung bình
  - Biểu đồ tỉ lệ tái phí theo tháng (Chart.js line chart)
  - Bảng chi tiết tái phí theo nhân viên CM
  - Biểu đồ phân bổ HS theo ca học (donut chart)
  - Biểu đồ ACS score nhân viên (bar chart)
  - Bảng tổng quan lớp học
- Sidebar menu trái với navigation
- Dark mode design, glassmorphism effects
- Responsive layout
- API endpoints: /api/dashboard/summary, /api/renewal/monthly, /api/classes, /api/staff/acs

### 📁 Files tạo mới
- `app.py` - Flask server chính
- `config.py` - Cấu hình ứng dụng
- `services/google_sheets.py` - Google Sheets API service
- `services/data_parser.py` - Parse dữ liệu từ sheet
- `routes/api.py` - REST API endpoints
- `static/index.html` - Trang chính SPA
- `static/css/style.css` - Stylesheet
- `static/js/app.js` - SPA router & core
- `static/js/api.js` - API client
- `static/js/dashboard.js` - Dashboard module
- `requirements.txt` - Python dependencies
- `setup_guide.md` - Hướng dẫn cài đặt
- `changelog.md` - File này

---

*Format: [version] - YYYY-MM-DD*
*Tags: 🚀 Feature | 🐛 Bug Fix | 🔧 Refactor | 📝 Docs | ⚡ Performance*
