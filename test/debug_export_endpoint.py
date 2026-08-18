import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
app = create_app()

def test_export():
    with app.test_client() as client:
        print("1. Testing GET /api/students/EVI056/export?format=pdf...")
        r_pdf = client.get('/api/students/EVI056/export?format=pdf')
        print(f"   Status: {r_pdf.status_code}, Content-Type: {r_pdf.content_type}, Len: {len(r_pdf.data)}")

        print("\n2. Testing GET /api/students/EVI056/export?format=word...")
        r_word = client.get('/api/students/EVI056/export?format=word')
        print(f"   Status: {r_word.status_code}, Content-Type: {r_word.content_type}, Headers: {dict(r_word.headers)}, Len: {len(r_word.data)}")

        print("\n3. Testing GET /api/students/EVI056/export?format=excel...")
        r_excel = client.get('/api/students/EVI056/export?format=excel')
        print(f"   Status: {r_excel.status_code}, Content-Type: {r_excel.content_type}, Headers: {dict(r_excel.headers)}, Len: {len(r_excel.data)}")

if __name__ == '__main__':
    test_export()
