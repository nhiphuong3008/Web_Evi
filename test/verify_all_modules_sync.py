import sys
import os
import sqlite3
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import (
    get_students_db,
    get_student_detail_db,
    get_crm_renewal_pipeline_db,
    get_monthly_renewal_pdf_data_db
)

class TestAllModulesSync(unittest.TestCase):
    def test_evi266_sync_across_all_modules(self):
        # 1. Student detail 360
        st_detail = get_student_detail_db('EVI266')
        self.assertTrue(st_detail['success'])
        st = st_detail['student']
        self.assertEqual(st['code'], 'EVI266')
        self.assertEqual(st['total_sessions'], 96)
        self.assertEqual(st['remaining_sessions'], 25)
        self.assertEqual(st['expiry_date'], '05/11/2026')
        self.assertEqual(st['expiry_month'], '11')
        print("\n✅ 1. Student Detail 360 profile returns correct primary course date: 05/11/2026 (Month 11)")

        # 2. CRM Renewal Pipeline Month 11/2026
        pipe = get_crm_renewal_pipeline_db(month=11, year=2026)
        self.assertTrue(pipe['success'])
        found = False
        for stage, items in pipe['kanban'].items():
            for item in items:
                if item['student_code'] == 'EVI266':
                    found = True
                    self.assertEqual(item['current_end_date'], '05/11/2026')
        self.assertTrue(found)
        print("✅ 2. CRM Renewal Pipeline Month 11/2026 returns EVI266 with Hạn hết phí: 05/11/2026")

        # 3. Monthly Renewal PDF Data Month 11/2026
        pdf_data = get_monthly_renewal_pdf_data_db(month=11, year=2026)
        self.assertTrue(pdf_data['success'])
        found_pdf = False
        for item in pdf_data.get('data', []):
            if item.get('student_code') == 'EVI266':
                found_pdf = True
                self.assertEqual(item.get('expected_expiry_date'), '05/11/2026')
        self.assertTrue(found_pdf)
        print("✅ 3. Monthly Renewal PDF Data Month 11/2026 returns EVI266 with Hạn hết phí: 05/11/2026")

if __name__ == '__main__':
    unittest.main()
