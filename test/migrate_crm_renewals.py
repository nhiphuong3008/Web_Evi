import os
import sys
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session, engine
from database.models import Base, Student, StudentRenewal, RenewalDetailLog, StudentSubscription, RenewalTransaction

def run_migration():
    print("🚀 Starting Migration for CRM Subscription & Renewal Transactions Tables...")
    
    # 1. Create tables if not exist
    Base.metadata.create_all(bind=engine)
    print("✅ Created/Verified tables: student_subscriptions, renewal_transactions")

    session = db_session()
    
    # Clear existing CRM tables for clean re-seed
    session.query(StudentSubscription).delete()
    session.query(RenewalTransaction).delete()
    session.commit()

    # Fetch all students from CSDL
    students = session.query(Student).all()
    print(f"Total students in DB: {len(students)}")

    # Fetch all detail logs from Google Sheets imports
    logs = session.query(RenewalDetailLog).all()
    # Map logs by student_code
    logs_by_code = {}
    for l in logs:
        code = (l.student_code or '').strip()
        if code:
            if code not in logs_by_code:
                logs_by_code[code] = []
            logs_by_code[code].append(l)

    subs_count = 0
    tx_count = 0

    # Seed from StudentRenewal records (the 2026 due list)
    ren_records = session.query(StudentRenewal).all()
    print(f"Total StudentRenewal records: {len(ren_records)}")

    for r in ren_records:
        code = r.student_code
        st_logs = logs_by_code.get(code, [])
        has_stacked_log = (r.status == 'stacked') or any((l.renewal_status and 'Chồng' in l.renewal_status) for l in st_logs)

        orig_expiry = r.expected_expiry_date or '29/08/2026'
        cur_expiry = orig_expiry

        parts = orig_expiry.split('/')
        exp_month = r.month or (int(parts[1]) if len(parts) == 3 else 8)
        exp_year = r.year or (int(parts[2]) if len(parts) == 3 else 2026)

        ren_status = 'Upcoming'
        stage = 'D-30'

        if r.status == 'failed':
            ren_status = 'Failed'
            stage = 'Failed'
        elif r.status == 'pending':
            ren_status = 'Upcoming'
            stage = 'D-30'
        elif r.status == 'success':
            ren_status = 'Renewed'
            stage = 'Success'
        elif r.status == 'stacked' or has_stacked_log:
            ren_status = 'Early_Renewed'
            stage = 'Success'
            if len(parts) == 3:
                cur_expiry = f"{parts[0]}/{parts[1]}/{exp_year + 1}"
            else:
                cur_expiry = f"15/05/2027"

            # Add transaction
            tx = RenewalTransaction(
                transaction_id=f"TX-{code}-202605",
                student_code=code,
                student_name=r.student_name,
                payment_date='2026-05-15 10:00',
                amount=7200000.0,
                package_sessions=72,
                fee_package='Gói 72 buổi',
                is_early_renewal=1,
                attributed_month='2026-05',
                attributed_year=2026,
                attributed_month_num=5,
                created_by='Hệ Thống CRM',
                notes='Ghi nhận chồng phí từ đợt Tháng 5/2026'
            )
            session.add(tx)
            tx_count += 1

        # Lookup Master Student table by student code (code is unique)
        st_obj = session.query(Student).filter(Student.code == code).first()
        st_name = st_obj.full_name if (st_obj and st_obj.full_name) else r.student_name
        st_en = st_obj.english_name if (st_obj and st_obj.english_name) else (r.english_name or '')
        st_cls = st_obj.class_name if (st_obj and st_obj.class_name) else (r.class_name or '')
        st_cm = st_obj.cm_staff if (st_obj and st_obj.cm_staff) else (r.cm_staff or '')

        sub = StudentSubscription(
            subscription_id=f"SUB-{code}-{exp_month}-{exp_year}",
            student_code=code,
            student_name=st_name,
            english_name=st_en,
            class_name=st_cls,
            cm_staff=st_cm,
            start_date='01/01/2026',
            original_end_date=orig_expiry,
            current_end_date=cur_expiry,
            remaining_sessions=0,
            renewal_status=ren_status,
            pipeline_stage=stage,
            is_cm_locked=1 if (exp_month == 8 and exp_year == 2026) else 0,
            notes=r.notes or ''
        )
        session.add(sub)
        subs_count += 1

    session.commit()
    print(f"✅ Migration Completed! Inserted {subs_count} Subscriptions and {tx_count} Transactions.")

    # Audit Month 8/2026 Due List (Students whose current_end_date has month=8 and year=2026)
    month_8_subs = session.query(StudentSubscription).all()
    due_month_8 = [s for s in month_8_subs if len(s.current_end_date.split('/')) == 3 and int(s.current_end_date.split('/')[1]) == 8 and int(s.current_end_date.split('/')[2]) == 2026]
    print(f"\n📊 AUDIT: Total active due subscriptions for Month 8/2026 = {len(due_month_8)}")
    for d in due_month_8:
        print(f"  • #{d.id} | {d.student_code} | {d.student_name} | Class: {d.class_name} | Expiry: {d.current_end_date} | Stage: {d.pipeline_stage}")

    session.close()

if __name__ == '__main__':
    run_migration()
