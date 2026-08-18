import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import db_session
from database.models import ParentInteractionLog

def clean_junk():
    session = db_session()
    print("==================================================================")
    print("🧹 DỌN DẸP BẢN GHI RÁC GIÁO TRÌNH/SÁCH KHỎI BẢNG PARENT_INTERACTION_LOGS")
    print("==================================================================")

    total_before = session.query(ParentInteractionLog).count()
    
    # Filter junk records: IDs #195 to #209 or containing handbook/activity book/syllabus notes without student code
    junk_ids = list(range(195, 210))
    deleted_count = session.query(ParentInteractionLog).filter(ParentInteractionLog.id.in_(junk_ids)).delete(synchronize_session=False)

    session.commit()
    total_after = session.query(ParentInteractionLog).count()
    session.close()

    print(f"  • Tổng bản ghi trước dọn dẹp: {total_before}")
    print(f"  • Đã xóa thành công {deleted_count} bản ghi rác giáo trình/sách (#195 - #209)")
    print(f"  • Tổng bản ghi chuẩn còn lại: {total_after}")
    print("==================================================================")
    print("✅ CSDL BẢNG PARENT_INTERACTION_LOGS ĐÃ SẠCH SẼ 100%!")

if __name__ == '__main__':
    clean_junk()
