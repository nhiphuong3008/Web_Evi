import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import init_db, db_session
from database.models import Student, ClassMaster
from database.migrate_sheets_to_db import run_migration
from services.db_service import get_students_db, get_cm_classes_db

class TestMultiClassStudents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n--- Running migration to test multi-class student aggregation ---")
        run_migration()

    def test_01_multi_class_students_exist(self):
        session = db_session()
        st_multi = session.query(Student).filter(Student.class_name.like('%,%')).all()
        print(f"\n[TEST 1] Found {len(st_multi)} students enrolled in MULTIPLE classes:")
        for st in st_multi:
            print(f"  - [{st.code}] {st.full_name}: {st.class_name}")
        self.assertGreater(len(st_multi), 0, "Should have students enrolled in multiple classes")

    def test_02_student_search_by_class(self):
        res = get_students_db(class_name="Khóa Debate 2026")
        self.assertTrue(res['success'])
        found_names = [st['name'] for st in res['data']]
        print(f"\n[TEST 2] Students enrolled in 'Khóa Debate 2026' ({len(found_names)}):")
        for n in found_names:
            print(f"  - {n}")
        self.assertIn("Nguyễn Ngọc Huyền", found_names, "Nguyễn Ngọc Huyền should be found in Khóa Debate 2026")
        self.assertIn("Dương Diệp Anh", found_names, "Dương Diệp Anh should be found in Khóa Debate 2026")

        res_galax = get_students_db(class_name="Galax 1.4")
        found_galax = [st['name'] for st in res_galax['data']]
        self.assertIn("Nguyễn Ngọc Huyền", found_galax, "Nguyễn Ngọc Huyền should ALSO be found in Galax 1.4")

    def test_03_available_classes(self):
        res = get_students_db()
        self.assertTrue(res['success'])
        classes = res['available_classes']
        print(f"\n[TEST 3] Available classes list ({len(classes)}): {classes[:10]}...")
        self.assertIn("Khóa Debate 2026", classes)
        self.assertIn("Khóa Speaking 2026", classes)

if __name__ == '__main__':
    unittest.main()
