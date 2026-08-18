import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('static/js/moon_syllabus_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

moon1_midterm = db['Moon 1']['Midterm test']
print("Moon 1 Midterm Test Data:")
print("  Title:", moon1_midterm['title'])
print("  Subtitle:", moon1_midterm['subtitle'])
print("  Vocab:", moon1_midterm['vocab'])
print("  Phonics:", moon1_midterm['phonics'])
print("  Struct:", moon1_midterm['struct'])

assert "Book" in moon1_midterm['vocab']
assert "Crayon" in moon1_midterm['vocab']
assert "Eraser" in moon1_midterm['vocab']

print("\nTEST PASSED 100%! 🚀")
