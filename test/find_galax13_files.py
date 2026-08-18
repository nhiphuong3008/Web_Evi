import os
official_dir = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\14. Class syllabus (official)"

for root, dirs, files in os.walk(official_dir):
    for f in files:
        if 'Galax 1.3' in f:
            print(os.path.join(root, f))
