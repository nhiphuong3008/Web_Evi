import os
import sys
import re

official_dir = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)"

def extract_class_name(filename):
    fname = os.path.basename(filename)
    m = re.search(r'(Galax\s*\d+\.\d+|Sun\s*\d+\.\d+|Moon\s*\d+\.\d+|Sun\s*S\.\d+|S\.\d+)', fname, re.IGNORECASE)
    cname = m.group(1).strip().replace('S.7', 'Sun S.7') if m else ''
    if not cname:
        m2 = re.search(r'(Galax|Sun|Moon)\s*\d+\.\d+', fname, re.IGNORECASE)
        if m2: cname = m2.group(0).strip()
    return cname

def deduplicate_class_files():
    class_files_map = {}
    
    for root, dirs, files in os.walk(official_dir):
        for f in files:
            if f.endswith('.xlsx') and not f.startswith('~$'):
                filepath = os.path.join(root, f)
                cname = extract_class_name(f)
                if not cname:
                    continue
                if cname not in class_files_map:
                    class_files_map[cname] = []
                class_files_map[cname].append((f, filepath))

    print(f"Total Unique Classes in Official Folder: {len(class_files_map)}\n")
    
    chosen_files = {}
    for cname in sorted(class_files_map.keys()):
        flist = class_files_map[cname]
        clean_cname = cname.encode('ascii', 'ignore').decode('ascii')
        
        # Priority: file with 'doi gtrinh' or 'Syllabus' or newest modified time
        best_file = flist[0]
        if len(flist) > 1:
            # Sort by modified time or keyword 'doi gtrinh'
            flist.sort(key=lambda x: (
                1 if 'doi gtrinh' in x[0].lower() or 'doi gtr' in x[0].lower() else 0,
                0 if 'finished' in x[0].lower() else 1,
                os.path.getmtime(x[1])
            ), reverse=True)
            best_file = flist[0]
            
        chosen_files[cname] = best_file[1]
        clean_best = best_file[0].encode('ascii', 'ignore').decode('ascii')
        print(f"Class '{clean_cname}' ({len(flist)} files) ===> Chosen Best File: '{clean_best}'")

    return chosen_files

if __name__ == '__main__':
    deduplicate_class_files()
