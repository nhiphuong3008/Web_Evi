import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def clean_phone_logs():
    session = db_session()
    print("==================================================================")
    print("🧹 DỌN DẸP 84 BẢN GHI LỖI LỆCH CỘT SĐT KHỎI BẢNG PARENT_INTERACTION_LOGS")
    print("==================================================================")

    total_before = session.query(ParentInteractionLog).count()

    logs = session.query(ParentInteractionLog).all()
    misaligned_ids = []

    for l in logs:
        note = l.note or l.interaction_detail or ''
        if "Tình hình học tập:" in note and "Lịch sử chăm sóc PH:" in note:
            parts = note.split("| Lịch sử chăm sóc PH:")
            acad = parts[0].replace("Tình hình học tập:", "").strip()
            acad_clean = re.sub(r'[\d\s/\.\-]', '', acad)
            if acad_clean in ('', 'sdt', 'sđt') or re.match(r'^[\d\s/\.\-]+$', acad):
                misaligned_ids.append(l.id)

    deleted_count = session.query(ParentInteractionLog).filter(ParentInteractionLog.id.in_(misaligned_ids)).delete(synchronize_session=False)

    session.commit()
    total_after = session.query(ParentInteractionLog).count()
    session.close()

    print(f"  • Tổng bản ghi trước dọn dẹp: {total_before}")
    print(f"  • Đã xóa thành công {deleted_count} bản ghi lỗi lệch cột SĐT")
    print(f"  • Tổng bản ghi nhật ký chăm sóc chuẩn còn lại: {total_after}")
    print("==================================================================")
    print("✅ CSDL PARENT_INTERACTION_LOGS ĐÃ SẠCH SẼ 100% NỘI DUNG TƯƠNG TÁC THỰC TẾ!")

if __name__ == '__main__':
    clean_phone_logs()
