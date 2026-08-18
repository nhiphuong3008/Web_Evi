"""
EVI Dashboard - Consolidated Database Models (SQLAlchemy ORM)
Quản lý 100% dữ liệu từ 3 Google Sheets:
- Bảng Master Học Sinh hợp nhất (students)
- Bảng Lớp Học (classes)
- Bảng Bài Về Nhà (homework_records)
- Bảng Điểm Thi các Unit (unit_grades)
- Bảng Nhật Ký Tương Tác Phụ Huynh (parent_interaction_logs)
- Bảng Nhận Xét Học Tập Theo Lớp (class_feedback_logs)
- Bảng Lịch Sử Học Sinh Bảo Lưu / Nghỉ Học (student_withdrawals)
- Bảng Rà Soát Thủ Công (audit_unmatched_records)
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

Base = declarative_base()


class Student(Base):
    """
    Bảng Học Sinh Hợp Nhất (All-in-One Master Students Table)
    Lưu trữ 100% tất cả các trường dữ liệu được gắn với học sinh từ cả 3 Google Sheets.
    Mã học sinh cố định vĩnh viễn (EVI001, EVI002...), giữ lại khi học sinh nghỉ/bảo lưu.
    """
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # Mã HS cố định (EVI001...)
    full_name = Column(String(255), nullable=False, index=True)         # Họ tên học sinh
    english_name = Column(String(100), index=True)                      # Nickname (Tên tiếng Anh)
    dob = Column(String(50))                                            # Ngày sinh
    birth_year = Column(String(20))                                     # Năm sinh
    parent_name = Column(String(255))                                   # Tên Phụ huynh (Bố / Mẹ / Phụ huynh)
    phone = Column(String(100), index=True)                             # SĐT liên hệ
    address = Column(Text)                                              # Địa chỉ
    status = Column(String(50), default='Đang học', index=True)         # Tình trạng ('Đang học', 'Bảo lưu', 'Đã nghỉ')

    # Thông tin Lớp học & Phụ trách
    # Thông tin Lớp học & Phụ trách
    class_name = Column(String(100), index=True)                        # Lớp đang học
    last_class_name = Column(String(100))                               # Lớp học cuối cùng / gần nhất trước khi bảo lưu/nghỉ
    schedule = Column(String(100))                                      # Ca học (TF5, MT5...)
    room = Column(String(100))                                          # Phòng học
    teacher = Column(String(100))                                       # Giáo viên chính (GV)
    cm_staff = Column(String(100))                                      # Quản lý (CM)
    ta_staff = Column(String(100))                                      # Trợ giảng (TA)
    grammar_class = Column(String(100))                                 # Lớp ngữ pháp / CLB

    # Thông tin Học phí & Số buổi học & Tái phí
    total_sessions = Column(Integer, default=0)                         # Tổng số buổi đăng ký
    remaining_sessions = Column(Integer, default=0)                     # Số buổi học còn lại
    charged_absent_sessions = Column(Integer, default=0)                # Số buổi nghỉ tính phí
    expiry_date = Column(String(50))                                    # Ngày dự kiến hết phí
    expiry_month = Column(String(50))                                   # Tháng hết phí / tái phí
    expiry_year = Column(String(50))                                    # Năm hết phí
    renewal_status_2025 = Column(String(100))                           # Tình trạng tái phí 2025

    # Chi tiết Gói phí
    fee_package_1 = Column(String(100))
    fee_package_2 = Column(String(100))
    fee_package_3 = Column(String(100))
    fee_package_4 = Column(String(100))

    # Bổ sung: Thông tin Tuổi / Học lực / PH (từ tabs HV 2012-2015, Naomi/Amber Daily Checking)
    year_of_birth = Column(String(20))                                  # Năm sinh (2012, 2013...)
    age = Column(String(20))                                            # Độ tuổi hiện tại
    academic_level = Column(Text)                                       # Nhận xét học lực chi tiết
    parent_attitude = Column(Text)                                      # Tình trạng / Thái độ phụ huynh

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    homework_records = relationship("HomeworkRecord", back_populates="student", cascade="all, delete-orphan")
    unit_grades = relationship("UnitGrade", back_populates="student", cascade="all, delete-orphan")
    parent_interactions = relationship("ParentInteractionLog", back_populates="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.full_name,
            'english_name': self.english_name or '',
            'dob': self.dob or '',
            'birth_year': self.birth_year or '',
            'parent_name': self.parent_name or '',
            'phone': self.phone or '',
            'address': self.address or '',
            'status': self.status or 'Đang học',
            'class_name': self.class_name or '',
            'last_class_name': self.last_class_name or '',
            'schedule': self.schedule or '',
            'room': self.room or '',
            'teacher': self.teacher or '',
            'cm': self.cm_staff or '',
            'ta': self.ta_staff or '',
            'grammar_class': self.grammar_class or '',
            'total_sessions': self.total_sessions or 0,
            'remaining_sessions': self.remaining_sessions or 0,
            'charged_absent_sessions': self.charged_absent_sessions or 0,
            'expiry_date': self.expiry_date or '',
            'expiry_month': self.expiry_month or '',
            'expiry_year': self.expiry_year or '',
            'renewal_status_2025': self.renewal_status_2025 or '',
            'fee_package_1': self.fee_package_1 or '',
            'fee_package_2': self.fee_package_2 or '',
            'fee_package_3': self.fee_package_3 or '',
            'fee_package_4': self.fee_package_4 or '',
        }


class ClassMaster(Base):
    """
    Bảng Lớp Học
    """
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100), unique=True, nullable=False, index=True)
    schedule = Column(String(100))
    room = Column(String(100))
    teacher = Column(String(100))
    cm_staff = Column(String(100))
    ta_staff = Column(String(100))
    start_date = Column(String(50), nullable=True)
    curriculum = Column(String(100), nullable=True)
    shift_code = Column(String(100), nullable=True)
    status = Column(String(50), default='Đang hoạt động', index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'class_name': self.class_name,
            'schedule': self.schedule or '',
            'room': self.room or '',
            'teacher': self.teacher or '',
            'cm_staff': self.cm_staff or '',
            'ta_staff': self.ta_staff or '',
            'start_date': self.start_date or '',
            'curriculum': self.curriculum or '',
            'shift_code': self.shift_code or '',
            'status': self.status or 'Đang hoạt động'
        }


class HomeworkRecord(Base):
    """
    Bảng Nhật ký Bài Về Nhà (BTVN)
    """
    __tablename__ = 'homework_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), ForeignKey('students.code'), nullable=True, index=True)
    student_name = Column(String(255), nullable=False, index=True)
    english_name = Column(String(100))
    class_name = Column(String(100), index=True)
    phone = Column(String(100))
    schedule = Column(String(100))
    submission_date = Column(String(50), index=True)
    status = Column(String(50), index=True)  # 'Đã nộp', 'Nộp muộn', 'Chưa nộp BTVN'
    score = Column(String(50))
    score_num = Column(Float, default=0.0)
    total_questions = Column(String(50))
    teacher_note = Column(Text)

    student = relationship("Student", back_populates="homework_records")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.student_code or '',
            'name': self.student_name,
            'english_name': self.english_name or '',
            'class_name': self.class_name or '',
            'phone': self.phone or '',
            'schedule': self.schedule or '',
            'date': self.submission_date or '',
            'status': self.status or 'Chưa nộp BTVN',
            'score': self.score or '',
            'score_num': self.score_num or 0.0,
            'total_questions': self.total_questions or '',
            'teacher_note': self.teacher_note or '',
        }


class UnitGrade(Base):
    """
    Bảng Bảng Điểm Thi các Unit & Mid-term
    """
    __tablename__ = 'unit_grades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), ForeignKey('students.code'), nullable=True, index=True)
    student_name = Column(String(255), nullable=False, index=True)
    english_name = Column(String(100))
    class_name = Column(String(100), index=True)
    course = Column(String(100))
    test_name = Column(String(100), index=True)
    listening = Column(Float, nullable=True)
    listening_max = Column(Float, default=10.0)
    reading_writing = Column(Float, nullable=True)
    reading_writing_max = Column(Float, default=12.0)
    speaking = Column(Float, nullable=True)
    speaking_max = Column(Float, default=10.0)
    total_score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    comment = Column(Text)

    student = relationship("Student", back_populates="unit_grades")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.student_code or '',
            'name': self.student_name,
            'english_name': self.english_name or '',
            'class_name': self.class_name or '',
            'course': self.course or '',
            'test_name': self.test_name or '',
            'listening': self.listening,
            'listening_max': self.listening_max,
            'reading_writing': self.reading_writing,
            'reading_writing_max': self.reading_writing_max,
            'speaking': self.speaking,
            'speaking_max': self.speaking_max,
            'total_score': self.total_score,
            'max_score': self.max_score,
            'comment': self.comment or '',
        }


class ParentInteractionLog(Base):
    """
    Bảng Nhật Ký Tương Tác Phụ Huynh & Check-in Hàng Ngày
    (Từ các tab 'Nhật ký tương tác lớp Thục Anh', '(Naomi) Daily Checking', '(Amber) Daily checking')
    """
    __tablename__ = 'parent_interaction_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), ForeignKey('students.code'), nullable=True, index=True)
    student_name = Column(String(255), index=True)
    english_name = Column(String(100))
    class_name = Column(String(100), index=True)
    staff_name = Column(String(100))
    month = Column(String(50))
    note = Column(Text)
    interaction_detail = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="parent_interactions")

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.student_code or '',
            'name': self.student_name,
            'english_name': self.english_name or '',
            'class_name': self.class_name or '',
            'staff_name': self.staff_name or '',
            'month': self.month or '',
            'note': self.note or '',
            'interaction_detail': self.interaction_detail or '',
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else ''
        }


class ClassFeedbackLog(Base):
    """
    Bảng Nhận Xét Học Tập Chi Tiết Theo Lớp (Từ 14 tabs 'NXHT...' trong Sheet 2)
    """
    __tablename__ = 'class_feedback_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100), nullable=False, index=True)
    student_name = Column(String(255), index=True)
    english_name = Column(String(100))
    lesson_name = Column(String(100))
    feedback_content = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'class_name': self.class_name,
            'name': self.student_name or '',
            'english_name': self.english_name or '',
            'lesson_name': self.lesson_name or '',
            'feedback_content': self.feedback_content or ''
        }


class StudentWithdrawal(Base):
    """
    Bảng Lịch Sử Học Sinh Bảo Lưu / Nghỉ Học (Từ tab 'Withdraw' Sheet 1)
    """
    __tablename__ = 'student_withdrawals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), index=True)
    student_name = Column(String(255), index=True)
    english_name = Column(String(100))
    status_type = Column(String(50))  # 'BL' (Bảo lưu) hoặc 'Nghỉ'
    reason = Column(Text)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.student_code or '',
            'name': self.student_name or '',
            'english_name': self.english_name or '',
            'status_type': self.status_type or '',
            'reason': self.reason or ''
        }


class StudentRenewal(Base):
    """
    Bảng Nhật Ký Quản Lý Tái Phí Học Sinh
    """
    __tablename__ = 'student_renewals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), index=True)
    student_name = Column(String(255), nullable=False, index=True)
    english_name = Column(String(100))
    class_name = Column(String(100), index=True)
    cm_staff = Column(String(100), index=True)
    month = Column(Integer, index=True)
    year = Column(Integer, index=True)
    status = Column(String(50), default='pending', index=True)  # 'success', 'stacked', 'pending', 'failed'
    expected_expiry_date = Column(String(50))                    # Ngày dự kiến hết phí
    fee_package = Column(String(100))
    amount = Column(Float, default=0.0)
    due_date = Column(String(50))
    notes = Column(Text)
    created_by = Column(String(100))
    completed_at = Column(DateTime)                             # Ngày giờ hoàn thành tái phí / chồng phí
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        status_code = self.status or 'pending'
        status_labels = {
            'success': '🟢 Thành công',
            'stacked': '🔵 Chồng phí',
            'pending': '🟡 Chờ xử lý',
            'failed': '🔴 Thất bại'
        }
        status_label = status_labels.get(status_code, '🟡 Chờ xử lý')
        return {
            'id': self.id,
            'student_code': self.student_code or '',
            'student_name': self.student_name or '',
            'english_name': self.english_name or '',
            'class_name': self.class_name or '',
            'cm_staff': self.cm_staff or '',
            'month': self.month or 0,
            'year': self.year or 2026,
            'status': status_code,
            'status_label': status_label,
            'expected_expiry_date': self.expected_expiry_date or '',
            'fee_package': self.fee_package or '',
            'amount': self.amount or 0.0,
            'due_date': self.due_date or '',
            'notes': self.notes or '',
            'created_by': self.created_by or '',
            'completed_at': self.completed_at.strftime('%d/%m/%Y %H:%M') if self.completed_at else '',
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else ''
        }


class AuditUnmatchedRecord(Base):
    """
    Bảng Nhật ký Bản ghi chưa khớp mã cố định để Rà Soát Thủ Công
    """
    __tablename__ = 'audit_unmatched_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_tab = Column(String(100), index=True)
    raw_student_name = Column(String(255))
    raw_english_name = Column(String(100))
    raw_class = Column(String(100))
    issue_description = Column(Text)
    status = Column(String(50), default='Pending Review')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'source_tab': self.source_tab,
            'raw_student_name': self.raw_student_name,
            'raw_english_name': self.raw_english_name or '',
            'raw_class': self.raw_class or '',
            'issue_description': self.issue_description or '',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class User(Base):
    """
    Bảng Tài Khoản Người Dùng & Phân Quyền Hệ Thống
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default='cm')  # 'admin', 'cm', 'teacher'
    cm_staff_name = Column(String(100), nullable=True)     # Ví dụ: 'Thục Anh', 'Amber', 'Naomi', 'Ms. Lan'
    is_active = Column(Integer, default=1)                  # 1: Active, 0: Disabled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email or '',
            'role': self.role,
            'cm_staff_name': self.cm_staff_name or '',
            'is_active': bool(self.is_active),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class AttendanceRecord(Base):
    """
    Bảng Nhật Ký Điểm Danh Hàng Ngày
    """
    __tablename__ = 'attendance_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100), nullable=False, index=True)
    attendance_date = Column(String(50), nullable=False, index=True)  # YYYY-MM-DD
    student_code = Column(String(20), index=True)
    student_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='Có mặt')     # 'Có mặt', 'Vắng có phép', 'Vắng không phép', 'Đi muộn', 'Lý do khác'
    note = Column(Text, nullable=True)
    is_guest = Column(Integer, default=0)                              # 1: Học sinh bổ sung/học ghép từ lớp khác, 0: Học sinh chính thức
    created_by = Column(String(100))                                   # Username của CM/Người điểm danh
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Các mục Bài Tập Về Nhà (BVN) hàng ngày
    hw_total_questions = Column(Integer, default=10)                  # Tổng số câu (mặc định 10)
    hw_correct_answers = Column(Integer, nullable=True)               # Số câu đúng (nhập tay)
    hw_score = Column(Float, nullable=True)                          # Điểm BVN (Thang 10: = (Số câu đúng / Tổng số câu) * 10)
    hw_submission_status = Column(String(100), default='Nộp đúng giờ') # 'Nộp đúng giờ', 'Nộp muộn', 'Không làm', 'Nghỉ học', 'Học buổi đầu', 'Không có BVN'
    hw_comment = Column(Text, nullable=True)                           # Nhận xét bài về nhà học viên

    def to_dict(self):
        return {
            'id': self.id,
            'class_name': self.class_name,
            'attendance_date': self.attendance_date,
            'student_code': self.student_code or '',
            'student_name': self.student_name,
            'status': self.status,
            'note': self.note or '',
            'is_guest': bool(self.is_guest),
            'created_by': self.created_by or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'hw_total_questions': self.hw_total_questions if self.hw_total_questions is not None else 10,
            'hw_correct_answers': self.hw_correct_answers,
            'hw_score': self.hw_score,
            'hw_submission_status': self.hw_submission_status or 'Nộp đúng giờ',
            'hw_comment': self.hw_comment or ''
        }


class ClassSchedule(Base):
    """
    Bảng Thời Khóa Biểu Lớp Học (Từ tab SCHEDULE)
    """
    __tablename__ = 'class_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    section = Column(String(50), default='Chính thức')  # 'Chính thức' hoặc 'Bổ trợ'
    day = Column(String(50), nullable=False, index=True) # 'Thứ 2 (MON)', 'Thứ 3 (TUE)', ...
    shift_code = Column(String(20), nullable=False)      # 'MT5', 'MT6', 'TF5', 'TF6', 'WS5', 'WS6'
    shift_name = Column(String(100), nullable=False)     # 'Block 5 (17:30 - 19:00)', ...
    class_name = Column(String(100), nullable=False, index=True)
    materials = Column(String(255), nullable=True)
    room = Column(String(100), nullable=True, index=True)
    teacher = Column(String(100), nullable=True, index=True)
    students_count = Column(Integer, default=0)
    cm_staff = Column(String(100), nullable=True, index=True)
    ta_staff = Column(String(100), nullable=True)
    tutoring_info = Column(Text, nullable=True)
    lesson_plan_url = Column(String(500), nullable=True) # Link giáo án Drive
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        default_drive = "https://drive.google.com/drive/folders/1JBDNHJLPorVjqbEHfHJgObhP9wsEejTz?usp=sharing"
        return {
            'id': self.id,
            'section': self.section,
            'day': self.day,
            'shift_code': self.shift_code,
            'shift_name': self.shift_name,
            'class_name': self.class_name,
            'materials': self.materials or '',
            'room': self.room or '',
            'teacher': self.teacher or '',
            'students_count': self.students_count or 0,
            'cm_staff': self.cm_staff or '',
            'ta_staff': self.ta_staff or '',
            'tutoring_info': self.tutoring_info or '',
            'lesson_plan_url': self.lesson_plan_url or default_drive
        }


class LessonSyllabus(Base):
    """
    Bảng Lưu Trữ Chương Trình / Giáo Án Chi Tiết Các Giáo Trình (Moon 1..6, Sun 1..5, Galaxy...)
    """
    __tablename__ = 'lesson_syllabuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(100), nullable=False, index=True) # E.g. 'Sun 1', 'Moon 3', 'Sun 2'...
    class_name = Column(String(100), nullable=True, index=True)  # E.g. 'Moon 5.2', 'Galax 1.4'
    official_date = Column(String(50), nullable=True)             # E.g. '06/08/2026' or '2026-08-06'
    lesson_num = Column(Integer, default=1, index=True)           # 1, 2, 3...
    lesson_title = Column(String(100))                            # 'LESSON 1', 'LESSON 2'...
    unit_name = Column(String(200))                               # 'UNIT 1 HELLO!'
    pages = Column(String(100))                                   # '4-5'
    vocabulary = Column(Text)                                     # Từ vựng / Nội dung chính
    grammar = Column(Text)                                        # Cấu trúc / Ngữ pháp
    lesson_target = Column(Text)                                  # Mục tiêu bài học
    homework_teacher = Column(Text)                               # BTVN trên sách / GV giao
    homework_cm = Column(Text)                                    # BTVN E-learning / CM giao
    file_source = Column(String(100))                             # 'Sun 1.xlsx'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'course_name': self.course_name,
            'class_name': self.class_name or '',
            'official_date': self.official_date or '',
            'lesson_num': self.lesson_num,
            'lesson_title': self.lesson_title or '',
            'unit_name': self.unit_name or '',
            'pages': self.pages or '',
            'vocabulary': self.vocabulary or '',
            'grammar': self.grammar or '',
            'lesson_target': self.lesson_target or '',
            'homework_teacher': self.homework_teacher or '',
            'homework_cm': self.homework_cm or '',
            'file_source': self.file_source or ''
        }



class StudentHistorySnapshot(Base):
    """
    Bảng Lịch Sử Thông Tin Học Sinh Theo Tháng (Từ Sheet 4 > tab 'Data')
    Lưu snapshot HS qua từng tháng từ 2023 đến nay để theo dõi lịch sử chuyển lớp, đổi GV, đổi CM.
    """
    __tablename__ = 'student_history_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), index=True)
    student_name = Column(String(255))
    english_name = Column(String(100))
    dob = Column(String(50))
    class_name = Column(String(100), index=True)
    teacher = Column(String(100))
    cm_staff = Column(String(100))
    snapshot_month = Column(Integer, index=True)        # Tháng (1-12)
    snapshot_year = Column(Integer, index=True)          # Năm (2023, 2024, 2025, 2026)
    source_sheet = Column(String(100))                   # Nguồn dữ liệu (Sheet 4 Data, Sheet 2 Data DSHS...)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'code': self.student_code or '', 'name': self.student_name or '',
            'english_name': self.english_name or '', 'dob': self.dob or '',
            'class_name': self.class_name or '', 'teacher': self.teacher or '',
            'cm_staff': self.cm_staff or '',
            'snapshot_month': self.snapshot_month, 'snapshot_year': self.snapshot_year,
            'source_sheet': self.source_sheet or ''
        }


class RenewalDetailLog(Base):
    """
    Bảng Nhật Ký Chi Tiết Tái Phí Từng Học Sinh (Từ Sheet 1 > 3 tabs Tái phí)
    Ghi lại lịch sử tái phí qua các đợt (tái phí 2025, tái phí đến 6/2026, tái phí mới nhất 6/5/2026).
    """
    __tablename__ = 'renewal_detail_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), index=True)
    student_name = Column(String(255))
    english_name = Column(String(100))
    class_name = Column(String(100), index=True)
    schedule = Column(String(100))
    teacher = Column(String(100))
    cm_staff = Column(String(100))
    ta_staff = Column(String(100))
    total_sessions = Column(Integer, default=0)
    remaining_sessions = Column(Integer, default=0)
    expiry_date = Column(String(100))
    expiry_month = Column(String(50))
    expiry_year = Column(String(50))
    renewal_status = Column(String(200))                 # Tình trạng tái phí
    renewal_time = Column(String(200))                   # Thời gian tái phí
    interaction_note = Column(Text)                      # Ghi chú tương tác
    source_tab = Column(String(100), index=True)         # 'Tái phí', 'Tái phí (từ 6/5/2026)', 'Tái phí đến 6/2026'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'code': self.student_code or '', 'name': self.student_name or '',
            'english_name': self.english_name or '', 'class_name': self.class_name or '',
            'schedule': self.schedule or '', 'teacher': self.teacher or '', 'cm_staff': self.cm_staff or '',
            'total_sessions': self.total_sessions or 0, 'remaining_sessions': self.remaining_sessions or 0,
            'expiry_date': self.expiry_date or '', 'expiry_month': self.expiry_month or '',
            'expiry_year': self.expiry_year or '', 'renewal_status': self.renewal_status or '',
            'renewal_time': self.renewal_time or '', 'interaction_note': self.interaction_note or '',
            'source_tab': self.source_tab or ''
        }


class MonthlyAttendanceRecord(Base):
    """
    Bảng Điểm Danh Hàng Ngày (Unpivot từ Sheet 1 > tab 'Điểm danh', 97 cột ngày)
    Mỗi bản ghi = 1 HS x 1 ngày.
    """
    __tablename__ = 'monthly_attendance_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(20), index=True)
    student_name = Column(String(255))
    english_name = Column(String(100))
    class_name = Column(String(100), index=True)
    schedule = Column(String(50))
    teacher = Column(String(100))
    cm_staff = Column(String(100))
    attendance_date = Column(String(50), index=True)     # YYYY-MM-DD hoặc nguyên gốc
    attendance_value = Column(String(50))                 # 'x' (có mặt), 'K' (vắng KP), 'P' (vắng CP), 'BL' (bảo lưu)...
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'code': self.student_code or '', 'name': self.student_name or '',
            'english_name': self.english_name or '', 'class_name': self.class_name or '',
            'schedule': self.schedule or '', 'teacher': self.teacher or '', 'cm_staff': self.cm_staff or '',
            'attendance_date': self.attendance_date or '', 'attendance_value': self.attendance_value or ''
        }


class GrammarClubEnrollment(Base):
    """
    Bảng Đăng Ký Lớp Ngữ Pháp & CLB Speaking (Từ Sheet 1 > tab 'DS lớp ngữ pháp + CLB')
    """
    __tablename__ = 'grammar_club_enrollments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_name = Column(String(255), index=True)
    english_name = Column(String(100))
    dob = Column(String(50))
    parent_name = Column(String(255))
    phone = Column(String(100))
    main_class = Column(String(100))                     # Lớp chính (vc column)
    school_grade = Column(String(50))                    # Lớp trường (Lớp 3, Lớp 4...)
    grammar_class = Column(String(100))                  # Ca ngữ pháp (Ca 1 - L34...)
    speaking_club = Column(String(100))                  # Ca CLB Speaking
    note_grammar = Column(Text)                          # Ghi chú ngữ pháp
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.student_name or '', 'english_name': self.english_name or '',
            'dob': self.dob or '', 'parent_name': self.parent_name or '', 'phone': self.phone or '',
            'main_class': self.main_class or '', 'school_grade': self.school_grade or '',
            'grammar_class': self.grammar_class or '', 'speaking_club': self.speaking_club or '',
            'note_grammar': self.note_grammar or ''
        }


class TestScheduleEntry(Base):
    """
    Bảng Lịch Kiểm Tra Các Lớp (Từ Sheet 4 > tab 'Nhập lịch kiểm tra')
    """
    __tablename__ = 'test_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_date = Column(String(50), index=True)
    class_code = Column(String(100), index=True)
    teacher = Column(String(100))
    student_count = Column(Integer, default=0)
    test_content = Column(Text)
    existing_tests_count = Column(Integer, default=0)
    justification = Column(Text)
    week = Column(String(20))
    month = Column(String(20))
    year = Column(String(20), index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'test_date': self.test_date or '', 'class_code': self.class_code or '',
            'teacher': self.teacher or '', 'student_count': self.student_count or 0,
            'test_content': self.test_content or '', 'justification': self.justification or '',
            'week': self.week or '', 'month': self.month or '', 'year': self.year or ''
        }


class LevelCompletion(Base):
    """
    Bảng Lịch Hết Trình Độ & Họp Phụ Huynh (Từ Sheet 4 > tab 'Lịch hết trình độ và họp PH')
    """
    __tablename__ = 'level_completions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100), index=True)
    current_level = Column(String(100))
    completion_date = Column(String(100))
    next_level = Column(String(100))
    meeting_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'class_name': self.class_name or '',
            'current_level': self.current_level or '', 'completion_date': self.completion_date or '',
            'next_level': self.next_level or '', 'meeting_notes': self.meeting_notes or ''
        }


class KpiMonthlyReport(Base):
    """
    Bảng KPI Báo Cáo Hàng Tháng (Từ Sheet 1 > tabs 'Báo cáo', 'Dashboard')
    """
    __tablename__ = 'kpi_monthly_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_type = Column(String(100), index=True)         # 'renewal_rate', 'attendance_avg', 'btvn_avg', 'completion'
    cm_staff = Column(String(100), index=True)
    month = Column(Integer, index=True)
    year = Column(Integer, index=True)
    due_count = Column(Integer, default=0)                # Số HS đến hạn
    success_count = Column(Integer, default=0)            # Số HS thành công
    pending_count = Column(Integer, default=0)            # Số HS chưa tái phí
    failed_count = Column(Integer, default=0)             # Số HS thất bại
    rate_percent = Column(Float, default=0.0)             # Tỉ lệ %
    raw_value = Column(String(200))                       # Giá trị gốc
    source_tab = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'report_type': self.report_type or '', 'cm_staff': self.cm_staff or '',
            'month': self.month, 'year': self.year, 'due_count': self.due_count or 0,
            'success_count': self.success_count or 0, 'pending_count': self.pending_count or 0,
            'failed_count': self.failed_count or 0, 'rate_percent': self.rate_percent or 0.0,
            'raw_value': self.raw_value or '', 'source_tab': self.source_tab or ''
        }


class ClassScheduleAdjustment(Base):
    """
    Bảng Lưu Cấu Hình Ngày Học Chính Thức & Điều Chỉnh Lùi Lịch Cho Từng Lớp
    """
    __tablename__ = 'class_schedule_adjustments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(100), nullable=False, unique=True, index=True) # E.g. 'Galax 1.4', 'Sun 2.4'...
    start_date = Column(String(50), nullable=True)                            # YYYY-MM-DD (e.g. '2026-07-21')
    delayed_lessons = Column(Text, nullable=True, default='[]')                # JSON list of lesson numbers delayed e.g. [5, 12]
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        import json
        try:
            del_list = json.loads(self.delayed_lessons or '[]')
        except:
            del_list = []
        return {
            'id': self.id,
            'class_name': self.class_name,
            'start_date': self.start_date or '',
            'delayed_lessons': del_list,
            'note': self.note or ''
        }


class HolidayHistoryLog(Base):
    """
    Bảng Lưu Trữ Lịch Sử Các Đợt Nghỉ Lễ, Nghỉ Đột Xuất & Lùi Lịch
    """
    __tablename__ = 'holiday_history_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)                         # Tên dịp / Lý do (e.g. 'Nghỉ lễ Quốc Khánh 2/9')
    holiday_type = Column(String(100), default='Nghỉ lễ cố định')       # 'Nghỉ lễ cố định', 'Nghỉ đột xuất', 'Lùi lịch riêng'
    start_date = Column(String(50), nullable=False, index=True)         # YYYY-MM-DD
    end_date = Column(String(50), nullable=False, index=True)           # YYYY-MM-DD
    affected_classes = Column(Text, default='["ALL"]')                  # JSON list: ["ALL"] hoặc ["Galax 1.3", "Moon 5.2"]
    affected_students_count = Column(Integer, default=0)                # Số học sinh được tự động gia hạn hạn học
    affected_lessons_count = Column(Integer, default=0)                 # Số ca học trùng ngày nghỉ bị dời
    created_by = Column(String(100), nullable=True)                     # Username / Người tạo
    status = Column(String(50), default='Active', index=True)           # 'Active' hoặc 'Cancelled'
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        import json
        try:
            classes = json.loads(self.affected_classes or '["ALL"]')
        except:
            classes = ["ALL"]
        return {
            'id': self.id,
            'title': self.title,
            'holiday_type': self.holiday_type or 'Nghỉ lễ cố định',
            'start_date': self.start_date,
            'end_date': self.end_date,
            'affected_classes': classes,
            'affected_students_count': self.affected_students_count or 0,
            'affected_lessons_count': self.affected_lessons_count or 0,
            'created_by': self.created_by or '',
            'status': self.status or 'Active',
            'note': self.note or '',
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else ''
        }


class StudentSubscription(Base):
    """
    Bảng Quản lý thời hạn và gói học của Học Sinh (CRM Subscription).
    Theo dõi ngày hết phí gốc (original_end_date) và ngày hết phí thực tế (current_end_date) sau khi chồng phí.
    """
    __tablename__ = 'student_subscriptions'

    id = Column(Integer, primary_key=True)
    subscription_id = Column(String(50), unique=True, index=True)
    student_code = Column(String(20), index=True)
    student_name = Column(String(255))
    english_name = Column(String(100))
    class_name = Column(String(100), index=True)
    cm_staff = Column(String(100), index=True)
    start_date = Column(String(50))
    original_end_date = Column(String(50))
    current_end_date = Column(String(50), index=True)
    remaining_sessions = Column(Integer, default=0)
    renewal_status = Column(String(50), default='Upcoming')  # Upcoming, Renewed, Early_Renewed, Late_Renewed, Failed, Churned
    pipeline_stage = Column(String(50), default='D-30')      # D-30, Contacted, Committed, At-Risk, Success, Failed
    is_cm_locked = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id or f"SUB-{self.student_code}",
            'student_code': self.student_code or '',
            'student_name': self.student_name or '',
            'english_name': self.english_name or '',
            'class_name': self.class_name or '',
            'cm_staff': self.cm_staff or '',
            'start_date': self.start_date or '',
            'original_end_date': self.original_end_date or '',
            'current_end_date': self.current_end_date or '',
            'remaining_sessions': self.remaining_sessions or 0,
            'renewal_status': self.renewal_status or 'Upcoming',
            'pipeline_stage': self.pipeline_stage or 'D-30',
            'is_cm_locked': self.is_cm_locked or 0,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%d/%m/%Y %H:%M') if self.updated_at else ''
        }


class RenewalTransaction(Base):
    """
    Bảng Ghi nhận Giao Dịch Thu Tiền Tái Phí / Chồng Phí (CRM Renewal Transaction).
    Lưu vết từng lần đóng phí để tính Doanh số & KPI tái phí.
    """
    __tablename__ = 'renewal_transactions'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(50), unique=True, index=True)
    student_code = Column(String(20), index=True)
    student_name = Column(String(255))
    payment_date = Column(String(50))
    amount = Column(Float, default=0.0)
    package_sessions = Column(Integer, default=0)
    fee_package = Column(String(100))
    is_early_renewal = Column(Integer, default=0)            # 1: Chồng phí sớm, 0: Đúng hạn
    attributed_month = Column(String(20))                    # YYYY-MM
    attributed_year = Column(Integer)
    attributed_month_num = Column(Integer)
    created_by = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id or f"TX-{self.id}",
            'student_code': self.student_code or '',
            'student_name': self.student_name or '',
            'payment_date': self.payment_date or '',
            'amount': self.amount or 0.0,
            'package_sessions': self.package_sessions or 0,
            'fee_package': self.fee_package or '',
            'is_early_renewal': self.is_early_renewal or 0,
            'attributed_month': self.attributed_month or '',
            'attributed_year': self.attributed_year or 0,
            'attributed_month_num': self.attributed_month_num or 0,
            'created_by': self.created_by or '',
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else ''
        }


class ActivityLog(Base):
    """
    Bảng Nhật Ký Hoạt Động & Audit Log Người Dùng (Admin Activity & Audit Trail)
    Lưu vết 100% các thao tác Thêm, Sửa, Xóa, Điểm Danh, Nhập Điểm, Tái Phí... của các User.
    """
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, index=True)         # Tên đăng nhập ('cm_thucanh', 'admin'...)
    user_fullname = Column(String(255), nullable=True)                 # Họ tên hiển thị ('Phạm Thị Thục Anh'...)
    user_role = Column(String(50), nullable=True, default='cm')         # Quyền ('admin', 'cm', 'teacher')
    action_type = Column(String(50), nullable=False, index=True)       # 'CREATE', 'UPDATE', 'DELETE', 'ATTENDANCE', 'GRADE', 'INTERACTION', 'RENEWAL_STAGE', 'RENEWAL_PAYMENT', 'HOLIDAY_SHIFT', 'CLASS_EDIT', 'USER_MANAGEMENT'
    target_module = Column(String(50), nullable=False, index=True)     # 'STUDENT', 'CLASS', 'ATTENDANCE', 'GRADE', 'INTERACTION', 'RENEWAL', 'HOLIDAY', 'USER'
    target_id = Column(String(100), nullable=True)                     # Mã HS (EVI056), Tên lớp, ID bản ghi...
    description = Column(Text, nullable=False)                         # Mô tả tiếng Việt chi tiết nội dung thao tác
    ip_address = Column(String(50), nullable=True)                     # IP truy cập
    is_read_by_admin = Column(Integer, default=0, index=True)          # 0: Chưa đọc, 1: Đã đọc
    created_at = Column(DateTime, default=datetime.datetime.now, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username or 'system',
            'user_fullname': self.user_fullname or self.username or 'Hệ thống',
            'user_role': self.user_role or 'cm',
            'action_type': self.action_type or 'UPDATE',
            'target_module': self.target_module or 'SYSTEM',
            'target_id': self.target_id or '',
            'description': self.description or '',
            'ip_address': self.ip_address or '',
            'is_read_by_admin': bool(self.is_read_by_admin),
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M:%S') if self.created_at else '',
            'time_ago': self.get_time_ago()
        }

    def get_time_ago(self):
        if not self.created_at:
            return ''
        now = datetime.datetime.now()
        diff = now - self.created_at
        seconds = diff.total_seconds()
        if seconds < 60:
            return 'Vừa xong'
        elif seconds < 3600:
            return f"{int(seconds // 60)} phút trước"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} giờ trước"
        elif seconds < 604800:
            return f"{int(seconds // 86400)} ngày trước"
        else:
            return self.created_at.strftime('%d/%m/%Y')




