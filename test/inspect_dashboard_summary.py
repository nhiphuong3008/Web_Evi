import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.db_service import get_dashboard_summary

res = get_dashboard_summary()
print("DASHBOARD SUMMARY RES:")
print("KPI:", json.dumps(res.get('kpi'), ensure_ascii=False, indent=2))
print("ACS STATS:", json.dumps(res.get('acs_stats'), ensure_ascii=False, indent=2))
print("RENEWAL MONTHLY COUNT:", len(res.get('renewal_monthly', [])))
print("CLASSES COUNT:", len(res.get('classes', [])))
if res.get('classes'):
    print("SAMPLE CLASS:", json.dumps(res['classes'][0], ensure_ascii=False, indent=2))
