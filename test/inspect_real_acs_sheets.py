import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from services.data_parser import DataParser

parser = DataParser()
acs = parser.parse_acs_stats()
print("Parsed ACS stats from Google Sheets parser:")
print(acs)
