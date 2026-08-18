import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import get_students_db

def test_search_cases():
    test_queries = [
        "trần đình long",
        "Trần Đình Long",
        "TRẦN ĐÌNH LONG",
        "tran dinh long",
        "dinh long",
        "Đình Long",
        "Long",
        "EVI022"
    ]

    print("--- TESTING SMART VIETNAMESE SEARCH FOR TRẦN ĐÌNH LONG ---")
    for q in test_queries:
        res = get_students_db(search=q)
        matched_count = res.get('count', 0)
        found_names = [f"{s['code']} - {s['name']}" for s in res.get('data', []) if 'Long' in s['name']]
        print(f"Query: '{q}' ➔ Matched {matched_count} students. Found: {found_names}")
        assert matched_count > 0, f"Query '{q}' failed to return results!"

    print("\nALL SEARCH TESTS PASSED 100%!")

if __name__ == '__main__':
    test_search_cases()
