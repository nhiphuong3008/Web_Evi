import os
import sys
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')
from services.db_service import get_schedule_matrix_db

def run_tests():
    print("=== RUNNING SCHEDULE MATRIX AUDIT & VERIFICATION ===")
    
    # 1. Direct DB record count
    conn = sqlite3.connect('database/evi_center.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM class_schedules")
    total_db_records = cursor.fetchone()[0]
    print(f"[TEST 1] Total DB Records in class_schedules: {total_db_records}")
    assert total_db_records == 40, f"Expected 40 records, found {total_db_records}"
    print("  -> PASS!")

    # 2. Check duplicate (class_name, day, shift_code)
    cursor.execute("""
        SELECT class_name, day, shift_code, COUNT(*) 
        FROM class_schedules 
        GROUP BY LOWER(TRIM(class_name)), day, shift_code 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    print(f"[TEST 2] Duplicates count: {len(duplicates)}")
    assert len(duplicates) == 0, f"Found duplicates: {duplicates}"
    print("  -> PASS!")

    # 3. Check section values
    cursor.execute("SELECT DISTINCT section FROM class_schedules")
    sections = [r[0] for r in cursor.fetchall()]
    print(f"[TEST 3] Distinct sections: {sections}")
    assert sections == ['Chính thức'], f"Expected only 'Chính thức', found {sections}"
    print("  -> PASS!")

    conn.close()

    # 4. Check get_schedule_matrix_db API output
    res = get_schedule_matrix_db()
    assert res.get('success') is True, f"API error: {res.get('error')}"
    matrix = res.get('matrix', [])
    print(f"[TEST 4] API Matrix rows returned: {len(matrix)}")
    
    # Count total classes rendered across matrix
    classes_in_matrix = set()
    for row in matrix:
        if row.get('mt5'):
            classes_in_matrix.add(row['mt5']['class_name'])
        if row.get('mt6'):
            classes_in_matrix.add(row['mt6']['class_name'])
            
    print(f"[TEST 5] Total unique classes rendered in matrix: {len(classes_in_matrix)}")
    print(f"  Classes: {sorted(list(classes_in_matrix))}")
    assert len(classes_in_matrix) == 20, f"Expected 20 unique classes, found {len(classes_in_matrix)}"
    print("  -> PASS!")

    print("\nALL 5 VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")

if __name__ == '__main__':
    run_tests()
