import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import init_db, db_session
from database.models import (
    Student, ClassMaster, HomeworkRecord, UnitGrade,
    ParentInteractionLog, ClassFeedbackLog, StudentWithdrawal, ClassSchedule,
    StudentHistorySnapshot, RenewalDetailLog, MonthlyAttendanceRecord,
    GrammarClubEnrollment, TestScheduleEntry, LevelCompletion, KpiMonthlyReport
)

class TestAll4SheetsMigration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.session = db_session()

    def test_01_students_and_classes(self):
        student_count = self.session.query(Student).count()
        class_count = self.session.query(ClassMaster).count()
        print(f"\n[TEST 1] Students count: {student_count}, Classes count: {class_count}")
        self.assertGreater(student_count, 0, "Students table should not be empty")

    def test_02_homework_and_grades(self):
        hw_count = self.session.query(HomeworkRecord).count()
        grade_count = self.session.query(UnitGrade).count()
        print(f"[TEST 2] Homework count: {hw_count}, UnitGrades count: {grade_count}")
        self.assertGreater(hw_count, 0, "HomeworkRecords table should contain data")
        self.assertGreater(grade_count, 0, "UnitGrades table should contain data")

    def test_03_extended_tables(self):
        history_count = self.session.query(StudentHistorySnapshot).count()
        renewal_count = self.session.query(RenewalDetailLog).count()
        att_count = self.session.query(MonthlyAttendanceRecord).count()
        grammar_count = self.session.query(GrammarClubEnrollment).count()
        test_sched_count = self.session.query(TestScheduleEntry).count()
        level_comp_count = self.session.query(LevelCompletion).count()
        kpi_count = self.session.query(KpiMonthlyReport).count()
        feedback_count = self.session.query(ClassFeedbackLog).count()
        interaction_count = self.session.query(ParentInteractionLog).count()

        print(f"[TEST 3] Extended tables count:")
        print(f"  - StudentHistorySnapshot: {history_count}")
        print(f"  - RenewalDetailLog: {renewal_count}")
        print(f"  - MonthlyAttendanceRecord: {att_count}")
        print(f"  - GrammarClubEnrollment: {grammar_count}")
        print(f"  - TestScheduleEntry: {test_sched_count}")
        print(f"  - LevelCompletion: {level_comp_count}")
        print(f"  - KpiMonthlyReport: {kpi_count}")
        print(f"  - ClassFeedbackLog: {feedback_count}")
        print(f"  - ParentInteractionLog: {interaction_count}")

        self.assertGreater(history_count, 0)
        self.assertGreater(renewal_count, 0)
        self.assertGreater(att_count, 0)
        self.assertGreater(grammar_count, 0)
        self.assertGreater(test_sched_count, 0)
        self.assertGreater(level_comp_count, 0)
        self.assertGreater(kpi_count, 0)

    def test_04_student_extended_fields(self):
        # Verify student table extended columns (year_of_birth, age, academic_level, parent_attitude)
        students_with_extended_data = self.session.query(Student).filter(
            (Student.academic_level != None) | (Student.parent_attitude != None) | (Student.year_of_birth != None)
        ).count()
        print(f"[TEST 4] Students with extended fields (academic/parent attitude/YOB): {students_with_extended_data}")
        self.assertGreater(students_with_extended_data, 0)

if __name__ == '__main__':
    unittest.main()
