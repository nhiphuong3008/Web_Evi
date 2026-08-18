import sys
import os
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def test_moon_pdf():
    # 1. Test Moon 1 Unit 2 (Family)
    url_moon2 = "http://127.0.0.1:5001/api/students/EVI068/test-report-pdf?is_moon=1&class_name=Moon+1.1&test_name=Unit+02&tot_vocab=20&corr_vocab=18"
    print("Testing MOON 1 UNIT 2 PDF:", url_moon2)
    r1 = requests.get(url_moon2)
    assert r1.status_code == 200
    assert 'MOON 1 UNIT TEST' in r1.text
    assert 'UNIT 2: FAMILY' in r1.text
    assert 'Mommy' in r1.text
    assert 'Grandma' in r1.text
    assert 'Letter C' in r1.text
    print("  • MOON 1 UNIT 2 (FAMILY) Passed 100%!")

    # 2. Test Moon 3 Unit 2 (Feelings)
    url_moon3 = "http://127.0.0.1:5001/api/students/EVI068/test-report-pdf?is_moon=1&class_name=Moon+3.1&test_name=Unit+02"
    print("Testing MOON 3 UNIT 2 PDF:", url_moon3)
    r2 = requests.get(url_moon3)
    assert r2.status_code == 200
    assert 'MOON 3 UNIT TEST' in r2.text
    assert 'UNIT 2: MY FEELINGS' in r2.text
    assert 'Happy' in r2.text
    print("  • MOON 3 UNIT 2 (FEELINGS) Passed 100%!")

    print("\nALL DYNAMIC MOON SYLLABUS PDF TESTS PASSED 100%!")

if __name__ == '__main__':
    test_moon_pdf()
