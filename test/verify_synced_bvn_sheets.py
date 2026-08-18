import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_attendance_db

def verify_bvn():
    print("=== VERIFY GALAX 1.3 (06/08/2026) ===")
    res1 = get_attendance_db('Galax 1.3', '2026-08-06')
    for r in res1.get('data', []):
        c_name = r['student_name'].encode('ascii', 'ignore').decode('ascii')
        c_comm = r.get('hw_comment', '').encode('ascii', 'ignore').decode('ascii')
        c_stat = r.get('hw_submission_status', '').encode('ascii', 'ignore').decode('ascii')
        print(f"  {r['student_code']:7s} | {c_name:20s} | Score: {r.get('hw_score')} ({r.get('hw_correct_answers')}/{r.get('hw_total_questions')}) | Status: {c_stat} | Comment: {c_comm}")

    print("\n=== VERIFY SUN 2.4 (06/08/2026) ===")
    res2 = get_attendance_db('Sun 2.4', '2026-08-06')
    for r in res2.get('data', []):
        c_name = r['student_name'].encode('ascii', 'ignore').decode('ascii')
        c_comm = r.get('hw_comment', '').encode('ascii', 'ignore').decode('ascii')
        c_stat = r.get('hw_submission_status', '').encode('ascii', 'ignore').decode('ascii')
        print(f"  {r['student_code']:7s} | {c_name:20s} | Score: {r.get('hw_score')} ({r.get('hw_correct_answers')}/{r.get('hw_total_questions')}) | Status: {c_stat} | Comment: {c_comm}")

if __name__ == '__main__':
    verify_bvn()
