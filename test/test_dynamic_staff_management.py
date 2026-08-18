"""
Test script to verify dynamic staff list and cascade update staff name functionality.
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

import unittest
from services.db_service import get_staff_list_db, update_staff_name_db, db_session
from database.models import ClassSchedule

class TestDynamicStaffManagement(unittest.TestCase):
    def test_get_staff_list_db(self):
        res = get_staff_list_db()
        self.assertTrue(res.get('success'))
        self.assertIn('cms', res)
        self.assertIn('teachers', res)
        self.assertGreater(len(res['cms']), 0)
        self.assertGreater(len(res['teachers']), 0)

    def test_update_staff_name_cascade(self):
        session = db_session()
        # Find an existing class teacher or CM
        cs = session.query(ClassSchedule).first()
        if cs and cs.cm_staff:
            cs_id = cs.id
            old_cm = cs.cm_staff
            temp_name = old_cm + "_TEST"
            session.close()
            
            # Test rename cascade
            res1 = update_staff_name_db(old_cm, temp_name, role='cm')
            self.assertTrue(res1.get('success'))
            
            # Requery to verify updated
            session2 = db_session()
            updated_cs = session2.query(ClassSchedule).filter(ClassSchedule.id == cs_id).first()
            self.assertEqual(updated_cs.cm_staff, temp_name)
            session2.close()
            
            # Revert back
            res2 = update_staff_name_db(temp_name, old_cm, role='cm')
            self.assertTrue(res2.get('success'))
        else:
            session.close()

if __name__ == '__main__':
    unittest.main()
