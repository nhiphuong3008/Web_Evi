import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app

def test_crm():
    app = create_app()
    print("--- 🧪 TESTING CRM RENEWAL & STACKING FEE MODULE ---")
    
    with app.test_client() as client:
        # 1. Test Pipeline GET for Month 8/2026
        r1 = client.get('/api/crm/renewals/pipeline?month=8&year=2026')
        print("\n1. GET /api/crm/renewals/pipeline (Month 8/2026):")
        print("Status code:", r1.status_code)
        res1 = r1.get_json()
        assert res1.get('success') is True, f"Pipeline GET failed: {res1}"
        
        kpi = res1.get('kpi', {})
        print("KPI Summary:", kpi)
        kanban = res1.get('kanban', {})
        print(f"Kanban Stage Counts: D-30={len(kanban.get('d30', []))}, Contacted={len(kanban.get('contacted', []))}, Committed={len(kanban.get('committed', []))}, At-Risk={len(kanban.get('at_risk', []))}, Completed={len(kanban.get('completed', []))}")
        assert kpi.get('total_due') >= 4, f"Expected at least 4 due students for Month 8/2026, found {kpi.get('total_due')}"

        # 2. Test Payment Transaction (Chồng phí for Bùi Khánh Ly EVI241)
        r2 = client.post('/api/crm/renewals/transaction', json={
            'student_code': 'EVI241',
            'is_early_renewal': 1,
            'package_sessions': 72,
            'amount': 7200000.0,
            'notes': 'Test chồng phí cho Bùi Khánh Ly',
            'created_by': 'Tester'
        })
        print("\n2. POST /api/crm/renewals/transaction:")
        print("Status code:", r2.status_code, r2.get_json())
        assert r2.status_code == 200 and r2.get_json().get('success') is True

        # 3. Test Stage Transition (Chuyển stage cho EVI038 sang Contacted)
        r3 = client.post('/api/crm/renewals/stage', json={
            'subscription_id': 'SUB-EVI038-8-2026',
            'stage': 'Contacted',
            'note': 'Đã trao đổi với mẹ Hùng'
        })
        print("\n3. POST /api/crm/renewals/stage:")
        print("Status code:", r3.status_code, r3.get_json())
        assert r3.status_code == 200 and r3.get_json().get('success') is True

    print("\n✅ ALL CRM RENEWAL MODULE TESTS PASSED 100%!")

if __name__ == '__main__':
    test_crm()
