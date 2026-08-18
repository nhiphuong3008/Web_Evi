import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import (
    Student, LessonSyllabus, ClassSchedule, ClassScheduleAdjustment,
    ParentInteractionLog, StudentHistorySnapshot, RenewalDetailLog,
    MonthlyAttendanceRecord, GrammarClubEnrollment, TestScheduleEntry,
    LevelCompletion, KpiMonthlyReport
)

session = db_session()

print("=" * 70)
print("  AUDIT TỔNG THỂ DỮ LIỆU CÓ CẤU TRÚC TRONG CSDL SQLITE (evi_center.db)")
print("=" * 70)

models_to_check = [
    ("Học sinh Master (Student)", Student),
    ("Khung Giáo Án Chi Tiết (LessonSyllabus)", LessonSyllabus),
    ("Thời Khóa Biểu Lớp (ClassSchedule)", ClassSchedule),
    ("Lùi Lịch Buổi Học (ClassScheduleAdjustment)", ClassScheduleAdjustment),
    ("Nhật Ký Chăm Sóc PH (ParentInteractionLog)", ParentInteractionLog),
    ("Snapshot Lịch Sử HS (StudentHistorySnapshot)", StudentHistorySnapshot),
    ("Lịch Sử Tái Phí (RenewalDetailLog)", RenewalDetailLog),
    ("Điểm Danh Hàng Tháng (MonthlyAttendanceRecord)", MonthlyAttendanceRecord),
    ("Đăng Ký CLB / Ngữ Pháp (GrammarClubEnrollment)", GrammarClubEnrollment),
    ("Lịch Kiểm Tra (TestScheduleEntry)", TestScheduleEntry),
    ("Lịch Hoàn Thành Trình Độ (LevelCompletion)", LevelCompletion),
    ("Báo Cáo KPI (KpiMonthlyReport)", KpiMonthlyReport),
]

for name, model in models_to_check:
    cnt = session.query(model).count()
    status = "✅ OK" if cnt > 0 else "⚠️ TRỐNG"
    print(f"  {status} {name:48s}: {cnt:6d} bản ghi")

session.close()
