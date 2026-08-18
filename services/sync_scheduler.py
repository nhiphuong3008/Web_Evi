"""
EVI Dashboard - Background Sync Scheduler
Chạy ngầm tự động quét dữ liệu từ các nguồn Google Sheets 1 tiếng/lần.
Cơ chế Incremental Sync (UPSERT):
- Chỉ thêm mới hoặc cập nhật thông tin khác biệt.
- TUYỆT ĐỐI KHÔNG XÓA hay GHI ĐÈ dữ liệu nhập thủ công từ Web (Điểm danh, Nhật ký CM, Tái phí...).
"""

import threading
import time
import datetime
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database.db_manager import db_session
from database.models import (
    Student, ClassMaster, HomeworkRecord, UnitGrade, ClassSchedule
)
from services.google_sheets import GoogleSheetsService
from services.data_parser import parse_float_vn, parse_homework_data, parse_grades_from_worksheet

logger = logging.getLogger(__name__)

# Global sync state
_sync_state = {
    'last_sync_time': None,
    'last_sync_status': 'Chưa chạy',
    'last_sync_message': '',
    'is_syncing': False,
    'sync_count': 0,
    'stats': {}
}
_sync_lock = threading.Lock()
_timer_thread = None
_stop_event = threading.Event()


def get_sync_status():
    """Lấy trạng thái đồng bộ hiện tại."""
    with _sync_lock:
        return dict(_sync_state)


def safe_get_worksheet(sp, title_or_idx, retries=2):
    """Lấy worksheet an toàn từ Spreadsheet."""
    for attempt in range(retries):
        try:
            if isinstance(title_or_idx, str):
                try:
                    return sp.worksheet(title_or_idx)
                except Exception:
                    target_lower = title_or_idx.lower()
                    for w in sp.worksheets():
                        if target_lower in w.title.lower():
                            return w
                    return None
            else:
                return sp.worksheets()[title_or_idx]
        except Exception as e:
            if '429' in str(e):
                time.sleep((attempt + 1) * 3)
            else:
                logger.warning(f"Could not load worksheet {title_or_idx}: {e}")
                return None
    return None


def run_incremental_sync():
    """
    Thực hiện quét và đồng bộ tăng cường (UPSERT) từ Google Sheets về SQLite CSDL.
    Không xóa bảng CSDL cũ!
    """
    global _sync_state
    with _sync_lock:
        if _sync_state['is_syncing']:
            logger.info("⏳ Sync đang chạy trong nền, bỏ qua lượt gọi trùng...")
            return False, "Đồng bộ đang diễn ra..."
        _sync_state['is_syncing'] = True
        _sync_state['last_sync_status'] = 'Đang đồng bộ...'

    logger.info("🔄 [Background Sync] Bắt đầu quét Google Sheets ➔ CSDL SQLite...")
    start_t = time.time()
    cfg = config.get_config()

    try:
        service = GoogleSheetsService(cfg.GOOGLE_SHEETS_CREDENTIALS_FILE, cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
        if not service.connect():
            msg = "Không thể kết nối Google Sheets API (thiếu credentials hoặc không có mạng)."
            logger.warning(f"⚠️ [Background Sync] {msg}")
            with _sync_lock:
                _sync_state['is_syncing'] = False
                _sync_state['last_sync_status'] = 'Thất bại'
                _sync_state['last_sync_message'] = msg
            return False, msg

        session = db_session()

        # Connect spreadsheets
        s1 = service.client.open_by_key(cfg.GOOGLE_SHEETS_SPREADSHEET_ID)
        time.sleep(0.5)
        s2 = service.client.open_by_key(cfg.GOOGLE_SHEETS_BTVN_ID)
        time.sleep(0.5)
        s4 = service.client.open_by_key(cfg.GOOGLE_SHEETS_NEW_GRADES_ID) if hasattr(cfg, 'GOOGLE_SHEETS_NEW_GRADES_ID') else None
        time.sleep(0.5)

        # Cache existing students
        existing_students = {s.code: s for s in session.query(Student).all() if s.code}
        student_name_map = {}
        for code, st in existing_students.items():
            if st.full_name:
                student_name_map[st.full_name.strip().lower()] = code

        new_st_count = 0
        updated_st_count = 0

        # STEP 1: Sync Master Students from Sheet 1 'DATA HS FULL PHÍ'
        ws_master = safe_get_worksheet(s1, 'DATA HS FULL PHÍ')
        if ws_master:
            master_rows = ws_master.get_all_values()
            for r in master_rows[1:]:
                if len(r) > 1 and r[1].strip() and r[1].strip().startswith('EVI'):
                    code = r[1].strip().upper()
                    name = r[2].strip()
                    en_name = r[3].strip() if len(r) > 3 else ''
                    dob = r[4].strip() if len(r) > 4 else ''
                    parent = r[5].strip() if len(r) > 5 else ''
                    phone = r[6].strip() if len(r) > 6 else ''
                    addr = r[7].strip() if len(r) > 7 else ''

                    if code in existing_students:
                        st = existing_students[code]
                        # UPSERT: Update basic fields if not populated or changed in Sheet
                        if name and not st.full_name: st.full_name = name
                        if en_name and not st.english_name: st.english_name = en_name
                        if dob and not st.dob: st.dob = dob
                        if parent and not st.parent_name: st.parent_name = parent
                        if phone and not st.phone: st.phone = phone
                        if addr and not st.address: st.address = addr
                        updated_st_count += 1
                    else:
                        st_obj = Student(
                            code=code,
                            full_name=name,
                            english_name=en_name,
                            dob=dob,
                            parent_name=parent,
                            phone=phone,
                            address=addr,
                            status='Đang học'
                        )
                        session.add(st_obj)
                        existing_students[code] = st_obj
                        new_st_count += 1

                    student_name_map[name.lower()] = code

            session.commit()

        # STEP 2: Sync Homework from Sheet 2 'Nhập KQ BVN'
        new_hw_count = 0
        ws_hw = safe_get_worksheet(s2, 'Nhập KQ BVN')
        if ws_hw:
            raw_btvn = ws_hw.get_all_values()
            parsed_hw = parse_homework_data(raw_btvn)

            # Query existing HW keys to prevent duplication
            existing_hw_keys = set()
            for rec in session.query(HomeworkRecord.student_code, HomeworkRecord.class_name, HomeworkRecord.submission_date).all():
                if rec[0] and rec[1] and rec[2]:
                    existing_hw_keys.add(f"{rec[0]}_{rec[1]}_{rec[2]}")

            for h in parsed_hw:
                code = h.get('code', '').strip().upper()
                name = h.get('name', '').strip()
                matched_code = code if code in existing_students else student_name_map.get(name.lower())
                cname = h.get('phone_class', '').strip()
                sub_date = h.get('date', '').strip()

                key = f"{matched_code}_{cname}_{sub_date}"
                if matched_code and key not in existing_hw_keys:
                    hw_obj = HomeworkRecord(
                        student_code=matched_code,
                        student_name=name,
                        english_name=h.get('english_name', ''),
                        class_name=cname,
                        phone=h.get('phone', ''),
                        schedule=h.get('schedule', ''),
                        submission_date=sub_date,
                        status=h.get('status', 'Chưa nộp BTVN'),
                        score=h.get('score', ''),
                        score_num=h.get('score_num', 0.0),
                        total_questions=h.get('total_questions', '')
                    )
                    session.add(hw_obj)
                    existing_hw_keys.add(key)
                    new_hw_count += 1

            session.commit()

        # STEP 3: Sync Unit Grades from Sheet 4
        new_grade_count = 0
        if s4:
            ws_imp = safe_get_worksheet(s4, 'Nhập điểm (Import results)')
            if ws_imp:
                existing_grade_keys = set()
                for rec in session.query(UnitGrade.student_code, UnitGrade.class_name, UnitGrade.test_name).all():
                    if rec[0] and rec[1] and rec[2]:
                        existing_grade_keys.add(f"{rec[0]}_{rec[1]}_{rec[2]}")

                imp_rows = ws_imp.get_all_values()
                for r in imp_rows[2:]:
                    if len(r) > 1 and r[1].strip() and r[1].strip().startswith('EVI'):
                        st_code = r[1].strip().upper()
                        name = r[2].strip() if len(r) > 2 else ''
                        en_name = r[3].strip() if len(r) > 3 else ''
                        cname = r[4].strip() if len(r) > 4 else ''
                        gv = r[5].strip() if len(r) > 5 else ''
                        test_name = r[6].strip() if len(r) > 6 else ''
                        tot_sc = parse_float_vn(r[7]) if len(r) > 7 else None
                        lis_sc = parse_float_vn(r[8]) if len(r) > 8 and r[8].strip() else None
                        rw_sc = parse_float_vn(r[9]) if len(r) > 9 and r[9].strip() else None
                        spk_sc = parse_float_vn(r[10]) if len(r) > 10 and r[10].strip() else None
                        comment = r[11].strip() if len(r) > 11 else ''

                        matched_code = st_code if st_code in existing_students else student_name_map.get(name.lower())
                        key = f"{matched_code}_{cname}_{test_name}"

                        if matched_code and key not in existing_grade_keys:
                            ug_obj = UnitGrade(
                                student_code=matched_code,
                                student_name=name,
                                english_name=en_name,
                                class_name=cname,
                                course=gv,
                                test_name=test_name or 'Bài kiểm tra',
                                listening=lis_sc,
                                listening_max=10.0,
                                reading_writing=rw_sc,
                                reading_writing_max=10.0,
                                speaking=spk_sc,
                                speaking_max=10.0,
                                total_score=tot_sc,
                                max_score=10.0,
                                comment=comment
                            )
                            session.add(ug_obj)
                            existing_grade_keys.add(key)
                            new_grade_count += 1

                session.commit()

        total_st_db = session.query(Student).count()
        total_hw_db = session.query(HomeworkRecord).count()
        total_grade_db = session.query(UnitGrade).count()

        elapsed = round(time.time() - start_t, 2)
        session.close()

        msg = f"Đồng bộ thành công sau {elapsed}s! (Thêm {new_st_count} học sinh mới, {new_hw_count} BTVN mới, {new_grade_count} điểm thi mới)."
        logger.info(f"✅ [Background Sync] {msg}")

        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with _sync_lock:
            _sync_state['last_sync_time'] = now_str
            _sync_state['last_sync_status'] = 'Thành công'
            _sync_state['last_sync_message'] = msg
            _sync_state['sync_count'] += 1
            _sync_state['is_syncing'] = False
            _sync_state['stats'] = {
                'students': total_st_db,
                'homework': total_hw_db,
                'grades': total_grade_db,
                'new_students': new_st_count,
                'updated_students': updated_st_count,
                'new_homework': new_hw_count,
                'new_grades': new_grade_count,
                'elapsed_seconds': elapsed
            }

        return True, msg

    except Exception as e:
        logger.error(f"❌ [Background Sync Error]: {e}", exc_info=True)
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = f"Lỗi đồng bộ: {str(e)}"
        with _sync_lock:
            _sync_state['last_sync_time'] = now_str
            _sync_state['last_sync_status'] = 'Thất bại'
            _sync_state['last_sync_message'] = msg
            _sync_state['is_syncing'] = False
        return False, msg


def _periodic_worker(interval_seconds=3600):
    """Vòng lặp chạy ngầm mỗi interval_seconds (1 tiếng/lần)."""
    logger.info(f"🚀 [Sync Scheduler Worker] Khởi chạy worker chạy ngầm ({interval_seconds}s / lần)...")
    # Chạy đồng bộ đầu tiên sau khi khởi động web 10 giây
    time.sleep(10)
    while not _stop_event.is_set():
        try:
            run_incremental_sync()
        except Exception as e:
            logger.error(f"Error in periodic worker loop: {e}")
        # Wait for next interval or stop signal
        _stop_event.wait(interval_seconds)


def start_background_sync(app=None, interval_seconds=3600):
    """Khởi tạo và bắt đầu thread đồng bộ chạy ngầm."""
    global _timer_thread
    if _timer_thread is not None and _timer_thread.is_alive():
        logger.info("Sync Scheduler thread đã chạy trước đó.")
        return

    _stop_event.clear()
    _timer_thread = threading.Thread(
        target=_periodic_worker,
        args=(interval_seconds,),
        daemon=True,
        name="EVI_Background_Sync_Thread"
    )
    _timer_thread.start()
    logger.info(f"✅ Đã bật Background Sync Google Sheets ➔ DB (Chu kỳ: {interval_seconds//60} phút/lần)")


def stop_background_sync():
    """Dừng thread đồng bộ chạy ngầm."""
    global _timer_thread
    _stop_event.set()
    if _timer_thread:
        _timer_thread.join(timeout=2.0)
        logger.info("🛑 Đã dừng Sync Scheduler.")
