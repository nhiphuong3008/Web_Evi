# 🚀 PROJECT SUMMARY & ARCHITECTURE OVERVIEW - EVI DASHBOARD

> **Dành cho AI Agent**: Đọc file này để nắm bắt trọn vẹn kiến trúc, CSDL và quy tắc phát triển của dự án Web EVI trong vài giây mà không tốn quota prompt.

---

## 📌 1. TỔNG QUAN HỆ THỐNG (SYSTEM OVERVIEW)
- **Tên ứng dụng**: **EVI Dashboard** (Hệ Thống Quản Lý Trung Tâm Tiếng Anh EVI).
- **Công nghệ chính**:
  - **Backend**: Python 3.12 + Flask Framework + SQLAlchemy ORM.
  - **Database**: SQLite CSDL local (`database/evi_center.db`).
  - **Frontend**: HTML5 + Vanilla CSS (Mỹ thuật hiện đại / Studio Ghibli Theme) + Vanilla JavaScript (Modular ES6).
- **Cổng chạy (Port)**: `http://127.0.0.1:5001`.

---

## 🗄️ 2. KIẾN TRÚC CSDL & QUY TẮC DB-FIRST (GO-LIVE DB PERSISTENCE)

> ⚠️ **QUY TẮC BẮT BUỘC (CRITICAL RULE)**:
> 1. Khi Golive hệ thống sẽ dùng **100% CSDL SQLite (DB)**. Dữ liệu từ Google Sheets / Excel chỉ là dữ liệu phi cấu trúc ban đầu.
> 2. Mọi thao tác Thêm, Sửa, Xóa từ Web hoặc Script bắt buộc phải lưu trực tiếp vào CSDL SQLite (`database/evi_center.db`).
> 3. **BẢO VỆ NGUYÊN VẸN CÁC MODULE CỐT LÕI**: Các mục *Thêm lớp mới & Quản lý lớp, Schedule, Syllabus, Báo cáo học tập, Danh sách học sinh* KHÔNG được tự ý chỉnh sửa làm ảnh hưởng. Nếu có sự liên kết bắt buộc, AI phải thông báo và xin ý kiến phê duyệt của USER trước khi thực hiện.

### 📊 Bảng CSDL ORM Chính (`database/models.py`) - Tổng cộng > 14,600 bản ghi có cấu trúc:
1. `Student` (`students`): 437 Hồ sơ học sinh master.
2. `LessonSyllabus` (`lesson_syllabuses`): 3,465 Buổi học giáo án chi tiết của 51 lớp.
3. `ClassSchedule` (`class_schedules`): 38 Lớp học trong ma trận thời khóa biểu.
4. `ClassScheduleAdjustment` (`class_schedule_adjustments`): 20 Bản ghi điều chỉnh lùi lịch.
5. `ParentInteractionLog` (`parent_interaction_logs`): 17 Nhật ký chăm sóc phụ huynh.
6. `StudentHistorySnapshot` (`student_history_snapshots`): 1,874 Snapshot lịch sử học sinh từ 2023.
7. `RenewalDetailLog` (`renewal_detail_logs`): 874 Lịch sử tái phí chi tiết 3 đợt.
8. `MonthlyAttendanceRecord` (`monthly_attendance_records`): 1,529 Điểm danh unpivot 97 ngày.
9. `GrammarClubEnrollment` (`grammar_club_enrollments`): Đăng ký lớp Ngữ pháp & CLB Speaking.
10. `TestScheduleEntry` (`test_schedule_entries`): 183 Lịch kiểm tra các lớp.
11. `LevelCompletion` (`level_completions`): 15 Lịch hoàn thành trình độ & họp PH.
12. `KpiMonthlyReport` (`kpi_monthly_reports`): 179 Báo cáo KPI tái phí & điểm danh hàng tháng.

---

## 📁 3. SƠ ĐỒ THƯ MỤC & FILE CHÍNH (FILE MAP)

```
Web_Evi/
├── app.py                      # Server Flask Backend (Entry Point API - 100% DB-driven)
├── config.py                   # Cấu hình biến môi trường
├── changelog.md                # ⚠️ NHẬT KÝ THAY ĐỔI (Ghi log mọi sửa đổi ở đây)
├── PROJECT_SUMMARY.md          # 📜 File tóm tắt dự án AI đọc ưu tiên
├── .agents/
│   └── AGENTS.md               # ⚙️ Workspace Rules cho AI Agent (Tự động nạp mỗi phiên)
├── database/
│   ├── models.py               # Tất cả 12 SQLAlchemy ORM Models
│   ├── db_manager.py           # Quản lý kết nối & Session CSDL SQLite
│   ├── evi_center.db           # CSDL SQLite chính thức
│   └── parse_and_import_templates.py # Script nạp giáo án Excel -> DB
├── services/
│   ├── db_service.py           # Business logic chính đọc/ghi CSDL & xử lý bài học/BTVN
│   ├── sync_scheduler.py       # 🔄 Module chạy ngầm 1 tiếng/lần Incremental Sync Google Sheets -> DB (UPSERT)
│   └── google_sheets.py        # Kết nối API đọc Google Sheets
├── routes/                     # Blueprint API Endpoints (100% DB Mode)
├── static/
│   ├── index.html              # Single Page App chính (SPA)
│   ├── css/style.css           # Vanilla CSS Design System (Ghibli Theme, Flat, Soft Shadow)
│   └── js/
│       ├── app.js              # Khởi tạo SPA
│       ├── dashboard.js        # Dashboard KPI, Modal Stack (modalStack, pushModalState, closeModal)
│       ├── schedule.js         # Ma trận Thời khóa biểu, Pop-up Nhật ký lớp, Thẻ Báo Cáo Ghibli
│       ├── students.js         # Quản lý Học sinh & Hồ sơ 360
│       └── auth.js             # Đăng nhập & Phân quyền
└── test/                       # ⚠️ TẤT CẢ FILE TEST/SCRIPT THỬ NGHIỆM BẮT BUỘC ĐẶT Ở ĐÂY
```

---

## 📜 4. QUY TẮC PHÁT TRIỂN & QUY TRÌNH LÀM VIỆC (AGENT MANDATES)

1. **GHI LOG MỌI THAY ĐỔI**: Sau khi hoàn thành bất kỳ tính năng hay sửa lỗi nào, **bắt buộc cập nhật ngay vào `changelog.md`** dưới mục phiên bản mới nhất.
2. **LƯU TRỮ TEST TRONG `test/`**: Tất cả script thử nghiệm, kiểm tra dữ liệu **bắt buộc đặt trong thư mục `test/`** (ví dụ `test/test_homework.py`). Không tạo file rác ở thư mục gốc.
3. **ĐÓNG MODAL PHÂN CẤP (INCREMENTAL CLOSING)**: Sử dụng `Dashboard.pushModalState()` và `Dashboard.closeModal()` để đóng từng bước (step-by-step) về pop-up mẹ, không đóng hoàn toàn về trang gốc khi đang xem xem sub-modal/preview.
4. **BẢO TỒN CSDL DUAL-WRITE & GO-LIVE DB**: Mọi dữ liệu từ Google Sheets/Excel phi cấu trúc hoặc từ giao diện web (Thêm/Sửa/Xóa) **bắt buộc phải lưu song song / trực tiếp vào CSDL SQLite (`database/evi_center.db`)** để sẵn sàng 100% cho giai đoạn Go-Live.
