"""
Script đồng bộ điểm số từ Google Sheet → CSDL SQLite (unit_grades).
Sheet ID: 1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA
GID: 1373957511

Cấu trúc dữ liệu nguồn:
  Col 0: Tháng/Năm (3/2026)
  Col 1: Mã HS (EVI378)
  Col 2: Tên HS
  Col 3: Tên tiếng Anh
  Col 4: Lớp
  Col 5: Giáo viên
  Col 6: CM
  Col 7: Tên bài test (Unit 06, Midterm, Final)
  Col 8: Điểm tổng /10
  Col 17: Nhận xét chi tiết
  Col 29: Listening /10
  Col 30: Reading-Writing /10
  Col 31: Speaking /10
"""
import os, sys, csv, io, urllib.request, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import UnitGrade, Student

SHEET_ID = "1Dk2ysAqsdE-dHKvYma8xygBjvToa_oDybPlN6aUL6vA"
GID = "1373957511"


def parse_vn_float(val):
    """Parse Vietnamese decimal format (comma as decimal separator) to float."""
    if not val or not val.strip():
        return None
    val = val.strip().replace(',', '.')
    try:
        return float(val)
    except ValueError:
        return None


def normalize_test_name(raw):
    """Normalize test name to match existing DB convention."""
    raw = raw.strip()
    # Map Google Sheet format to DB format
    mapping = {
        'Unit 01': 'Unit 01', 'Unit 02': 'Unit 02', 'Unit 03': 'Unit 03',
        'Unit 04': 'Unit 04', 'Unit 05': 'Unit 05', 'Unit 06': 'Unit 06',
        'Unit 07': 'Unit 07', 'Unit 08': 'Unit 08', 'Unit 09': 'Unit 09',
        'Unit 10': 'Unit 10', 'Unit 11': 'Unit 11', 'Unit 12': 'Unit 12',
        'Unit 5-6': 'Unit 5-6', 'Unit 11-12': 'Unit 11-12',
        'Midterm': 'Giữa khóa', 'Final': 'Cuối khóa',
    }
    return mapping.get(raw, raw)


def fetch_csv_data():
    """Fetch CSV data from Google Sheet."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read().decode('utf-8')
    reader = csv.reader(io.StringIO(data))
    return list(reader)


def get_col(row, idx, default=''):
    """Safe column accessor."""
    if idx < len(row):
        return row[idx].strip()
    return default


def main():
    print("=" * 80)
    print("🔄 ĐỒNG BỘ ĐIỂM SỐ TỪ GOOGLE SHEET → CSDL SQLITE")
    print("=" * 80)

    # Step 1: Fetch data
    print("\n📥 Fetching CSV data from Google Sheet...")
    rows = fetch_csv_data()
    print(f"   Tổng số dòng: {len(rows)}")

    # Step 2: Filter valid EVI records
    evi_rows = [r for r in rows if len(r) > 1 and r[1].strip().startswith('EVI')]
    print(f"   Bản ghi có mã EVI: {len(evi_rows)}")

    # Step 3: Build student code map
    session = db_session()
    all_students = {s.code: s for s in session.query(Student).all()}
    print(f"   Tổng học sinh trong DB: {len(all_students)}")

    # Step 4: Process records
    inserted = 0
    updated = 0
    skipped = 0
    unmatched_codes = set()
    errors = []

    for idx, row in enumerate(evi_rows):
        student_code = get_col(row, 1)
        student_name = get_col(row, 2)
        english_name = get_col(row, 3)
        class_name = get_col(row, 4)
        test_name_raw = get_col(row, 7)

        # Skip rows without essential data
        if not student_code or not test_name_raw:
            skipped += 1
            continue

        # Normalize class name (fix capitalization inconsistencies)
        if class_name.lower() in ('bảo lưu', 'bảo lưu'):
            class_name = 'Bảo lưu'

        test_name = normalize_test_name(test_name_raw)

        # Parse scores
        total_score = parse_vn_float(get_col(row, 8))
        listening = parse_vn_float(get_col(row, 29))
        reading_writing = parse_vn_float(get_col(row, 30))
        speaking = parse_vn_float(get_col(row, 31))
        comment = get_col(row, 17)

        # Clean up comment (remove literal \n)
        if comment:
            comment = comment.replace('\\n', '\n')

        # Check student exists in DB
        student = all_students.get(student_code)
        if not student:
            unmatched_codes.add(student_code)
            # Still import but without FK relationship
            pass

        # Check if record already exists (upsert by student_code + class_name + test_name)
        existing = session.query(UnitGrade).filter(
            UnitGrade.student_code == student_code,
            UnitGrade.class_name == class_name,
            UnitGrade.test_name == test_name
        ).first()

        if existing:
            # Update existing record
            if listening is not None:
                existing.listening = listening
            if reading_writing is not None:
                existing.reading_writing = reading_writing
            if speaking is not None:
                existing.speaking = speaking
            if total_score is not None:
                existing.total_score = total_score
            if comment:
                existing.comment = comment
            if english_name:
                existing.english_name = english_name
            existing.listening_max = 10.0
            existing.reading_writing_max = 10.0
            existing.speaking_max = 10.0
            existing.max_score = 10.0
            updated += 1
        else:
            # Insert new record
            grade = UnitGrade(
                student_code=student_code if student else None,
                student_name=student_name,
                english_name=english_name,
                class_name=class_name,
                course=class_name,
                test_name=test_name,
                listening=listening,
                listening_max=10.0,
                reading_writing=reading_writing,
                reading_writing_max=10.0,
                speaking=speaking,
                speaking_max=10.0,
                total_score=total_score,
                max_score=10.0,
                comment=comment
            )
            session.add(grade)
            inserted += 1

    # Commit
    session.commit()

    # Report
    print("\n" + "=" * 80)
    print("📊 KẾT QUẢ ĐỒNG BỘ:")
    print(f"   ✅ Inserted (mới):   {inserted}")
    print(f"   🔄 Updated (cập nhật): {updated}")
    print(f"   ⏭️  Skipped (bỏ qua):  {skipped}")
    print(f"   ❌ Mã HS không khớp DB: {len(unmatched_codes)}")
    if unmatched_codes:
        print(f"      Codes: {sorted(unmatched_codes)}")

    # Verify totals
    total_after = session.query(UnitGrade).count()
    active_classes = session.query(UnitGrade.class_name).distinct().order_by(UnitGrade.class_name).all()
    print(f"\n   📈 Tổng bản ghi unit_grades sau sync: {total_after}")
    print(f"   📋 Tổng lớp học: {len(active_classes)}")

    session.close()
    print("\n✅ ĐỒNG BỘ HOÀN TẤT!")


if __name__ == '__main__':
    main()
