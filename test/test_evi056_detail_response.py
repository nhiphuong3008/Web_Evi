import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_student_detail_db

def test_evi056():
    res = get_student_detail_db('EVI056')
    print("Success:", res['success'])
    print("Grades count:", len(res.get('grades', [])))
    print("Homework count:", len(res.get('homework', [])))
    print("CM Notes count:", len(res.get('cm_notes', [])))

    print("\nSample Grades:")
    for g in res.get('grades', [])[:5]:
        print(f"  - [{g.get('class_name')}] {g.get('test_name')}: L={g.get('listening')}, RW={g.get('reading_writing')}, S={g.get('speaking')}, Tot={g.get('total_score')} | Comment: {g.get('comment')}")

    print("\nSample CM Notes:")
    for c in res.get('cm_notes', []):
        print(f"  - Staff: {c.get('staff_name')} | Note: {c.get('note')}")

if __name__ == '__main__':
    test_evi056()
