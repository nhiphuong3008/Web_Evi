import os

js_path = r"c:\Users\nhiph\OneDrive\Documents\Web_Evi\static\js\search.js"

with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File: {js_path}")
print(f"Size: {len(content)} characters, {len(content.splitlines())} lines")

# Basic check for parenthesis/brace matching
open_braces = content.count('{')
close_braces = content.count('}')
print(f"Braces check: {{ = {open_braces}, }} = {close_braces}")

if open_braces == close_braces:
    print("✅ Braces matched perfectly!")
else:
    print("❌ Warning: Brace count mismatch!")

