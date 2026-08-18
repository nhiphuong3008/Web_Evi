import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.db_service import get_schedule_matrix_db

def test_matrix():
    res = get_schedule_matrix_db()
    matrix = res.get('matrix', [])
    print(f"Total Schedule Matrix Days: {len(matrix)}\n")
    
    matrix = res.get('matrix', [])
    print(f"Total Schedule Matrix Rows: {len(matrix)}\n")
    
    for row in matrix:
        d_name = str(row.get('day_code') or '')
        mt5_class = row['mt5']['class_name'] if row.get('mt5') else '---'
        mt6_class = row['mt6']['class_name'] if row.get('mt6') else '---'
        if row.get('is_first_row_of_day'):
            print(f"\nDay: {d_name:5s} (Rows: {row['row_span']})")
        print(f"  -> MT5: {mt5_class:15s} | MT6: {mt6_class:15s}")

if __name__ == '__main__':
    test_matrix()
