import urllib.request
import json

url = 'http://127.0.0.1:5001/api/attendance?class_name=Galax+1.3&date=2026-08-06'
r = urllib.request.urlopen(url)
d = json.loads(r.read())
print(f"Live HTTP API returned {len(d.get('data',[]))} attendance & HW records:")
for rec in d.get('data', []):
    c_name = rec['student_name'].encode('ascii', 'ignore').decode('ascii')
    c_comm = rec.get('hw_comment', '').encode('ascii', 'ignore').decode('ascii')
    c_stat = rec.get('hw_submission_status', '').encode('ascii', 'ignore').decode('ascii')
    print(f"  {rec['student_code']} | {c_name:20s} | Score: {rec.get('hw_score')} ({rec.get('hw_correct_answers')}/{rec.get('hw_total_questions')}) | Status: {c_stat} | Comment: {c_comm}")
