import sys, os, time, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_session
from database.models import GrammarClubEnrollment
import services.google_sheets as gs

session = db_session()

try:
    print("Fetching Sheet 1 'DS lớp ngữ pháp + CLB'...")
    s1 = gs.get_spreadsheet('master')
    if s1:
        ws_gc = None
        for w in s1.worksheets():
            if 'ngữ pháp' in w.title.lower() or 'clb' in w.title.lower():
                ws_gc = w
                break
        if ws_gc:
            rows = ws_gc.get_all_values()
            session.query(GrammarClubEnrollment).delete()
            gc_count = 0
            for r in rows[1:]:
                name = r[1].strip() if len(r) > 1 else ''
                if not name or name.lower() in ['tên học sinh', 'họ và tên']:
                    continue
                session.add(GrammarClubEnrollment(
                    student_name=name,
                    english_name=r[2].strip() if len(r) > 2 else '',
                    dob=r[3].strip() if len(r) > 3 else '',
                    parent_name=r[4].strip() if len(r) > 4 else '',
                    phone=r[5].strip() if len(r) > 5 else '',
                    main_class=r[0].strip() if len(r) > 0 else '',
                    school_grade=r[6].strip() if len(r) > 6 else '',
                    grammar_class=r[7].strip() if len(r) > 7 else '',
                    speaking_club=r[8].strip() if len(r) > 8 else '',
                    note_grammar=r[10].strip() if len(r) > 10 else ''
                ))
                gc_count += 1
            session.commit()
            print(f"✅ Đã nạp thành công {gc_count} bản ghi vào GrammarClubEnrollment!")
        else:
            print("⚠️ Tab 'DS lớp ngữ pháp + CLB' không tìm thấy")
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    session.close()
