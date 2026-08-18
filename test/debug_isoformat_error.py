import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import db_session
from database.models import StudentSubscription, Student, RenewalTransaction

session = db_session()
cur_month = 11
cur_year = 2026

all_subs = session.query(StudentSubscription).all()
students_master = {st.code: st for st in session.query(Student).all() if st.code}

due_subs = []
for s in all_subs:
    s_dict = s.to_dict()
    st_master = students_master.get(s.student_code)
    if st_master:
        if st_master.class_name:
            s_dict['class_name'] = st_master.class_name
        if st_master.cm_staff:
            s_dict['cm_staff'] = st_master.cm_staff
        if st_master.full_name:
            s_dict['student_name'] = st_master.full_name
        if st_master.english_name:
            s_dict['english_name'] = st_master.english_name
        s_dict['student_status'] = st_master.status or 'Đang học'
        if st_master.expiry_date:
            s_dict['current_end_date'] = st_master.expiry_date
            s_dict['original_end_date'] = st_master.expiry_date

    cls = (s_dict.get('class_name') or '').strip()
    st_status = s_dict.get('student_status', 'Đang học')

    if cls in ['Bảo lưu', 'Đã nghỉ', 'Nghỉ học', '—', ''] or st_status in ['Đã nghỉ', 'Nghỉ học', 'Bảo lưu'] or s.renewal_status in ['Churned', 'Frozen']:
        continue

    parts = (s.current_end_date or s.original_end_date or '').split('/')
    if len(parts) == 3:
        m_val = int(parts[1])
        y_val = int(parts[2])
        if m_val == cur_month and y_val == cur_year:
            due_subs.append(s_dict)

kanban = {'d30': [], 'contacted': [], 'committed': [], 'at_risk': [], 'completed': []}
for r in due_subs:
    stg = r.get('pipeline_stage', 'D-30')
    rn_st = r.get('renewal_status', 'Upcoming')
    if rn_st in ['Failed', 'Churned']:
        r['pipeline_stage'] = 'Failed'
        kanban['completed'].append(r)
    elif rn_st in ['Renewed', 'Early_Renewed']:
        r['pipeline_stage'] = 'Success'
        kanban['completed'].append(r)
    elif stg in ['D-30', 'Upcoming']:
        kanban['d30'].append(r)
    elif stg in ['Contacted', 'Reminded']:
        kanban['contacted'].append(r)
    elif stg in ['Committed']:
        kanban['committed'].append(r)
    elif stg in ['At-Risk', 'Danger']:
        kanban['at_risk'].append(r)
    else:
        kanban['completed'].append(r)

attr_month_str = f"{cur_year}-{cur_month:02d}"
print("Executing RenewalTransaction query...")
tx_query = session.query(RenewalTransaction).filter(RenewalTransaction.attributed_month == attr_month_str).all()
print("RenewalTransaction query complete, tx_query count:", len(tx_query))
session.close()
