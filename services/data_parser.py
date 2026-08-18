"""
EVI Dashboard - Data Parser
Parse dữ liệu thô từ Google Sheets thành cấu trúc JSON chuẩn.
Cung cấp dữ liệu demo khi chưa kết nối Google Sheets.
"""

import logging
import re

logger = logging.getLogger(__name__)


def parse_percentage(value):
    """
    Parse chuỗi phần trăm kiểu Việt Nam (dùng dấu phẩy) thành float.
    Ví dụ: '50,00%' -> 50.0, '100,00%' -> 100.0
    """
    if not value or value == '#REF!':
        return 0.0
    try:
        cleaned = value.replace('%', '').replace(',', '.').strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0


def parse_number(value):
    """Parse chuỗi số, trả về 0 nếu không hợp lệ."""
    if not value or value == '#REF!':
        return 0
    try:
        cleaned = value.replace(',', '.').strip()
        return int(float(cleaned))
    except (ValueError, AttributeError):
        return 0


def parse_float_vn(value):
    """Parse số thực kiểu VN (dùng dấu phẩy) thành float."""
    if not value:
        return 0.0
    try:
        cleaned = value.replace(',', '.').strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0


class DataParser:
    """Parser cho dữ liệu từ Google Sheets."""

    def __init__(self, raw_data):
        """
        Args:
            raw_data: List of lists - dữ liệu thô từ sheet
        """
        self.raw_data = raw_data

    def parse_all(self):
        """Parse toàn bộ dữ liệu, trả về dict tổng hợp."""
        return {
            'renewal_monthly': self.parse_renewal_monthly(),
            'renewal_yearly': self.parse_renewal_yearly(),
            'classes': self.parse_class_list(),
            'acs_stats': self.parse_acs_stats(),
        }

    def parse_renewal_monthly(self):
        """
        Parse báo cáo tỉ lệ tái phí hàng tháng.
        Dữ liệu nằm ở cột A-F, lặp lại theo pattern:
        - Hàng header: 'Tháng:', [số tháng], 'Năm:', [năm]
        - Hàng tiêu đề cột: CM, Số HS đến hạn...
        - Các hàng dữ liệu CM
        - Hàng 'Tổng' (nếu thiếu sẽ tự cộng tổng)
        """
        results = []
        i = 0

        while i < len(self.raw_data):
            row = self.raw_data[i]

            if len(row) > 0 and row[0] == 'Tháng:':
                month = parse_number(row[1]) if len(row) > 1 else 0
                year = parse_number(row[3]) if len(row) > 3 else 0

                if month == 0 or year == 0:
                    i += 1
                    continue

                i += 1
                if i < len(self.raw_data):
                    i += 1

                staff_data = []
                total_data = None

                while i < len(self.raw_data):
                    row = self.raw_data[i]

                    if len(row) == 0 or (len(row) > 0 and row[0] == 'Tháng:'):
                        break

                    cm_name = row[0].strip() if len(row) > 0 else ''

                    due = parse_number(row[1]) if len(row) > 1 else 0
                    success = parse_number(row[2]) if len(row) > 2 else 0
                    pending = parse_number(row[3]) if len(row) > 3 else 0
                    failed = parse_number(row[4]) if len(row) > 4 else 0
                    rate = parse_percentage(row[5]) if len(row) > 5 else 0.0

                    if cm_name == 'Tổng':
                        total_data = {
                            'name': 'Tổng', 'due': due, 'success': success,
                            'pending': pending, 'failed': failed, 'rate': rate
                        }
                    elif cm_name and cm_name not in ['CM', '#REF!'] and (due > 0 or success > 0 or pending > 0 or failed > 0):
                        staff_data.append({
                            'name': cm_name, 'due': due, 'success': success,
                            'pending': pending, 'failed': failed, 'rate': rate
                        })

                    i += 1

                if staff_data:
                    # Auto calculate total if missing from sheet
                    if not total_data:
                        tot_due = sum(s['due'] for s in staff_data)
                        tot_success = sum(s['success'] for s in staff_data)
                        tot_pending = sum(s['pending'] for s in staff_data)
                        tot_failed = sum(s['failed'] for s in staff_data)
                        tot_rate = round((tot_success / tot_due * 100), 2) if tot_due > 0 else 0.0
                        total_data = {
                            'name': 'Tổng', 'due': tot_due, 'success': tot_success,
                            'pending': tot_pending, 'failed': tot_failed, 'rate': tot_rate
                        }

                    results.append({
                        'month': month,
                        'year': year,
                        'staff': staff_data,
                        'total': total_data,
                    })
            else:
                i += 1

        return results

    def parse_renewal_yearly(self):
        """
        Parse báo cáo tỉ lệ tái phí năm (cột I-V, dòng đầu).
        """
        result = {
            'year': 2025,
            'months': [],
            'total': None,
        }

        for i, row in enumerate(self.raw_data):
            if len(row) > 8 and row[8] == 'Tháng':
                month_labels = []
                for j in range(9, min(22, len(row))):
                    month_labels.append(row[j])

                if i + 1 < len(self.raw_data):
                    cases_row = self.raw_data[i + 1]
                    cases = [parse_number(cases_row[j]) for j in range(9, min(22, len(cases_row)))]

                if i + 2 < len(self.raw_data):
                    success_row = self.raw_data[i + 2]
                    successes = [parse_number(success_row[j]) for j in range(9, min(22, len(success_row)))]

                if i + 3 < len(self.raw_data):
                    rate_row = self.raw_data[i + 3]
                    rates = [parse_percentage(rate_row[j]) for j in range(9, min(22, len(rate_row)))]

                for idx, label in enumerate(month_labels):
                    if label and label != '2025':
                        result['months'].append({
                            'month': parse_number(label),
                            'cases': cases[idx] if idx < len(cases) else 0,
                            'success': successes[idx] if idx < len(successes) else 0,
                            'rate': rates[idx] if idx < len(rates) else 0.0,
                        })
                    elif label == '2025':
                        result['total'] = {
                            'cases': cases[idx] if idx < len(cases) else 0,
                            'success': successes[idx] if idx < len(successes) else 0,
                            'rate': rates[idx] if idx < len(rates) else 0.0,
                        }
                break

        return result

    def parse_class_list(self):
        """
        Parse danh sách lớp học (cột I-O, vùng dữ liệu lớp).
        """
        classes = []
        for i, row in enumerate(self.raw_data):
            if len(row) > 8 and row[8] == 'Lớp':
                j = i + 1
                while j < len(self.raw_data):
                    r = self.raw_data[j]
                    if len(r) <= 8 or not r[8] or r[8] == '':
                        break

                    class_name = r[8].strip()
                    if not class_name:
                        break

                    class_entry = {
                        'name': class_name,
                        'schedule': r[9].strip() if len(r) > 9 else '',
                        'room': r[10].strip() if len(r) > 10 else '',
                        'teacher': r[11].strip() if len(r) > 11 else '',
                        'cm': r[12].strip() if len(r) > 12 else '',
                        'ta': r[13].strip() if len(r) > 13 else '',
                        'students': parse_number(r[14]) if len(r) > 14 else 0,
                    }
                    classes.append(class_entry)
                    j += 1
                break

        return classes

    def parse_acs_stats(self):
        """
        Parse thống kê ACS theo CM (cột R-S).
        Returns:
            dict: {staff: [{name, score}], average, total_students}
        """
        result = {
            'staff': [],
            'average': 0.0,
            'total_students': 0,
        }

        for i, row in enumerate(self.raw_data):
            if len(row) > 18 and row[17] == 'CM' and row[18] == 'ACS':
                for j in range(i + 1, min(i + 15, len(self.raw_data))):
                    r = self.raw_data[j]
                    if len(r) <= 17:
                        continue

                    name = r[17].strip()
                    score_str = r[18].strip() if len(r) > 18 else ''

                    if not name:
                        continue

                    score = parse_float_vn(score_str)

                    if name == 'TB':
                        result['average'] = score
                    elif name == 'Tổng số HS':
                        result['total_students'] = parse_number(score_str)
                    elif name not in ['CM', 'ACS']:
                        result['staff'].append({
                            'name': name,
                            'score': score,
                        })

                break

        return result


def parse_homework_data(raw_rows):
    """
    Parse danh sách BTVN học sinh từ sheet BTVN ('Nhập KQ BVN' hoặc các tab khác).
    Cột: Ngày nhập, Mã học viên, Tên học viên, Tên tiếng Anh, Số điện thoại, Lớp, Giáo viên, Ca học, Điểm BVN, Tổng số câu
    """
    students = []
    if not raw_rows:
        return students

    for row in raw_rows:
        if len(row) < 4 or not any(row):
            continue

        # Check if row is a header or title row
        first_cell = str(row[0]).strip().upper()
        if 'MÃ HỌC VIÊN' in first_cell or 'BÁO CÁO' in first_cell or 'THÁNG' in first_cell and len(row) < 3:
            continue

        date_val = str(row[0]).strip() if len(row) > 0 else ''
        code = str(row[1]).strip() if len(row) > 1 else ''
        name = str(row[2]).strip() if len(row) > 2 else ''
        en_name = str(row[3]).strip() if len(row) > 3 else ''
        phone = str(row[4]).strip() if len(row) > 4 else ''
        class_name = str(row[5]).strip() if len(row) > 5 else ''
        teacher = str(row[6]).strip() if len(row) > 6 else ''
        schedule = str(row[7]).strip() if len(row) > 7 else ''
        score_raw = str(row[8]).strip() if len(row) > 8 else ''
        total_q = str(row[9]).strip() if len(row) > 9 else ''

        if code.startswith('EVI') or name or en_name:
            if name.upper() in ['TÊN HỌC VIÊN', 'MÃ HỌC VIÊN', 'TÊN']:
                continue

            status = 'Đã nộp'
            if not score_raw or score_raw == '0,0' or score_raw == '0' or score_raw == '':
                status = 'Chưa nộp BTVN'
            elif parse_float_vn(score_raw) < 5.0 and parse_float_vn(score_raw) > 0:
                status = 'Nộp muộn'

            students.append({
                'code': code if code.startswith('EVI') else (code or 'N/A'),
                'name': name,
                'english_name': en_name,
                'phone_class': class_name or phone,
                'phone': phone,
                'class_name': class_name,
                'teacher': teacher,
                'schedule': schedule,
                'date': date_val,
                'score': score_raw,
                'score_num': parse_float_vn(score_raw),
                'total_questions': total_q,
                'status': status,
            })

    return students


def parse_grades_from_worksheet(rows, sheet_title="SUN S.7"):
    """
    Parse điểm số học sinh từ một worksheet cụ thể, tự động bóc tách tất cả các Unit/Bài Test nằm theo chiều ngang.
    """
    if not rows or len(rows) < 5:
        return []

    class_name = sheet_title
    course_name = "KID'S BOX"

    # Header inspection in top rows
    for r in rows[:4]:
        for cell in r:
            cell_str = str(cell)
            if 'LỚP:' in cell_str:
                parts = cell_str.split('LỚP:')
                if len(parts) > 1:
                    c_found = parts[1].split('TÊN')[0].strip()
                    if c_found:
                        class_name = c_found
            if 'CHƯƠNG TRÌNH' in cell_str:
                parts = cell_str.split('CHƯƠNG TRÌNH')
                if len(parts) > 1 and parts[1].strip():
                    course_name = parts[1].strip()

    unit_row = rows[3] if len(rows) > 3 else []
    skill_row = rows[4] if len(rows) > 4 else []

    # Detect horizontal test blocks
    test_blocks = []
    current_block = None

    for col_idx in range(3, max(len(unit_row), len(skill_row))):
        u_header = unit_row[col_idx].strip() if col_idx < len(unit_row) else ''
        s_header = skill_row[col_idx].strip() if col_idx < len(skill_row) else ''

        if u_header:
            current_block = {
                'test_name': u_header,
                'start_col': col_idx,
                'listening_col': -1, 'listening_max': 10,
                'reading_col': -1, 'reading_max': 20,
                'speaking_col': -1, 'speaking_max': 10,
                'comment_col': -1
            }
            test_blocks.append(current_block)

        if not current_block and test_blocks:
            current_block = test_blocks[-1]

        if current_block:
            s_upper = s_header.upper()
            if 'NGHE' in s_upper:
                current_block['listening_col'] = col_idx
                if '/15' in s_header: current_block['listening_max'] = 15
                elif '/20' in s_header: current_block['listening_max'] = 20
                elif '/25' in s_header: current_block['listening_max'] = 25
                elif '/10' in s_header: current_block['listening_max'] = 10
            elif 'ĐỌC' in s_upper or 'VIẾT' in s_upper:
                current_block['reading_col'] = col_idx
                if '/12' in s_header: current_block['reading_max'] = 12
                elif '/20' in s_header: current_block['reading_max'] = 20
                elif '/35' in s_header: current_block['reading_max'] = 35
                elif '/22' in s_header: current_block['reading_max'] = 22
            elif 'NÓI' in s_upper:
                current_block['speaking_col'] = col_idx
                if '/26' in s_header: current_block['speaking_max'] = 26
            elif 'NHẬN XÉT' in s_upper:
                current_block['comment_col'] = col_idx

    # If no explicit Unit headers found in Row 4, fallback to single block
    if not test_blocks:
        test_blocks = [{
            'test_name': 'TEST UNIT',
            'start_col': 3,
            'listening_col': 3, 'listening_max': 10,
            'reading_col': 4, 'reading_max': 12,
            'speaking_col': 5, 'speaking_max': 10,
            'comment_col': 6
        }]

    all_grades = []
    header_idx = -1
    for idx, r in enumerate(rows):
        row_str = ' '.join(str(c) for c in r).upper()
        if 'STT' in row_str or 'ENGLISH NAME' in row_str or ('TÊN' in row_str and 'KỸ NĂNG' not in row_str):
            header_idx = idx
            break

    start_r = (header_idx + 1) if header_idx != -1 else 5
    for r in rows[start_r:]:
        if len(r) < 3 or not any(r):
            continue

        stt = str(r[0]).strip() if len(r) > 0 else ''
        name = str(r[1]).strip() if len(r) > 1 else ''
        en_name = str(r[2]).strip() if len(r) > 2 else ''

        if not name and not en_name:
            continue
        if name.upper() in ['STT', 'TÊN', 'CHƯƠNG TRÌNH', 'LỚP']:
            continue

        displayName = name or en_name

        for tb in test_blocks:
            listening = parse_float_vn(r[tb['listening_col']]) if tb['listening_col'] != -1 and tb['listening_col'] < len(r) and r[tb['listening_col']].strip() else None
            reading_writing = parse_float_vn(r[tb['reading_col']]) if tb['reading_col'] != -1 and tb['reading_col'] < len(r) and r[tb['reading_col']].strip() else None
            speaking = parse_float_vn(r[tb['speaking_col']]) if tb['speaking_col'] != -1 and tb['speaking_col'] < len(r) and r[tb['speaking_col']].strip() else None
            comment = str(r[tb['comment_col']]).strip() if tb['comment_col'] != -1 and tb['comment_col'] < len(r) else ''

            if listening is None and reading_writing is None and speaking is None and not comment:
                continue

            total_score = 0
            max_score = 0
            if listening is not None:
                total_score += listening
                max_score += tb['listening_max']
            if reading_writing is not None:
                total_score += reading_writing
                max_score += tb['reading_max']
            if speaking is not None:
                total_score += speaking
                max_score += tb['speaking_max']

            all_grades.append({
                'stt': stt,
                'class_name': class_name,
                'course': course_name,
                'test_name': tb['test_name'],
                'name': displayName,
                'english_name': en_name,
                'listening': listening,
                'listening_max': tb['listening_max'],
                'reading_writing': reading_writing,
                'reading_writing_max': tb['reading_max'],
                'speaking': speaking,
                'speaking_max': tb['speaking_max'],
                'comment': comment,
                'total_score': total_score,
                'max_score': max_score or 22,
            })

    return all_grades


def parse_grades_data(raw_rows, class_name="SUN S.7"):
    """
    Parse điểm số học sinh cho single worksheet (compatibility wrapper).
    """
    return parse_grades_from_worksheet(raw_rows, class_name)


def get_demo_data():
    """
    Trả về dữ liệu demo khi chưa kết nối Google Sheets.
    Dữ liệu dựa trên cấu trúc thực tế từ sheet.
    """
    return {
        'renewal_monthly': [
            {
                'month': 11, 'year': 2025,
                'staff': [
                    {'name': 'HaTM', 'due': 4, 'success': 2, 'pending': 0, 'failed': 2, 'rate': 50.0},
                    {'name': 'DiuNHP', 'due': 4, 'success': 1, 'pending': 0, 'failed': 3, 'rate': 25.0},
                    {'name': 'LinhNN', 'due': 6, 'success': 4, 'pending': 0, 'failed': 2, 'rate': 66.67},
                ],
                'total': {'name': 'Tổng', 'due': 14, 'success': 7, 'pending': 0, 'failed': 7, 'rate': 50.0},
            },
            {
                'month': 12, 'year': 2025,
                'staff': [
                    {'name': 'HaTM', 'due': 7, 'success': 4, 'pending': 1, 'failed': 2, 'rate': 57.14},
                    {'name': 'LinhNN', 'due': 6, 'success': 4, 'pending': 1, 'failed': 0, 'rate': 66.67},
                    {'name': 'DiuNHP', 'due': 8, 'success': 4, 'pending': 3, 'failed': 1, 'rate': 50.0},
                ],
                'total': {'name': 'Tổng', 'due': 21, 'success': 12, 'pending': 5, 'failed': 3, 'rate': 57.14},
            },
            {
                'month': 1, 'year': 2026,
                'staff': [
                    {'name': 'LinhNN', 'due': 3, 'success': 0, 'pending': 2, 'failed': 4, 'rate': 0.0},
                    {'name': 'HaTM', 'due': 2, 'success': 0, 'pending': 0, 'failed': 2, 'rate': 0.0},
                    {'name': 'DiuNHP', 'due': 3, 'success': 1, 'pending': 0, 'failed': 1, 'rate': 33.33},
                ],
                'total': {'name': 'Tổng', 'due': 8, 'success': 1, 'pending': 2, 'failed': 7, 'rate': 12.5},
            },
            {
                'month': 2, 'year': 2026,
                'staff': [
                    {'name': 'HaTM', 'due': 5, 'success': 3, 'pending': 1, 'failed': 1, 'rate': 60.0},
                    {'name': 'DiuNHP', 'due': 2, 'success': 0, 'pending': 0, 'failed': 2, 'rate': 0.0},
                    {'name': 'LinhNN', 'due': 2, 'success': 1, 'pending': 0, 'failed': 1, 'rate': 50.0},
                ],
                'total': {'name': 'Tổng', 'due': 9, 'success': 4, 'pending': 1, 'failed': 4, 'rate': 44.44},
            },
            {
                'month': 3, 'year': 2026,
                'staff': [
                    {'name': 'LinhNN', 'due': 2, 'success': 2, 'pending': 0, 'failed': 0, 'rate': 100.0},
                    {'name': 'HaTM', 'due': 3, 'success': 3, 'pending': 0, 'failed': 0, 'rate': 100.0},
                    {'name': 'DiuNHP', 'due': 1, 'success': 1, 'pending': 0, 'failed': 0, 'rate': 100.0},
                ],
                'total': {'name': 'Tổng', 'due': 6, 'success': 6, 'pending': 0, 'failed': 0, 'rate': 100.0},
            },
            {
                'month': 4, 'year': 2026,
                'staff': [
                    {'name': 'LinhNN', 'due': 2, 'success': 2, 'pending': 0, 'failed': 0, 'rate': 100.0},
                    {'name': 'HaTM', 'due': 3, 'success': 3, 'pending': 0, 'failed': 0, 'rate': 100.0},
                    {'name': 'DiuNHP', 'due': 1, 'success': 1, 'pending': 0, 'failed': 0, 'rate': 100.0},
                ],
                'total': {'name': 'Tổng', 'due': 6, 'success': 6, 'pending': 0, 'failed': 0, 'rate': 100.0},
            },
            {
                'month': 6, 'year': 2026,
                'staff': [
                    {'name': 'AnhPTT', 'due': 0, 'success': 0, 'pending': 0, 'failed': 0, 'rate': 0.0},
                    {'name': 'Vân Anh', 'due': 1, 'success': 1, 'pending': 0, 'failed': 0, 'rate': 100.0},
                    {'name': 'NgọcCM', 'due': 1, 'success': 1, 'pending': 0, 'failed': 0, 'rate': 100.0},
                ],
                'total': {'name': 'Tổng', 'due': 2, 'success': 2, 'pending': 0, 'failed': 0, 'rate': 100.0},
            },
            {
                'month': 7, 'year': 2026,
                'staff': [
                    {'name': 'AnhPTT', 'due': 0, 'success': 0, 'pending': 0, 'failed': 0, 'rate': 0.0},
                    {'name': 'Vân Anh', 'due': 2, 'success': 1, 'pending': 0, 'failed': 1, 'rate': 50.0},
                    {'name': 'NgọcCM', 'due': 7, 'success': 0, 'pending': 0, 'failed': 7, 'rate': 0.0},
                ],
                'total': {'name': 'Tổng', 'due': 9, 'success': 1, 'pending': 0, 'failed': 8, 'rate': 11.11},
            },
            {
                'month': 8, 'year': 2026,
                'staff': [
                    {'name': 'AnhPTT', 'due': 3, 'success': 1, 'pending': 1, 'failed': 1, 'rate': 33.33},
                    {'name': 'Vân Anh', 'due': 13, 'success': 4, 'pending': 5, 'failed': 4, 'rate': 30.77},
                    {'name': 'NgọcCM', 'due': 5, 'success': 2, 'pending': 3, 'failed': 0, 'rate': 40.0},
                ],
                'total': {'name': 'Tổng', 'due': 21, 'success': 7, 'pending': 9, 'failed': 5, 'rate': 33.33},
            },
            {
                'month': 9, 'year': 2026,
                'staff': [
                    {'name': 'AnhPTT', 'due': 3, 'success': 0, 'pending': 3, 'failed': 0, 'rate': 0.0},
                    {'name': 'Vân Anh', 'due': 7, 'success': 0, 'pending': 1, 'failed': 0, 'rate': 0.0},
                    {'name': 'NgọcCM', 'due': 1, 'success': 0, 'pending': 1, 'failed': 0, 'rate': 0.0},
                ],
                'total': {'name': 'Tổng', 'due': 11, 'success': 0, 'pending': 5, 'failed': 0, 'rate': 0.0},
            },
        ],
        'renewal_yearly': {
            'year': 2025,
            'months': [
                {'month': i, 'cases': 0, 'success': 0, 'rate': 0.0} for i in range(1, 10)
            ] + [
                {'month': 10, 'cases': 4, 'success': 0, 'rate': 0.0},
                {'month': 11, 'cases': 6, 'success': 0, 'rate': 0.0},
                {'month': 12, 'cases': 9, 'success': 0, 'rate': 0.0},
            ],
            'total': {'cases': 19, 'success': 2, 'rate': 10.53},
        },
        'classes': [
            {'name': 'Galax 1.3', 'schedule': 'MT5', 'room': 'Mars', 'teacher': 'Jacob', 'cm': 'Vân Anh', 'ta': '', 'students': 6},
            {'name': 'Moon 5.2', 'schedule': 'MT5', 'room': 'Mercury', 'teacher': 'Andrew', 'cm': 'AnhPTT', 'ta': 'Giang', 'students': 10},
            {'name': 'GALAX 3.2', 'schedule': 'MT5', 'room': 'Jupiter', 'teacher': '', 'cm': 'AnhPTT', 'ta': '', 'students': 6},
            {'name': 'Sun 2.4', 'schedule': 'MT5', 'room': 'Uranus', 'teacher': 'Miguel', 'cm': 'NgọcCM', 'ta': '', 'students': 11},
            {'name': 'Sun 4.2', 'schedule': 'MT6', 'room': 'Mars', 'teacher': 'Miguel', 'cm': 'NgọcCM', 'ta': '', 'students': 4},
            {'name': 'Sun 1.5', 'schedule': '', 'room': '', 'teacher': 'Nghỉ hè đến tháng 8', 'cm': 'NgọcCM', 'ta': '', 'students': 0},
            {'name': 'Sun 5.1', 'schedule': '', 'room': '', 'teacher': 'Nghỉ hè', 'cm': 'NgọcCM', 'ta': '', 'students': 2},
            {'name': 'Moon 1.1', 'schedule': 'MT6', 'room': 'Jupiter', 'teacher': 'Andrew', 'cm': 'AnhPTT', 'ta': 'Giang', 'students': 6},
            {'name': 'Sun 2.2', 'schedule': 'TF5', 'room': 'Mercury', 'teacher': 'Jacob', 'cm': 'Vân Anh', 'ta': '', 'students': 13},
            {'name': 'Galax 1.4', 'schedule': 'TF5', 'room': 'Mars', 'teacher': 'Andrew', 'cm': 'Vân Anh', 'ta': '', 'students': 10},
            {'name': 'Sun 4.3', 'schedule': 'TF5', 'room': 'Uranus', 'teacher': 'Thomas (cover)', 'cm': 'NgọcCM', 'ta': '', 'students': 6},
            {'name': 'Sun 3.5', 'schedule': 'TF5', 'room': 'Jupiter', 'teacher': 'Miguel', 'cm': 'NgọcCM', 'ta': '', 'students': 9},
            {'name': 'Galax 3.1', 'schedule': 'TF6', 'room': 'Mars', 'teacher': 'Jacob', 'cm': 'Vân Anh', 'ta': '', 'students': 6},
            {'name': 'Sun 4.4', 'schedule': 'TF6', 'room': 'Uranus', 'teacher': 'Andrew', 'cm': 'NgọcCM', 'ta': '', 'students': 10},
            {'name': 'Sun S.7', 'schedule': 'TF6', 'room': 'Mercury', 'teacher': 'Miguel', 'cm': 'Vân Anh', 'ta': '', 'students': 9},
            {'name': 'Sun 1.4', 'schedule': 'TF6', 'room': 'Jupiter', 'teacher': 'Thomas (cover)', 'cm': 'NgọcCM', 'ta': '', 'students': 8},
            {'name': 'Galax 1.5', 'schedule': 'WS5', 'room': 'Uranus', 'teacher': 'Jacob', 'cm': 'Vân Anh', 'ta': '', 'students': 9},
            {'name': 'Moon 3.1', 'schedule': 'WS5', 'room': 'Mercury', 'teacher': 'Andrew', 'cm': 'AnhPTT', 'ta': 'Duyên', 'students': 11},
            {'name': 'Sun 1.6', 'schedule': 'WS5', 'room': 'Mars', 'teacher': 'Miguel', 'cm': 'AnhPTT', 'ta': 'Giang', 'students': 10},
            {'name': 'Sun 2.3', 'schedule': '', 'room': '', 'teacher': 'Nghỉ hè đến tháng 8', 'cm': 'Vân Anh', 'ta': '', 'students': 0},
            {'name': 'Sun 2.1', 'schedule': 'WS6', 'room': 'Uranus', 'teacher': 'Miguel', 'cm': 'AnhPTT', 'ta': 'Giang', 'students': 11},
            {'name': 'Moon 5.1', 'schedule': 'WS6', 'room': 'Mercury', 'teacher': 'Andrew', 'cm': 'Vân Anh', 'ta': 'Duyên', 'students': 7},
        ],
        'acs_stats': {
            'staff': [
                {'name': 'Vân Anh', 'score': 7.50},
                {'name': 'AnhPTT', 'score': 9.00},
                {'name': 'NgọcCM', 'score': 6.25},
            ],
            'average': 7.58,
            'total_students': 207,
        },
        'homework': [
            {'code': 'EVI232', 'name': 'Phạm Minh Vũ', 'english_name': 'Jack', 'phone_class': 'Sun S.7', 'date': '2026-03-15', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI405', 'name': 'Nguyễn Triệu Minh Khánh', 'english_name': 'Lisa 2', 'phone_class': 'Moon 5.2', 'date': '2026-03-15', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI056', 'name': 'Nguyễn Ngọc Huyền', 'english_name': 'Amy', 'phone_class': 'Sun 2.4', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI193', 'name': 'Phạm Hồng Đức', 'english_name': 'Alex', 'phone_class': 'Sun 2.2', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI255', 'name': 'Đỗ Nguyên Thảo', 'english_name': 'Mila', 'phone_class': 'Galax 1.3', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI313', 'name': 'Phạm Bảo Anh', 'english_name': 'Moon', 'phone_class': 'Sun S.7', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI275', 'name': 'Hoàng Hải Anh', 'english_name': 'Aaron', 'phone_class': 'Moon 1.1', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI395', 'name': 'Phạm Minh Châu', 'english_name': 'Jennie', 'phone_class': 'Sun 4.2', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI121', 'name': 'Ngô Gia Nam', 'english_name': 'Milton', 'phone_class': 'Sun 3.5', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI399', 'name': 'Nguyễn Bảo Nam', 'english_name': 'Robert', 'phone_class': 'Sun S.7', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI409', 'name': 'Trần Đình Nam', 'english_name': 'Max', 'phone_class': 'Galax 1.4', 'date': '', 'status': 'Chưa nộp BTVN'},
            {'code': 'EVI422', 'name': 'Lê Thị Ngân Hà', 'english_name': 'Anna', 'phone_class': 'Moon 5.1', 'date': '2026-03-20', 'status': 'Nộp muộn'},
            {'code': 'EVI390', 'name': 'Nguyễn Trúc Lâm Phương', 'english_name': 'Molly', 'phone_class': 'Sun S.7', 'date': '2026-03-22', 'status': 'Nộp muộn'},
            {'code': 'EVI391', 'name': 'Kiều Gia Bình', 'english_name': 'Jack', 'phone_class': 'Sun 2.1', 'date': '2026-03-22', 'status': 'Nộp muộn'},
            {'code': 'EVI116', 'name': 'Tạ Chí Thành', 'english_name': 'Pony', 'phone_class': 'Moon 3.1', 'date': '2026-03-22', 'status': 'Nộp muộn'},
            {'code': 'EVI167', 'name': 'Trần Trâm Anh', 'english_name': 'Rose', 'phone_class': 'Galax 3.1', 'date': '2026-03-25', 'status': 'Đã nộp'},
            {'code': 'EVI233', 'name': 'Nguyễn Kim Bảo An', 'english_name': 'Anna', 'phone_class': 'Sun 4.4', 'date': '2026-03-25', 'status': 'Đã nộp'},
            {'code': 'EVI358', 'name': 'Trương Khánh An', 'english_name': 'An', 'phone_class': 'Sun 1.6', 'date': '2026-03-25', 'status': 'Đã nộp'},
            {'code': 'EVI381', 'name': 'Nguyễn Huy Bách', 'english_name': 'Ben', 'phone_class': 'Galax 1.5', 'date': '2026-03-25', 'status': 'Đã nộp'},
        ],
        'grades': [
            {'stt': '1', 'class_name': 'SUN S.7', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Nguyễn Hoàng Minh Quân', 'english_name': 'Ronald', 'listening': 7, 'listening_max': 10, 'reading_writing': 11, 'reading_writing_max': 12, 'speaking': 8, 'total_score': 18, 'max_score': 22},
            {'stt': '2', 'class_name': 'SUN S.7', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Trịnh Minh Tiến', 'english_name': 'Bee', 'listening': 10, 'listening_max': 10, 'reading_writing': 10, 'reading_writing_max': 12, 'speaking': 9, 'total_score': 20, 'max_score': 22},
            {'stt': '3', 'class_name': 'SUN S.7', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Nguyễn Nam Khánh', 'english_name': 'Bin', 'listening': 6, 'listening_max': 10, 'reading_writing': 10, 'reading_writing_max': 12, 'speaking': 7, 'total_score': 16, 'max_score': 22},
            {'stt': '4', 'class_name': 'SUN S.7', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Nguyễn Nhật Khuê', 'english_name': 'Batman', 'listening': 10, 'listening_max': 10, 'reading_writing': 10, 'reading_writing_max': 12, 'speaking': 9, 'total_score': 20, 'max_score': 22},
            {'stt': '5', 'class_name': 'SUN S.7', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Nguyễn Phúc Lâm', 'english_name': 'Ben', 'listening': 10, 'listening_max': 10, 'reading_writing': 11, 'reading_writing_max': 12, 'speaking': 10, 'total_score': 21, 'max_score': 22},
            {'stt': '6', 'class_name': 'SUN S.7', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Thái Sơn', 'english_name': 'Lucas', 'listening': 7, 'listening_max': 10, 'reading_writing': 5, 'reading_writing_max': 12, 'speaking': 6, 'total_score': 12, 'max_score': 22},
            {'stt': '7', 'class_name': 'SUN S.7', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Nguyễn Tú Anh', 'english_name': 'Kuromi', 'listening': 10, 'listening_max': 10, 'reading_writing': 12, 'reading_writing_max': 12, 'speaking': 10, 'total_score': 22, 'max_score': 22},
            {'stt': '8', 'class_name': 'Moon 5.2', 'course': "SUPER MINDS", 'test_name': 'TEST UNIT 3', 'name': 'Nguyễn Triệu Minh Khánh', 'english_name': 'Lisa 2', 'listening': 9, 'listening_max': 10, 'reading_writing': 11, 'reading_writing_max': 12, 'speaking': 9, 'total_score': 20, 'max_score': 22},
            {'stt': '9', 'class_name': 'Sun 2.4', 'course': "KID'S BOX", 'test_name': 'TEST UNIT 2', 'name': 'Nguyễn Ngọc Huyền', 'english_name': 'Amy', 'listening': 8, 'listening_max': 10, 'reading_writing': 9, 'reading_writing_max': 12, 'speaking': 8, 'total_score': 17, 'max_score': 22},
            {'stt': '10', 'class_name': 'Galax 1.3', 'course': "THINK 1", 'test_name': 'FINAL TEST', 'name': 'Phạm Minh Vũ', 'english_name': 'Jack', 'listening': 9, 'listening_max': 10, 'reading_writing': 10, 'reading_writing_max': 12, 'speaking': 9, 'total_score': 19, 'max_score': 22},
        ],
    }


def parse_students_master(s1_spreadsheet, s2_spreadsheet=None, s3_spreadsheet=None):
    """
    Parse và tổng hợp danh sách học sinh (437+ HS) từ cả 3 Google Sheets:
    - DATA HS FULL PHÍ (Sheet 1): Thông tin cá nhân, Phụ huynh, SĐT, Ngày sinh, Tình trạng
    - Data DSHS (Sheet 2/3): Lớp học, Ca học, GV, CM, TA, Tổng số buổi, Số buổi còn lại
    - Tái phí (Sheet 1): Ngày hết phí, Tháng hết phí
    """
    students_dict = {}

    # 1. Read 'DATA HS FULL PHÍ' from Sheet 1
    if s1_spreadsheet:
        try:
            ws_full = s1_spreadsheet.worksheet('DATA HS FULL PHÍ')
            rows = ws_full.get_all_values()
            if len(rows) > 1:
                for r in rows[1:]:
                    if len(r) < 3 or not r[1].strip():
                        continue
                    code = r[1].strip().upper()
                    name = r[2].strip()
                    en_name = r[3].strip() if len(r) > 3 else ''
                    dob = r[4].strip() if len(r) > 4 else ''
                    parent = r[5].strip() if len(r) > 5 else ''
                    phone = r[6].strip() if len(r) > 6 else ''
                    address = r[7].strip() if len(r) > 7 else ''
                    status = r[8].strip() if len(r) > 8 else 'Đang học'

                    students_dict[code] = {
                        'code': code,
                        'name': name,
                        'english_name': en_name,
                        'dob': dob,
                        'parent_name': parent,
                        'phone': phone,
                        'address': address,
                        'status': status or 'Đang học',
                        'class_name': '',
                        'schedule': '',
                        'teacher': '',
                        'cm': '',
                        'ta': '',
                        'total_sessions': 0,
                        'remaining_sessions': 0,
                        'expiry_date': '',
                        'expiry_month': '',
                    }
        except Exception as e:
            logger.warning(f"Could not parse DATA HS FULL PHÍ: {e}")

    # 2. Read 'Data DSHS' from Sheet 2 or Sheet 3
    for sp in [s2_spreadsheet, s3_spreadsheet]:
        if not sp: continue
        try:
            ws_dshs = sp.worksheet('Data DSHS')
            rows = ws_dshs.get_all_values()
            if len(rows) > 3:
                for r in rows[3:]:
                    if len(r) < 2 or not r[0].strip():
                        continue
                    code = r[0].strip().upper()
                    name = r[1].strip() if len(r) > 1 else ''
                    en_name = r[2].strip() if len(r) > 2 else ''
                    parent = r[3].strip() if len(r) > 3 else ''
                    phone = r[4].strip() if len(r) > 4 else ''
                    c_name = r[5].strip() if len(r) > 5 else ''
                    sched = r[6].strip() if len(r) > 6 else ''
                    gv = r[7].strip() if len(r) > 7 else ''
                    cm = r[8].strip() if len(r) > 8 else ''
                    ta = r[9].strip() if len(r) > 9 else ''
                    tot_sess = parse_number(r[10]) if len(r) > 10 else 0
                    rem_sess = parse_number(r[11]) if len(r) > 11 else 0

                    if code not in students_dict:
                        students_dict[code] = {
                            'code': code,
                            'name': name,
                            'english_name': en_name,
                            'dob': '',
                            'parent_name': parent,
                            'phone': phone,
                            'address': '',
                            'status': 'Đang học',
                        }

                    st = students_dict[code]
                    if name and not st.get('name'): st['name'] = name
                    if en_name: st['english_name'] = en_name
                    if parent and not st.get('parent_name'): st['parent_name'] = parent
                    if phone and not st.get('phone'): st['phone'] = phone
                    if c_name:
                        c_lower = c_name.lower()
                        if 'bảo lưu' in c_lower:
                            st['status'] = 'Bảo lưu'
                            if st.get('class_name') and 'bảo lưu' not in st['class_name'].lower():
                                st['last_class_name'] = st['class_name']
                            st['class_name'] = ''
                        elif 'đã nghỉ' in c_lower or c_name in ['Nghỉ', 'Đã Nghỉ', 'Đã nghỉ', 'Nghỉ học']:
                            st['status'] = 'Đã nghỉ'
                            if st.get('class_name') and 'nghỉ' not in st['class_name'].lower():
                                st['last_class_name'] = st['class_name']
                            st['class_name'] = ''
                        elif c_name != '—':
                            st['status'] = 'Đang học'
                            st['class_name'] = c_name

                    if sched: st['schedule'] = sched
                    if gv: st['teacher'] = gv
                    if cm: st['cm'] = cm
                    is_short_term = any(k in c_name.lower() for k in ['khóa', 'khoa', 'debate', 'speaking', 'ôn thi', 'on thi', 'ngắn hạn', 'ngan han', 'bổ trợ', 'bo tro'])
                    if not is_short_term:
                        if tot_sess: st['total_sessions'] = tot_sess
                        if rem_sess: st['remaining_sessions'] = rem_sess
                    elif not st.get('total_sessions') or st.get('total_sessions') == 0:
                        if tot_sess: st['total_sessions'] = tot_sess
                        if rem_sess: st['remaining_sessions'] = rem_sess
        except Exception as e:
            logger.warning(f"Could not parse Data DSHS: {e}")

    # 3. Read 'Tái phí' from Sheet 1
    if s1_spreadsheet:
        try:
            ws_tai = s1_spreadsheet.worksheet('Tái phí')
            rows = ws_tai.get_all_values()
            if len(rows) > 1:
                for r in rows[1:]:
                    if len(r) < 2 or not r[0].strip():
                        continue
                    code = r[0].strip().upper()
                    exp_date = r[10].strip() if len(r) > 10 else ''
                    exp_month = r[11].strip() if len(r) > 11 else ''

                    if code in students_dict:
                        st = students_dict[code]
                        if exp_date and exp_date != '#VALUE!': st['expiry_date'] = exp_date
                        if exp_month and exp_month != '#VALUE!': st['expiry_month'] = exp_month
        except Exception as e:
            logger.warning(f"Could not parse Tái phí: {e}")

    return list(students_dict.values())

