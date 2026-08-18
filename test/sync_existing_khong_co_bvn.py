"""
Script to fix existing status in homework_records where attendance_records has 'Không có BVN'
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from database.models import AttendanceRecord, HomeworkRecord
from services.db_service import db_session

def fix_khong_co_bvn():
    session = db_session()
    try:
        att_records = session.query(AttendanceRecord).filter(
            AttendanceRecord.hw_submission_status.in_(['Không có BVN', 'Không có BTVN', 'Không bài', 'Không có'])
        ).all()
        print(f"Found {len(att_records)} attendance records with 'Không có BVN'")
        
        updated = 0
        for att in att_records:
            date_clean = att.attendance_date or ''
            if '-' in date_clean and len(date_clean.split('-')) == 3:
                parts = date_clean.split('-')
                date_clean = f"{parts[2]}/{parts[1]}/{parts[0]}"
            
            hw = session.query(HomeworkRecord).filter(
                HomeworkRecord.student_name == att.student_name,
                HomeworkRecord.class_name == att.class_name,
                HomeworkRecord.submission_date == date_clean
            ).first()
            
            if hw:
                hw.status = 'Không có BTVN'
                updated += 1
        
        session.commit()
        print(f"Successfully updated {updated} records to 'Không có BTVN'")
    finally:
        session.close()

if __name__ == '__main__':
    fix_khong_co_bvn()
