import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_crm_renewal_pipeline_db

class TestMonth72027Pipeline(unittest.TestCase):
    def test_month_7_2027_pipeline(self):
        res = get_crm_renewal_pipeline_db(month=7, year=2027)
        self.assertTrue(res['success'])
        
        all_items = []
        for stage, items in res['kanban'].items():
            for item in items:
                all_items.append(item)

        print(f"\n=== CRM RENEWAL PIPELINE FOR MONTH 7/2027 ({len(all_items)} students) ===")
        for item in all_items:
            print(f"  - [{item.get('student_code')}] {item.get('student_name')} | Class: {item.get('class_name')} | Expiry: {item.get('current_end_date')}")

        # Check EVI124 is present
        evi124 = next((x for x in all_items if x.get('student_code') == 'EVI124'), None)
        self.assertIsNotNone(evi124)
        self.assertEqual(evi124['student_name'], 'Nguyễn Đức Bình')
        self.assertEqual(evi124['current_end_date'], '29/07/2027')
        print("\n✅ EVI124 Nguyễn Đức Bình is NOW PROPERLY INCLUDED in Month 7/2027 CRM Renewal Pipeline!")

if __name__ == '__main__':
    unittest.main()
