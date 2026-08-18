import datetime
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Shift code mapping to Python weekday numbers (Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6)
SHIFT_WEEKDAYS = {
    'MT5': [0, 3],  # Mon, Thu
    'MT6': [0, 4],  # Mon, Fri
    'TF5': [1, 3],  # Tue, Thu
    'TF6': [1, 4],  # Tue, Fri
    'WS5': [2, 5],  # Wed, Sat
    'WS6': [2, 6],  # Wed, Sun
}


def calculate_expiry_date(remaining_sessions, shift_code, start_date=None):
    if not remaining_sessions or remaining_sessions <= 0:
        return None, None, None

    if start_date is None:
        start_date = datetime.date.today()

    shift = (shift_code or '').strip().upper()
    active_days = SHIFT_WEEKDAYS.get(shift, [1, 4])  # Default Tue/Fri if unknown

    curr = start_date
    sessions_left = int(remaining_sessions)

    # Step forward day by day
    while sessions_left > 0:
        curr += datetime.timedelta(days=1)
        if curr.weekday() in active_days:
            sessions_left -= 1

    formatted_date = curr.strftime('%d/%m/%Y')
    return formatted_date, curr.month, curr.year


# Test calculation
print("Test calculation for 10 sessions remaining, shift TF6, starting today:")
exp_date, m, y = calculate_expiry_date(10, 'TF6')
print(f"Result: Date={exp_date}, Month={m}, Year={y}")

print(
    "\nTest calculation for 25 sessions remaining, shift MT5, starting today:"
)
exp_date, m, y = calculate_expiry_date(25, 'MT5')
print(f"Result: Date={exp_date}, Month={m}, Year={y}")
