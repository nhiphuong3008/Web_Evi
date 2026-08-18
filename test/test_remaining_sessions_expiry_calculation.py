import sys
import os
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

DAYS_MAP = {
    'T2': 0, 'THỨ 2': 0, 'THỨ HÀI': 0, 'MON': 0, 'MONDAY': 0,
    'T3': 1, 'THỨ 3': 1, 'THỨ BA': 1, 'TUE': 1, 'TUESDAY': 1,
    'T4': 2, 'THỨ 4': 2, 'THỨ TƯ': 2, 'WED': 2, 'WEDNESDAY': 2,
    'T5': 3, 'THỨ 5': 3, 'THỨ NĂM': 3, 'THU': 3, 'THURSDAY': 3,
    'T6': 4, 'THỨ 6': 4, 'THỨ SÁU': 4, 'FRI': 4, 'FRIDAY': 4,
    'T7': 5, 'THỨ 7': 5, 'THỨ BẢY': 5, 'SAT': 5, 'SATURDAY': 5,
    'CN': 6, 'CHỦ NHẬT': 6, 'SUN': 6, 'SUNDAY': 6
}

def parse_schedule_days(schedule_str):
    if not schedule_str:
        return [0, 3] # Default MT5
    s = schedule_str.upper()
    days = set()
    if 'MT5' in s or 'M-T5' in s or 'T2-T5' in s or 'THỨ 2 - THỨ 5' in s or 'T2,T5' in s:
        days.update([0, 3])
    elif 'T3T6' in s or 'T3-T6' in s or 'T3,T6' in s:
        days.update([1, 4])
    elif 'T4T7' in s or 'T4-T7' in s or 'T4,T7' in s:
        days.update([2, 5])
    elif 'T5CN' in s or 'T5-CN' in s or 'T5,CN' in s:
        days.update([3, 6])
    elif 'T6CN' in s or 'T6-CN' in s or 'T6,CN' in s:
        days.update([4, 6])
    elif 'T7CN' in s or 'T7-CN' in s or 'T7,CN' in s:
        days.update([5, 6])
    else:
        for k, v in DAYS_MAP.items():
            if k in s:
                days.add(v)
    return sorted(list(days)) if days else [0, 3]

def calculate_fee_expiry_date(remaining_sessions, schedule_str='', start_from_date=None, off_dates=None):
    """
    Tính Ngày hết phí của học sinh theo SỐ BUỔI CÒN LẠI (remaining_sessions).
    - Nếu remaining_sessions <= 0: 'Đã hết phí'
    - Nếu remaining_sessions > 0: Đếm tiến N buổi học tương ứng theo Lịch học (schedule_str).
    """
    try:
        rem = int(remaining_sessions)
    except (ValueError, TypeError):
        rem = 0

    if rem <= 0:
        return 'Đã hết phí'

    if not start_from_date:
        start_dt = datetime.date.today()
    elif isinstance(start_from_date, str):
        parts = start_from_date.replace('/', '-').split('-')
        if len(parts[0]) == 4:
            start_dt = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            start_dt = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
    else:
        start_dt = start_from_date

    target_days = parse_schedule_days(schedule_str)
    off_set = set()
    if off_dates:
        for d in off_dates:
            try:
                p = d.replace('/', '-').split('-')
                if len(p[0]) == 4:
                    off_set.add(datetime.date(int(p[0]), int(p[1]), int(p[2])))
                else:
                    off_set.add(datetime.date(int(p[2]), int(p[1]), int(p[0])))
            except Exception:
                pass

    curr = start_dt
    matched = 0
    # Search forward up to 365 days
    for _ in range(365):
        if curr.weekday() in target_days:
            if curr not in off_set:
                matched += 1
                if matched == rem:
                    return curr.strftime('%d/%m/%Y')
        curr += datetime.timedelta(days=1)

    return curr.strftime('%d/%m/%Y')

# Unit testing
print("0 sessions remaining ->", calculate_fee_expiry_date(0, "MT5"))
print("5 sessions remaining in MT5 from 2026-08-12 ->", calculate_fee_expiry_date(5, "MT5", datetime.date(2026, 8, 12)))
