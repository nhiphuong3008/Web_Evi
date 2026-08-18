import sys
import os
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def test_pdf():
    url = "http://127.0.0.1:5001/api/students/EVI068/test-report-pdf?test_name=Unit+4%2B5+Test&tot_lis=15&tot_rw=20&corr_lis=15&corr_rw=19&comment=Em+l%C3%A0m+b%C3%A0i+r%E1%BA%A5t+t%E1%BB%91t"
    print("Testing GET", url)
    r = requests.get(url)
    print("PDF Response status:", r.status_code)
    assert r.status_code == 200
    assert 'SUN UNIT TEST' in r.text
    assert 'OVERALL SCORE' in r.text
    print("PDF ENDPOINT TEST PASSED 100%!")

if __name__ == '__main__':
    test_pdf()
