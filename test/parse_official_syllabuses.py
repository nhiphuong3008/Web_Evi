import os
import sys
import re
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

official_dir = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)"

def extract_class_and_start_date(filename):
    fname = os.path.basename(filename)
    
    # 1. Extract class name
    class_match = re.search(r'(Galax\s*\d+\.\d+|Sun\s*\d+\.\d+|Moon\s*\d+\.\d+|Sun\s*S\.\d+|S\.\d+)', fname, re.IGNORECASE)
    cname = class_match.group(1) if class_match else ''
    
    if not cname:
        # Try broader match
        m2 = re.search(r'(Galax|Sun|Moon)\s*[\d\.]+', fname, re.IGNORECASE)
        cname = m2.group(0) if m2 else ''

    # Normalize class name
    cname = cname.replace('S.7', 'Sun S.7')

    # 2. Extract date (dd_mm_yyyy or dd_m_yyyy or yyyy)
    date_match = re.search(r'(\d{1,2})[_\/\-](\d{1,2})[_\/\-](\d{4})', fname)
    start_date = None
    if date_match:
        d, m, y = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
        try:
            start_date = datetime.date(y, m, d)
        except:
            pass
            
    if not start_date:
        # Check start from ...
        m_start = re.search(r'START\s+from\s+(\d{1,2})[_\/\-](\d{1,2})[_\/\-](\d{4})', fname, re.IGNORECASE)
        if m_start:
            d, m, y = int(m_start.group(1)), int(m_start.group(2)), int(m_start.group(3))
            try:
                start_date = datetime.date(y, m, d)
            except:
                pass

    return cname.strip(), start_date

def test_extract():
    for root, dirs, files in os.walk(official_dir):
        excel_files = [f for f in files if f.endswith('.xlsx') and not f.startswith('~$')]
        for f in excel_files:
            cname, sdate = extract_class_and_start_date(f)
            sdate_str = sdate.strftime('%Y-%m-%d (%A)') if sdate else 'DEFAULT'
            clean_f = f.encode('ascii', 'ignore').decode('ascii')
            print(f"File: '{clean_f}'\n  ===> Class: '{cname}' | Start Date: '{sdate_str}'\n")

if __name__ == '__main__':
    test_extract()
