import os
import sys
import re
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session, init_db
from database.models import ClassScheduleAdjustment

official_dir = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)"

def extract_class_and_start_date(filename):
    fname = os.path.basename(filename)
    
    # 1. Extract class name
    class_match = re.search(r'(Galax\s*\d+\.\d+|Sun\s*\d+\.\d+|Moon\s*\d+\.\d+|Sun\s*S\.\d+|S\.\d+)', fname, re.IGNORECASE)
    cname = class_match.group(1) if class_match else ''
    
    if not cname:
        m2 = re.search(r'(Galax|Sun|Moon)\s*\d+\.\d+', fname, re.IGNORECASE)
        cname = m2.group(0) if m2 else ''

    cname = cname.replace('S.7', 'Sun S.7').strip()

    # 2. Extract date
    date_match = re.search(r'(\d{1,2})[_\/\-](\d{1,2})[_\/\-](\d{4})', fname)
    start_date = None
    if date_match:
        d, m, y = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
        try:
            start_date = datetime.date(y, m, d)
        except:
            pass

    return cname, start_date

def import_start_dates():
    init_db()
    session = db_session()
    
    saved_count = 0
    
    start_date_dict = {}
    for root, dirs, files in os.walk(official_dir):
        excel_files = [f for f in files if f.endswith('.xlsx') and not f.startswith('~$')]
        for f in excel_files:
            cname, sdate = extract_class_and_start_date(f)
            if not cname or not sdate:
                continue
            sdate_str = sdate.strftime('%Y-%m-%d')
            start_date_dict[cname] = (sdate_str, f)

    for cname, (sdate_str, f) in start_date_dict.items():
        adj = session.query(ClassScheduleAdjustment).filter(ClassScheduleAdjustment.class_name == cname).first()
        if not adj:
            adj = ClassScheduleAdjustment(
                class_name=cname,
                start_date=sdate_str,
                note=f"Imported from official file: {f}"
            )
            session.add(adj)
        else:
            adj.start_date = sdate_str
            adj.note = f"Updated from official file: {f}"
        saved_count += 1

    session.commit()
    print(f"Successfully imported/updated {saved_count} official class start dates in DB!")
    session.close()

if __name__ == '__main__':
    import_start_dates()
