"""
Full System Audit - EVI Dashboard
Kiểm tra toàn diện tất cả API endpoints, dữ liệu liên kết, đồng bộ và logic.
"""
import sys, os, json, requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = "http://localhost:5001"

def test_api(method, path, label, expected_keys=None, check_fn=None):
    """Test an API endpoint and return result."""
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{path}", timeout=15)
        else:
            r = requests.post(f"{BASE}{path}", json={}, timeout=15)
        
        if r.status_code != 200:
            return f"❌ [{r.status_code}] {label}: {r.text[:200]}"
        
        data = r.json()
        issues = []
        
        if expected_keys:
            for k in expected_keys:
                if k not in data:
                    issues.append(f"Missing key: '{k}'")
        
        if check_fn:
            result = check_fn(data)
            if result:
                issues.extend(result if isinstance(result, list) else [result])
        
        if issues:
            return f"⚠️ {label}: " + "; ".join(issues)
        return f"✅ {label}: OK"
    except Exception as e:
        return f"❌ {label}: {e}"

results = []
print("=" * 70)
print("  🔍 EVI DASHBOARD - FULL SYSTEM AUDIT")
print("=" * 70)

# ============================================================
# 1. HEALTH CHECK
# ============================================================
print("\n📌 1. HEALTH CHECK & CORE APIs")
results.append(test_api("GET", "/api/health", "Health Check", ["status", "mode"]))

# ============================================================
# 2. DASHBOARD SUMMARY
# ============================================================
print("\n📌 2. DASHBOARD SUMMARY")
def check_dashboard(d):
    issues = []
    ts = d.get("total_students")
    if ts is None or ts == 0:
        issues.append(f"total_students={ts} (expected > 200)")
    ac = d.get("active_classes")
    if ac is None or ac == 0:
        issues.append(f"active_classes={ac} (expected ~21)")
    rm = d.get("renewal_monthly")
    if not rm:
        issues.append("renewal_monthly is empty/null")
    return issues

results.append(test_api("GET", "/api/dashboard/summary", "Dashboard Summary",
    ["total_students", "active_classes"], check_dashboard))

# ============================================================
# 3. STUDENTS
# ============================================================
print("\n📌 3. STUDENTS MODULE")
def check_students(d):
    issues = []
    students = d if isinstance(d, list) else d.get("students", d.get("data", []))
    if not students:
        issues.append("No students returned")
        return issues
    count = len(students)
    if count < 200:
        issues.append(f"Only {count} students (expected ~437)")
    
    # Check critical fields
    sample = students[0] if students else {}
    for key in ["student_code", "name", "class_name", "status"]:
        if key not in sample:
            issues.append(f"Missing field '{key}' in student record")
    
    # Check for orphan students (no class)
    no_class = [s for s in students if not s.get("class_name") or s.get("class_name") in ["", "—", None]]
    active_no_class = [s for s in no_class if s.get("status") == "Đang học"]
    if active_no_class:
        issues.append(f"{len(active_no_class)} active students without class: {[s.get('student_code') for s in active_no_class[:5]]}")
    
    return issues

results.append(test_api("GET", "/api/students", "Students List", check_fn=check_students))

# ============================================================
# 4. SCHEDULE (TKB)
# ============================================================
print("\n📌 4. SCHEDULE (Thời Khóa Biểu)")
def check_schedule(d):
    issues = []
    schedule = d if isinstance(d, list) else d.get("schedule", d.get("data", []))
    if not schedule:
        issues.append("No schedule data returned")
    else:
        if len(schedule) < 10:
            issues.append(f"Only {len(schedule)} schedule entries (expected ~38+)")
    return issues

results.append(test_api("GET", "/api/schedule", "Schedule Matrix", check_fn=check_schedule))

# ============================================================
# 5. CLASSES (Quản lý lớp)
# ============================================================
print("\n📌 5. CLASS MANAGEMENT")
def check_classes(d):
    issues = []
    classes = d if isinstance(d, list) else d.get("classes", d.get("data", []))
    if not classes:
        issues.append("No classes returned")
    else:
        active = [c for c in classes if c.get("status") in ["Đang hoạt động", "active", None]]
        if len(classes) < 20:
            issues.append(f"Only {len(classes)} classes (expected ~21+)")
    return issues

results.append(test_api("GET", "/api/classes", "Classes List", check_fn=check_classes))

# ============================================================
# 6. SYLLABUS
# ============================================================
print("\n📌 6. SYLLABUS (Giáo án)")
def check_syllabus(d):
    issues = []
    syllabus = d if isinstance(d, list) else d.get("syllabuses", d.get("data", d.get("classes", [])))
    if not syllabus:
        issues.append("No syllabus data returned")
    return issues

results.append(test_api("GET", "/api/syllabus", "Syllabus List", check_fn=check_syllabus))

# ============================================================
# 7. CRM RENEWALS
# ============================================================
print("\n📌 7. CRM RENEWALS (Quản lý tái phí)")
def check_renewals(d):
    issues = []
    if "pipeline" not in d and "students" not in d and "data" not in d:
        # Check if it's top-level
        if "kpi" not in d and "summary" not in d:
            issues.append(f"Unexpected response structure. Keys: {list(d.keys())[:10]}")
    
    # Check KPI data
    kpi = d.get("kpi", d.get("summary", {}))
    if kpi:
        total = kpi.get("total_due", kpi.get("total", 0))
        if total == 0:
            issues.append("KPI total_due = 0")
    
    return issues

results.append(test_api("GET", "/api/crm/renewals/pipeline", "CRM Pipeline", check_fn=check_renewals))

# ============================================================
# 8. INTERACTIONS (Nhật ký tương tác)
# ============================================================
print("\n📌 8. PARENT INTERACTIONS")
def check_interactions(d):
    issues = []
    logs = d if isinstance(d, list) else d.get("logs", d.get("data", d.get("interactions", [])))
    if not logs:
        issues.append("No interaction logs returned")
    else:
        if len(logs) < 100:
            issues.append(f"Only {len(logs)} logs (expected 200+)")
    return issues

results.append(test_api("GET", "/api/interactions", "Interaction Logs", check_fn=check_interactions))

# ============================================================
# 9. HOLIDAY HISTORY
# ============================================================
print("\n📌 9. HOLIDAY & SHIFT ENGINE")
results.append(test_api("GET", "/api/schedule/holiday-history", "Holiday History"))

# ============================================================
# 10. AUTH
# ============================================================
print("\n📌 10. AUTHENTICATION")
def check_auth(d):
    issues = []
    if d.get("status") == "error" and "credentials" in str(d.get("message", "")).lower():
        return []  # Expected when not logged in
    return issues

results.append(test_api("GET", "/api/auth/me", "Auth Check", check_fn=check_auth))

# ============================================================
# 11. DATABASE INTEGRITY CHECK
# ============================================================
print("\n📌 11. DATABASE INTEGRITY")
try:
    from database.db_manager import db_session, init_db
    from database.models import (Student, LessonSyllabus, ClassSchedule, 
                                  ParentInteractionLog, StudentHistorySnapshot,
                                  MonthlyAttendanceRecord)
    init_db()
    session = db_session()
    
    # Count tables
    student_count = session.query(Student).count()
    active_count = session.query(Student).filter(Student.status == "Đang học").count()
    syllabus_count = session.query(LessonSyllabus).count()
    schedule_count = session.query(ClassSchedule).count()
    interaction_count = session.query(ParentInteractionLog).count()
    
    results.append(f"📊 DB Students: {student_count} total, {active_count} active")
    results.append(f"📊 DB Syllabus: {syllabus_count} lessons")
    results.append(f"📊 DB Schedule: {schedule_count} entries")
    results.append(f"📊 DB Interactions: {interaction_count} logs")
    
    # Check for data inconsistencies
    # a) Active students without class
    orphans = session.query(Student).filter(
        Student.status == "Đang học",
        (Student.class_name == None) | (Student.class_name == "") | (Student.class_name == "—")
    ).all()
    if orphans:
        codes = [s.student_code for s in orphans[:5]]
        results.append(f"⚠️ DB: {len(orphans)} active students without class: {codes}")
    else:
        results.append("✅ DB: All active students have class assignments")
    
    # b) Check students with remaining_sessions <= 0 but status is still "Đang học"
    from sqlalchemy import or_
    zero_remaining = session.query(Student).filter(
        Student.status == "Đang học",
        Student.remaining_sessions != None,
        Student.remaining_sessions <= 0
    ).all()
    if zero_remaining:
        codes = [(s.student_code, s.remaining_sessions, s.class_name) for s in zero_remaining[:5]]
        results.append(f"⚠️ DB: {len(zero_remaining)} active students with 0 remaining sessions: {codes}")
    else:
        results.append("✅ DB: No active students with 0 remaining sessions")
    
    # c) Check expiry_date format consistency  
    students_with_expiry = session.query(Student).filter(
        Student.expiry_date != None,
        Student.expiry_date != ""
    ).all()
    bad_format = []
    for s in students_with_expiry:
        ed = str(s.expiry_date) if s.expiry_date else ""
        if ed and not any([
            len(ed) == 10 and ed[4] == '-',   # YYYY-MM-DD
            len(ed) >= 19 and 'T' in ed,       # ISO
            '/' in ed,                          # DD/MM/YYYY
        ]):
            bad_format.append((s.student_code, ed))
    if bad_format:
        results.append(f"⚠️ DB: {len(bad_format)} students with unusual expiry_date format: {bad_format[:3]}")
    else:
        results.append("✅ DB: All expiry_date formats look consistent")
    
    # d) Check syllabus coverage - which classes have syllabus data
    classes_with_syllabus = session.query(LessonSyllabus.class_name).distinct().all()
    class_names = [c[0] for c in classes_with_syllabus]
    results.append(f"📊 DB: {len(class_names)} classes have syllabus data")
    
    # e) Check schedule completeness
    schedule_classes = session.query(ClassSchedule.class_name).distinct().all()
    schedule_names = [c[0] for c in schedule_classes]
    results.append(f"📊 DB: {len(schedule_names)} classes in schedule matrix")
    
    session.close()
    
except Exception as e:
    results.append(f"❌ DB Integrity Check Error: {e}")

# ============================================================
# 12. CROSS-MODULE SYNC CHECK
# ============================================================
print("\n📌 12. CROSS-MODULE SYNC CHECK")
try:
    # Compare dashboard total_students vs actual DB
    r = requests.get(f"{BASE}/api/dashboard/summary", timeout=15)
    dash = r.json()
    dash_students = dash.get("total_students", 0)
    dash_classes = dash.get("active_classes", 0)
    
    from database.db_manager import db_session
    from database.models import Student
    session = db_session()
    db_active = session.query(Student).filter(Student.status == "Đang học").count()
    session.close()
    
    if dash_students == db_active:
        results.append(f"✅ SYNC: Dashboard students ({dash_students}) = DB active ({db_active})")
    else:
        results.append(f"⚠️ SYNC MISMATCH: Dashboard shows {dash_students} but DB has {db_active} active students")
    
    # Check renewal data sync
    r2 = requests.get(f"{BASE}/api/crm/renewals/pipeline", timeout=15)
    renewal_data = r2.json()
    if "pipeline" in renewal_data:
        pipeline = renewal_data["pipeline"]
        pipeline_students = sum(len(v) if isinstance(v, list) else 0 for v in pipeline.values())
        results.append(f"📊 SYNC: CRM Pipeline has {pipeline_students} students in pipeline")
    elif "students" in renewal_data:
        results.append(f"📊 SYNC: CRM has {len(renewal_data['students'])} students")
    
except Exception as e:
    results.append(f"❌ Cross-module sync check error: {e}")

# ============================================================
# 13. FRONTEND STATIC FILES CHECK
# ============================================================
print("\n📌 13. FRONTEND FILES")
for path in ["/static/index.html", "/static/css/style.css", "/static/js/app.js",
             "/static/js/dashboard.js", "/static/js/schedule.js", "/static/js/students.js",
             "/static/js/renewals.js", "/static/js/interactions.js", "/static/js/auth.js"]:
    try:
        r = requests.get(f"{BASE}{path}", timeout=5)
        if r.status_code == 200:
            size_kb = len(r.content) / 1024
            results.append(f"✅ {path}: {size_kb:.1f} KB")
        else:
            results.append(f"❌ {path}: HTTP {r.status_code}")
    except Exception as e:
        results.append(f"❌ {path}: {e}")

# ============================================================
# FINAL REPORT
# ============================================================
print("\n" + "=" * 70)
print("  📋 AUDIT RESULTS")
print("=" * 70)
for r in results:
    print(f"  {r}")

errors = [r for r in results if r.startswith("❌")]
warnings = [r for r in results if r.startswith("⚠️")]
passed = [r for r in results if r.startswith("✅")]

print(f"\n  📊 SUMMARY: {len(passed)} PASSED | {len(warnings)} WARNINGS | {len(errors)} ERRORS")
print("=" * 70)
