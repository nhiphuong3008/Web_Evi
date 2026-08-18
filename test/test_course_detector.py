import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import db_session
from database.models import ClassSchedule, ClassMaster, Student, LessonSyllabus

def detect_course_name(class_name, materials=''):
    text = f"{class_name} {materials}".upper()
    
    # Direct matches
    for i in range(1, 7):
        if f"MOON {i}" in text or f"MOON{i}" in text:
            return f"Moon {i}"
    for i in range(1, 6):
        if f"SUN {i}" in text or f"SUN{i}" in text:
            return f"Sun {i}"
            
    # Kid's Box / Starters / Flyers mapping
    if 'KB1' in text or 'KB 1' in text: return 'Sun 1'
    if 'KB2' in text or 'KB 2' in text: return 'Sun 2'
    if 'KB3' in text or 'KB 3' in text or 'FW1' in text: return 'Sun 3'
    if 'KB4' in text or 'KB 4' in text or 'FW2' in text: return 'Sun 4'
    if 'KB5' in text or 'KB 5' in text or 'FW3' in text: return 'Sun 5'
    if 'KB6' in text or 'KB 6' in text: return 'Moon 1'
    
    if 'THINK 1' in text: return 'Moon 1'
    if 'THINK 2' in text: return 'Moon 2'
    if 'THINK 3' in text: return 'Moon 3'
    
    # Fallback to Sun 2 or Sun 1 if unknown
    return 'Sun 2'

def test_detector():
    session = db_session()
    classes = session.query(ClassSchedule.class_name, ClassSchedule.materials).all()
    print(f"Testing detector on {len(classes)} classes from ClassSchedule:\n")
    
    for cname, mat in classes:
        course = detect_course_name(cname, mat)
        count = session.query(LessonSyllabus).filter(LessonSyllabus.course_name == course).count()
        print(f"Class '{cname}' (mat: '{mat}') ===> Detected Syllabus: '{course}' ({count} lessons)")

if __name__ == '__main__':
    test_detector()
