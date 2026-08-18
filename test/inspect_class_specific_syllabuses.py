import os
import sys
import re
import openpyxl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

official_dir = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)"

def inspect_class_files():
    found_classes = {}
    
    for root, dirs, files in os.walk(official_dir):
        excel_files = [f for f in files if f.endswith('.xlsx') and not f.startswith('~$')]
        for f in excel_files:
            filepath = os.path.join(root, f)
            cname = ''
            
            # Match class name from filename
            m = re.search(r'(Galax\s*\d+\.\d+|Sun\s*\d+\.\d+|Moon\s*\d+\.\d+|Sun\s*S\.\d+|S\.\d+)', f, re.IGNORECASE)
            if m:
                cname = m.group(1).strip().replace('S.7', 'Sun S.7')
            if not cname:
                m2 = re.search(r'(Galax|Sun|Moon)\s*\d+\.\d+', f, re.IGNORECASE)
                if m2: cname = m2.group(0).strip()
                
            if not cname:
                continue

            found_classes[cname] = (f, filepath)

    print(f"Discovered {len(found_classes)} class-specific Excel files:\n")
    for cname in sorted(found_classes.keys()):
        fname, path = found_classes[cname]
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        clean_fname = fname.encode('ascii', 'ignore').decode('ascii')
        print(f"Class '{clean_cname}' ===> File: '{clean_fname}'")

if __name__ == '__main__':
    inspect_class_files()
