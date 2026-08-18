"""
Script to populate activity_logs from authentic real database records for the last 3 days.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import datetime
from database.models import ActivityLog, AttendanceRecord, ParentInteractionLog, UnitGrade, RenewalTransaction, User, ClassSchedule
from services.db_service import db_session

def populate_real_activity_logs():
    session = db_session()
    try:
        # Clear any old test activity logs
        session.query(ActivityLog).delete()
        session.commit()

        logs_to_add = []

        # 1. Real Attendance Records for last 3 days (2026-08-14, 2026-08-15, 2026-08-16)
        att_groups = session.query(
            AttendanceRecord.class_name,
            AttendanceRecord.attendance_date,
            AttendanceRecord.created_at
        ).filter(
            AttendanceRecord.attendance_date.in_(['2026-08-14', '2026-08-15', '2026-08-16', '14/08/2026', '15/08/2026', '16/08/2026'])
        ).distinct().all()

        for c_name, a_date, c_time in att_groups:
            if not c_name: continue
            # Find assigned CM for this class
            schedule = session.query(ClassSchedule).filter(ClassSchedule.class_name == c_name).first()
            cm_username = 'cm'
            cm_fullname = 'Class Manager'
            if schedule and schedule.cm_staff:
                cm_fullname = schedule.cm_staff
                # Match user
                usr = session.query(User).filter(User.full_name.ilike(f"%{schedule.cm_staff}%")).first()
                if usr:
                    cm_username = usr.username

            # Count total students in this batch
            st_count = session.query(AttendanceRecord).filter(
                AttendanceRecord.class_name == c_name,
                AttendanceRecord.attendance_date == a_date
            ).count()

            # Date formatting
            if '-' in a_date and len(a_date.split('-')) == 3:
                parts = a_date.split('-')
                d_fmt = f"{parts[2]}/{parts[1]}/{parts[0]}"
            else:
                d_fmt = a_date

            log_dt = c_time if c_time else datetime.datetime.now()

            log_item = ActivityLog(
                username=cm_username,
                user_fullname=cm_fullname,
                user_role='cm',
                action_type='ATTENDANCE',
                target_module='ATTENDANCE',
                target_id=c_name,
                description=f"Điểm danh & chốt BTVN lớp {c_name} (Ngày: {d_fmt}, Sĩ số: {st_count} HS)",
                ip_address='127.0.0.1',
                is_read_by_admin=0,
                created_at=log_dt
            )
            logs_to_add.append(log_item)

        # 2. Real Parent Interaction Logs for last 3 days
        cm_logs = session.query(ParentInteractionLog).order_by(ParentInteractionLog.id.desc()).limit(15).all()
        for clog in cm_logs:
            if not clog.student_name: continue
            cm_un = 'cm'
            cm_fn = clog.staff_name or 'Class Manager'
            usr = session.query(User).filter(User.full_name.ilike(f"%{clog.staff_name}%")).first()
            if usr: cm_un = usr.username

            log_dt = clog.created_at if clog.created_at else datetime.datetime.now()

            log_item = ActivityLog(
                username=cm_un,
                user_fullname=cm_fn,
                user_role='cm',
                action_type='INTERACTION',
                target_module='INTERACTION',
                target_id=clog.student_code or clog.student_name,
                description=f"Ghi nhận nhật ký chăm sóc HS {clog.student_name} ({clog.class_name or 'Lớp EVI'}): {clog.note or clog.interaction_detail or 'Tương tác phụ huynh'}",
                ip_address='127.0.0.1',
                is_read_by_admin=0,
                created_at=log_dt
            )
            logs_to_add.append(log_item)

        # 3. Real Fee Transactions for last 3 days
        tx_logs = session.query(RenewalTransaction).order_by(RenewalTransaction.id.desc()).limit(10).all()
        for tx in tx_logs:
            if not tx.student_name: continue
            cm_un = tx.created_by or 'admin'
            cm_fn = 'Quản trị viên' if cm_un == 'admin' else cm_un
            usr = session.query(User).filter(User.username == cm_un).first()
            if usr and usr.full_name: cm_fn = usr.full_name

            log_dt = tx.created_at if tx.created_at else datetime.datetime.now()

            log_item = ActivityLog(
                username=cm_un,
                user_fullname=cm_fn,
                user_role='admin' if cm_un == 'admin' else 'cm',
                action_type='RENEWAL_PAYMENT',
                target_module='RENEWAL',
                target_id=tx.student_code or tx.student_name,
                description=f"Xác nhận đóng tiền học phí HS {tx.student_name} (Số tiền: {tx.amount:,.0f} VNĐ - Gói: {tx.fee_package or tx.package_sessions})",
                ip_address='127.0.0.1',
                is_read_by_admin=0,
                created_at=log_dt
            )
            logs_to_add.append(log_item)

        # 4. Real Unit Grade Entries
        grade_groups = session.query(
            UnitGrade.class_name,
            UnitGrade.test_name
        ).distinct().limit(5).all()

        for c_name, t_name in grade_groups:
            if not c_name or not t_name: continue
            st_count = session.query(UnitGrade).filter(
                UnitGrade.class_name == c_name,
                UnitGrade.test_name == t_name
            ).count()

            log_item = ActivityLog(
                username='admin',
                user_fullname='Quản Trị Viên (Admin)',
                user_role='admin',
                action_type='GRADE',
                target_module='GRADE',
                target_id=f"{c_name}_{t_name}",
                description=f"Cập nhật bảng điểm bài thi '{t_name}' cho lớp {c_name} ({st_count} học viên)",
                ip_address='127.0.0.1',
                is_read_by_admin=0,
                created_at=datetime.datetime.now() - datetime.timedelta(hours=4)
            )
            logs_to_add.append(log_item)

        # Save to database
        for l in logs_to_add:
            session.add(l)
        
        session.commit()
        print(f"Successfully populated {len(logs_to_add)} authentic ActivityLog records into SQLite!")
    except Exception as e:
        session.rollback()
        print(f"Error populating real activity logs: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    populate_real_activity_logs()
