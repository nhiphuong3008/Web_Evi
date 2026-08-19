"""
EVI Dashboard - API Routes
REST API endpoints cho frontend.
"""

from flask import Blueprint, jsonify, request, current_app
import logging
import datetime
import os
import json

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Reference to data (giữ biến rỗng để tương thích)
_data_store = {}
ACTIVE_DATA_MODE = 'db'


def init_api(data=None):
    """Khởi tạo API."""
    global _data_store
    _data_store = data or {}


def _get_data():
    return _data_store


@api_bp.route('/system/mode', methods=['GET', 'POST'])
def system_data_mode():
    """Lấy Mode nguồn dữ liệu (Hệ thống luôn chạy 100% CSDL SQLite)."""
    return jsonify({
        'success': True,
        'mode': 'db',
        'mode_label': 'CSDL SQLite Tập Trung (Go-Live)'
    })


@api_bp.route('/sync/status', methods=['GET'])
def get_sync_status_route():
    """API lấy trạng thái quét & đồng bộ ngầm hiện tại."""
    try:
        from services.sync_scheduler import get_sync_status
        return jsonify({'success': True, 'sync_status': get_sync_status()})
    except Exception as e:
        logger.error(f"Error in get_sync_status_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/sync/trigger', methods=['POST'])
@api_bp.route('/sync/sheets_to_db', methods=['POST'])
@api_bp.route('/data/refresh', methods=['POST'])
def trigger_sync_route():
    """
    API Kích hoạt đồng bộ tăng cường (Incremental Sync) từ Google Sheets về Cơ sở dữ liệu SQLite.
    Không xóa bảng CSDL cũ!
    """
    try:
        logger.info("⏳ Bắt đầu đồng bộ Incremental Sync: Google Sheets ➔ Database...")
        from services.sync_scheduler import run_incremental_sync, get_sync_status
        ok, msg = run_incremental_sync()
        status_info = get_sync_status()
        return jsonify({
            'success': ok,
            'message': msg,
            'stats': status_info.get('stats', {})
        })
    except Exception as e:
        logger.error(f"Error in trigger_sync_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Dashboard
# ============================================================

@api_bp.route('/dashboard/summary')
def dashboard_summary():
    """
    Tổng quan dashboard - 100% dữ liệu từ CSDL SQLite.
    """
    try:
        from services.db_service import get_dashboard_summary
        dash_data = get_dashboard_summary()
        return jsonify({
            'success': True,
            'data': dash_data
        })
    except Exception as e:
        logger.error(f"Error in dashboard_summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Renewal (Tái phí)
# ============================================================

@api_bp.route('/renewal/monthly')
def renewal_monthly():
    """
    Báo cáo tái phí hàng tháng (100% CSDL SQLite).
    Query params: month, year (optional - filter)
    """
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        from services.db_service import get_renewals_db
        db_res = get_renewals_db(month=month, year=year)

        monthly_list = []
        if db_res.get('success'):
            m_val = month or db_res.get('month', 8)
            y_val = year or db_res.get('year', 2026)
            summary = db_res.get('summary', {})
            cm_stats = db_res.get('cm_stats', [])

            monthly_list.append({
                'month': m_val,
                'year': y_val,
                'staff': cm_stats,
                'total': {
                    'name': 'Tổng cộng',
                    'due': summary.get('due', 0),
                    'success': summary.get('success', 0),
                    'stacked': summary.get('stacked', 0),
                    'pending': summary.get('pending', 0),
                    'failed': summary.get('failed', 0),
                    'rate': summary.get('rate', 0.0)
                }
            })

        return jsonify({'success': True, 'data': monthly_list})

    except Exception as e:
        logger.error(f"Error in renewal_monthly: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/renewal/list', methods=['GET'])
def renewal_list_api():
    """
    API lấy danh sách chi tiết các lượt tái phí từ CSDL.
    """
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        cm_staff = request.args.get('cm_staff', type=str)
        status = request.args.get('status', type=str)

        from services.db_service import get_renewals_db
        res = get_renewals_db(month=month, year=year, cm_staff=cm_staff, status=status)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in renewal_list_api: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/renewal/save', methods=['POST'])
def renewal_save_api():
    """
    API thêm mới hoặc cập nhật lượt tái phí học sinh vào SQLite CSDL.
    """
    try:
        body = request.get_json() or {}
        from services.db_service import save_renewal_db
        res = save_renewal_db(body)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in renewal_save_api: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/renewal/yearly')
def renewal_yearly():
    """Báo cáo tái phí năm từ CSDL."""
    try:
        from services.db_service import get_renewals_db
        res_2026 = get_renewals_db(year=2026)
        return jsonify({
            'success': True,
            'data': res_2026.get('summary', {}) if res_2026.get('success') else {}
        })
    except Exception as e:
        logger.error(f"Error in renewal_yearly: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/crm/renewals/pipeline', methods=['GET'])
def crm_renewals_pipeline():
    """API lấy dữ liệu CRM Renewal Pipeline (Kanban 5 giai đoạn, KPI & CM Leaderboard)."""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        cm_staff = request.args.get('cm_staff', type=str)

        from services.db_service import get_crm_renewal_pipeline_db
        res = get_crm_renewal_pipeline_db(month=month, year=year, cm_staff=cm_staff)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in crm_renewals_pipeline: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/crm/renewals/transaction', methods=['POST'])
def crm_renewals_transaction():
    """API ghi nhận giao dịch thu tiền Tái phí / Chồng phí mới."""
    try:
        body = request.get_json() or {}
        from services.db_service import record_renewal_transaction_db, log_activity_db
        res = record_renewal_transaction_db(body)
        if res.get('success'):
            st_code = body.get('student_code', '')
            st_name = body.get('student_name', '')
            amount = body.get('amount', 0)
            created_by = body.get('created_by') or 'cm'
            log_activity_db(
                username=created_by,
                user_fullname=created_by,
                user_role='cm',
                action_type='RENEWAL_PAYMENT',
                target_module='RENEWAL',
                target_id=st_code,
                description=f"Ghi nhận đóng phí {float(amount):,.0f} VNĐ cho học sinh {st_name} ({st_code})"
            )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in crm_renewals_transaction: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/crm/renewals/stage', methods=['POST'])
def crm_renewals_stage():
    """API chuyển giai đoạn Kanban Pipeline & lưu nhật ký care."""
    try:
        body = request.get_json() or {}
        sub_id = body.get('subscription_id') or body.get('id')
        new_stage = body.get('stage')
        note = body.get('note')
        st_name = body.get('student_name', '')
        user_name = body.get('created_by') or body.get('username') or 'cm'

        if not sub_id or not new_stage:
            return jsonify({'success': False, 'error': 'Thiếu subscription_id hoặc stage mới!'}), 400

        from services.db_service import update_subscription_stage_db, log_activity_db
        res = update_subscription_stage_db(subscription_id=sub_id, new_stage=new_stage, note=note)
        if res.get('success'):
            log_activity_db(
                username=user_name,
                user_fullname=user_name,
                user_role='cm',
                action_type='RENEWAL_STAGE',
                target_module='RENEWAL',
                target_id=str(sub_id),
                description=f"Chuyển bước tái phí học sinh {st_name or sub_id} sang giai đoạn \"{new_stage}\""
            )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in crm_renewals_stage: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Classes (Lớp học)
# ============================================================

@api_bp.route('/classes')
def get_classes():
    """Danh sách lớp học (100% CSDL SQLite)."""
    try:
        from services.db_service import get_cm_classes_db
        cm = request.args.get('cm')
        schedule = request.args.get('schedule')

        res = get_cm_classes_db(cm_staff_name=cm, include_ended=True)
        classes = res.get('data', [])

        if schedule:
            classes = [c for c in classes if schedule.lower() in (c.get('schedule') or '').lower()]

        return jsonify({'success': True, 'data': classes})

    except Exception as e:
        logger.error(f"Error in get_classes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/classes/stats')
def classes_stats():
    """
    Thống kê lớp học (100% CSDL SQLite):
    - Phân bổ theo ca (MT, TF, WS)
    - Phân bổ theo phòng
    - Phân bổ theo CM
    """
    try:
        from services.db_service import get_cm_classes_db
        res = get_cm_classes_db(include_ended=False)
        classes = res.get('data', [])
        active = [c for c in classes if (c.get('students') or c.get('student_count') or 0) > 0 and c.get('schedule')]

        # Phân bổ theo ca học
        schedule_groups = {}
        for c in active:
            sched = c.get('schedule', 'Khác')
            if sched not in schedule_groups:
                schedule_groups[sched] = {'count': 0, 'students': 0}
            schedule_groups[sched]['count'] += 1
            schedule_groups[sched]['students'] += (c.get('students') or c.get('student_count') or 0)

        # Phân bổ theo phòng
        room_groups = {}
        for c in active:
            room = c.get('room', 'Khác')
            if room and room not in room_groups:
                room_groups[room] = {'count': 0, 'students': 0}
            if room:
                room_groups[room]['count'] += 1
                room_groups[room]['students'] += (c.get('students') or c.get('student_count') or 0)

        # Phân bổ theo CM
        cm_groups = {}
        for c in active:
            cm = c.get('cm_staff') or c.get('cm', 'Khác')
            if cm and cm not in cm_groups:
                cm_groups[cm] = {'count': 0, 'students': 0}
            if cm:
                cm_groups[cm]['count'] += 1
                cm_groups[cm]['students'] += (c.get('students') or c.get('student_count') or 0)

        return jsonify({
            'success': True,
            'data': {
                'by_schedule': schedule_groups,
                'by_room': room_groups,
                'by_cm': cm_groups,
                'total_active': len(active),
                'total_students': sum((c.get('students') or c.get('student_count') or 0) for c in active),
            }
        })

    except Exception as e:
        logger.error(f"Error in classes_stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Staff / ACS
# ============================================================

@api_bp.route('/staff/acs')
def staff_acs():
    """Điểm ACS nhân viên (100% CSDL SQLite)."""
    try:
        from services.db_service import get_dashboard_summary
        dash = get_dashboard_summary()
        return jsonify({
            'success': True,
            'data': dash.get('acs_stats', {})
        })

    except Exception as e:
        logger.error(f"Error in staff_acs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Data Write (cho tương lai)
# ============================================================

@api_bp.route('/data/write', methods=['POST'])
def write_data():
    """
    Ghi dữ liệu ngược vào Google Sheets.
    Body: {sheet_name, range, data: [[...]]}
    """
    try:
        from flask import current_app
        sheets_service = current_app.config.get('SHEETS_SERVICE')

        if not sheets_service or not sheets_service.is_connected:
            return jsonify({
                'success': False,
                'error': 'Google Sheets chưa kết nối. Vui lòng cấu hình credentials.'
            }), 503

        body = request.get_json()
        if not body:
            return jsonify({'success': False, 'error': 'Missing request body'}), 400

        sheet_name = body.get('sheet_name')
        cell_range = body.get('range')
        write_data = body.get('data')

        if not all([sheet_name, cell_range, write_data]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: sheet_name, range, data'
            }), 400

        result = sheets_service.write_sheet(sheet_name, cell_range, write_data)

        if result:
            return jsonify({'success': True, 'message': 'Data written successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to write data'}), 500

    except Exception as e:
        logger.error(f"Error in write_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Sheets Info
# ============================================================

@api_bp.route('/sheets/list')
def sheets_list():
    """Danh sách tất cả sheets trong spreadsheet."""
    try:
        from flask import current_app
        sheets_service = current_app.config.get('SHEETS_SERVICE')

        if not sheets_service or not sheets_service.is_connected:
            return jsonify({
                'success': True,
                'data': [],
                'connected': False,
                'message': 'Đang chạy ở chế độ demo. Cấu hình Google Sheets credentials để kết nối.'
            })

        sheets = sheets_service.get_all_sheets()
        return jsonify({
            'success': True,
            'data': sheets,
            'connected': True,
        })

    except Exception as e:
        logger.error(f"Error in sheets_list: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Homework & Grades Search (Tra cứu BTVN & Điểm số 100% CSDL SQLite)
# ============================================================

@api_bp.route('/homework', methods=['GET'])
def get_homework():
    """
    API Lấy danh sách kết quả BTVN (CSDL SQLite) hỗ trợ lọc theo Lớp, Khoảng ngày, và Phân quyền CM/Admin.
    """
    try:
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()
        class_filter = request.args.get('class', '').strip() or request.args.get('class_name', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        cm_staff = request.args.get('cm_staff', '').strip()
        user_role = request.args.get('user_role', '').strip()

        from services.db_service import get_homework_db
        res = get_homework_db(
            search=search,
            status=status_filter,
            class_name=class_filter,
            start_date=start_date,
            end_date=end_date,
            cm_staff=cm_staff,
            user_role=user_role
        )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_homework: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/grades', methods=['GET'])
def get_grades():
    """
    API Lấy danh sách điểm số học sinh (CSDL SQLite).
    """
    try:
        class_filter = request.args.get('class_name', '').strip()
        test_filter = request.args.get('test_name', '').strip()
        search = request.args.get('search', '').strip()
        active_only = request.args.get('active_only', 'true').strip().lower() != 'false'

        from services.db_service import get_grades_db
        res = get_grades_db(search=search, class_name=class_filter, test_name=test_filter, active_only=active_only)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_grades: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students', methods=['GET'])
def get_students():
    """
    API Lấy danh sách học sinh (CSDL SQLite).
    """
    try:
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()
        class_filter = request.args.get('class_name', '').strip()

        from services.db_service import get_students_db
        res = get_students_db(search=search, status=status_filter, class_name=class_filter)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_students: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students/<student_code>', methods=['GET'])
def get_student_detail(student_code):
    """
    API Lấy hồ sơ thông tin 360 độ của 1 học sinh (Đầy đủ CSDL).
    """
    try:
        from services.db_service import get_student_detail_db
        res = get_student_detail_db(student_code)
        status_code = 200 if res.get('success') else 404
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in get_student_detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students/<student_code>/status', methods=['POST'])
def update_student_status_route(student_code):
    """
    API Cập nhật tình trạng học của học sinh ('Đang học', 'Bảo lưu', 'Đã nghỉ')
    """
    try:
        body = request.get_json() or {}
        new_status = body.get('status', '').strip()
        remove_class = body.get('remove_class', '').strip()

        if not new_status:
            return jsonify({'success': False, 'error': 'Vui lòng cung cấp tình trạng học mới'}), 400

        from services.db_service import update_student_status_db
        res = update_student_status_db(student_code, new_status=new_status, remove_class=remove_class)
        status_code = 200 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in update_student_status_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students/add', methods=['POST'])
def add_new_student_route():
    """
    API Thêm học sinh mới thủ công.
    """
    try:
        body = request.get_json() or {}
        from services.db_service import add_new_student_db
        res = add_new_student_db(body)
        status_code = 200 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in add_new_student_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students/<student_code>/add-class', methods=['POST'])
def add_student_class_route(student_code):
    """
    API Gán thêm 1 lớp học mới cho học sinh (Dành cho học sinh học 2+ lớp).
    """
    try:
        body = request.get_json() or {}
        class_to_add = body.get('class_name', '').strip()
        from services.db_service import add_student_class_db
        res = add_student_class_db(student_code, class_to_add)
        status_code = 200 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in add_student_class_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students/<student_code>/remove-class', methods=['POST'])
def remove_student_class_route(student_code):
    """
    API Gỡ 1 lớp học khỏi danh sách các lớp của học sinh.
    """
    try:
        body = request.get_json() or {}
        class_to_remove = body.get('class_name', '').strip()
        from services.db_service import remove_student_class_db
        res = remove_student_class_db(student_code, class_to_remove)
        status_code = 200 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in remove_student_class_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students/<student_code>/care-log', methods=['POST'])
def add_parent_care_log_route(student_code):
    """
    API Thêm nhật ký tương tác chăm sóc phụ huynh bằng tay.
    """
    try:
        body = request.get_json() or {}
        note = body.get('note', '').strip()
        detail = body.get('detail', note).strip()
        staff_name = body.get('staff_name', '').strip()
        student_name = body.get('student_name', '').strip()
        class_name = body.get('class_name', '').strip()
        from services.db_service import add_parent_interaction_log_db
        res = add_parent_interaction_log_db(student_code, student_name, staff_name, note, detail, class_name)
        status_code = 200 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in add_parent_care_log_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/renewals/calculate-expiry', methods=['POST'])
def calculate_expiry_route():
    """
    API Tự động tính toán lại Hạn hết phí dự kiến độc lập 100% CSDL SQLite.
    """
    try:
        from services.db_service import recalculate_all_renewals_expiry_db
        res = recalculate_all_renewals_expiry_db()
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in calculate_expiry_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/renewals/interactions/<student_code>')
def get_student_interactions_route(student_code):
    """
    API Lấy timeline nhật ký tương tác của 1 học sinh (Đã xếp từ CŨ ĐẾN GẦN NHẤT).
    """
    try:
        from services.db_service import get_student_interaction_timeline_db
        res = get_student_interaction_timeline_db(student_code)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_student_interactions_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/interactions/all')
def get_all_interactions_route():
    """
    API Lấy danh sách nhật ký tương tác tập trung cho Trang Nhật Ký Tương Tác trên Sidebar.
    """
    try:
        cm_staff = request.args.get('cm_staff', '')
        search = request.args.get('search', '')
        month = request.args.get('month', '')
        year = request.args.get('year', '')
        from services.db_service import get_all_parent_interactions_db
        res = get_all_parent_interactions_db(cm_staff=cm_staff, student_search=search, month=month, year=year)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_all_interactions_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/interactions/add', methods=['POST'])
def add_interaction_route():
    """
    API Thêm nhật ký tương tác mới từ Trang Trung Tâm 'Nhật Ký Tương Tác'.
    Tự động cập nhật tới Tái Phí, Hồ Sơ Học Sinh và Báo Cáo CM.
    """
    try:
        body = request.get_json() or {}
        st_code = body.get('student_code', '').strip()
        st_name = body.get('student_name', '').strip()
        cls_name = body.get('class_name', '').strip()
        staff_name = body.get('staff_name', '').strip()
        note = body.get('note', '').strip()
        detail = body.get('detail', note).strip()

        interaction_date = body.get('interaction_date') or body.get('created_at') or body.get('date')

        from services.db_service import add_parent_interaction_log_db, log_activity_db
        res = add_parent_interaction_log_db(st_code, st_name, staff_name, note, detail, cls_name, interaction_date=interaction_date)
        if res.get('success'):
            username = body.get('username') or f"cm_{staff_name.lower().replace(' ', '')}" if staff_name else 'cm'
            snippet = (detail or note)[:80]
            log_activity_db(
                username=username,
                user_fullname=staff_name or username,
                user_role='cm',
                action_type='INTERACTION',
                target_module='INTERACTION',
                target_id=st_code or st_name,
                description=f"Thêm nhật ký chăm sóc học sinh {st_name} ({st_code} - {cls_name}): \"{snippet}...\""
            )
        status_code = 200 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in add_interaction_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/student/lookup')
def lookup_student():
    """
    Tra cứu tổng hợp thông tin 1 học sinh (BTVN + Điểm số) 100% CSDL SQLite.
    Query param: query (Mã EVIxxx hoặc tên)
    """
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Vui lòng nhập từ khóa tìm kiếm (Tên hoặc Mã học viên)'}), 400

        from services.db_service import get_homework_db, get_grades_db
        hw_res = get_homework_db(search=query)
        grade_res = get_grades_db(search=query)

        return jsonify({
            'success': True,
            'query': query,
            'homework': hw_res.get('data', []),
            'grades': grade_res.get('data', [])
        })

    except Exception as e:
        logger.error(f"Error in lookup_student: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Health check
# ============================================================

@api_bp.route('/health')
def health():
    """Health check endpoint."""
    from flask import current_app
    sheets_service = current_app.config.get('SHEETS_SERVICE')
    connected = sheets_service.is_connected if sheets_service else False

    return jsonify({
        'status': 'ok',
        'google_sheets_connected': connected,
        'mode': 'live' if connected else 'demo',
    })


@api_bp.route('/audit/unmatched', methods=['GET'])
def get_unmatched_audit():
    """
    API Lấy danh sách các bản ghi chưa khớp mã để rà soát thủ công.
    """
    try:
        from services.db_service import get_unmatched_audit_db
        res = get_unmatched_audit_db()
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_unmatched_audit: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Auth Endpoints
# ============================================================

@api_bp.route('/auth/login', methods=['POST'])
def auth_login():
    """API Đăng nhập hệ thống."""
    try:
        body = request.get_json() or {}
        username = body.get('username', '')
        password = body.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.'}), 400

        from services.db_service import authenticate_user_db
        res = authenticate_user_db(username, password)
        status_code = 200 if res.get('success') else 401
        return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in auth_login: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# User Management Endpoints
# ============================================================

@api_bp.route('/users', methods=['GET', 'POST'])
def handle_users():
    """API Lấy danh sách hoặc Tạo tài khoản người dùng."""
    try:
        from services.db_service import get_all_users_db, create_user_db
        if request.method == 'POST':
            body = request.get_json() or {}
            username = body.get('username', '')
            password = body.get('password', '')
            full_name = body.get('full_name', '')
            email = body.get('email', '')
            role = body.get('role', 'cm')
            cm_staff_name = body.get('cm_staff_name', '')

            if not username or not password or not full_name:
                return jsonify({'success': False, 'error': 'Tên đăng nhập, mật khẩu và Họ tên không được để trống.'}), 400

            res = create_user_db(username, password, full_name, email, role, cm_staff_name)
            status_code = 201 if res.get('success') else 400
            return jsonify(res), status_code
        else:
            res = get_all_users_db()
            return jsonify(res)
    except Exception as e:
        logger.error(f"Error in handle_users: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/users/<int:user_id>', methods=['PUT', 'DELETE'])
def handle_user_detail(user_id):
    """API Cập nhật hoặc Xóa tài khoản người dùng."""
    try:
        from services.db_service import update_user_db, delete_user_db
        if request.method == 'DELETE':
            res = delete_user_db(user_id)
            status_code = 200 if res.get('success') else 400
            return jsonify(res), status_code
        else:
            body = request.get_json() or {}
            res = update_user_db(user_id, body)
            status_code = 200 if res.get('success') else 400
            return jsonify(res), status_code
    except Exception as e:
        logger.error(f"Error in handle_user_detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# CM Classes & Roster Endpoints
# ============================================================

@api_bp.route('/cm/classes', methods=['GET'])
def get_cm_classes():
    """API Lấy danh sách các lớp học phụ trách của CM."""
    try:
        cm_staff_name = request.args.get('cm_staff_name', '').strip()
        include_ended_arg = request.args.get('include_ended', 'false').lower() in ['true', '1']
        from services.db_service import get_cm_classes_db
        res = get_cm_classes_db(cm_staff_name, include_ended=include_ended_arg)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_cm_classes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/classes', methods=['POST'])
def add_new_class():
    """API Thêm mới hoặc Cập nhật Lớp học (Admin only)."""
    try:
        body = request.get_json() or {}
        from services.db_service import add_class_db, log_activity_db
        res = add_class_db(body)
        if res.get('success'):
            cname = body.get('class_name', '')
            log_activity_db(
                username=body.get('username') or 'admin',
                user_fullname=body.get('created_by') or 'Admin',
                user_role='admin',
                action_type='CLASS_EDIT',
                target_module='CLASS',
                target_id=cname,
                description=f"Thêm/Chỉnh sửa thông tin lớp học {cname} (Ca: {body.get('schedule', '')}, GV: {body.get('teacher', '')}, CM: {body.get('cm_staff', '')})"
            )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in add_new_class: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/classes/status', methods=['POST'])
def update_class_status():
    """API Cập nhật trạng thái Lớp học ('Đang hoạt động', 'Đã kết thúc', 'Không hoạt động')."""
    try:
        body = request.get_json() or {}
        class_name = body.get('class_name', '')
        status = body.get('status', 'Đang hoạt động')
        if not class_name:
            return jsonify({'success': False, 'error': 'Thiếu tên lớp.'}), 400

        from services.db_service import update_class_status_db, log_activity_db
        res = update_class_status_db(class_name, status)
        if res.get('success'):
            log_activity_db(
                username=body.get('username') or 'admin',
                user_fullname='Admin',
                user_role='admin',
                action_type='CLASS_EDIT',
                target_module='CLASS',
                target_id=class_name,
                description=f"Đã cập nhật trạng thái lớp {class_name} ➔ '{status}'"
            )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in update_class_status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Attendance Endpoints
# ============================================================

@api_bp.route('/attendance', methods=['GET', 'POST'])
def handle_attendance():
    """API Lấy lịch sử hoặc Thực hiện Điểm danh."""
    try:
        from services.db_service import save_attendance_db, get_attendance_db, log_activity_db
        if request.method == 'POST':
            body = request.get_json() or {}
            class_name = body.get('class_name', '')
            attendance_date = body.get('date', body.get('attendance_date', ''))
            records = body.get('records', [])
            created_by = body.get('created_by', '')

            if not class_name or not attendance_date:
                return jsonify({'success': False, 'error': 'Thiếu tên lớp hoặc ngày điểm danh.'}), 400

            res = save_attendance_db(class_name, attendance_date, records, created_by)
            if res.get('success'):
                user_str = created_by or 'cm'
                log_activity_db(
                    username=user_str,
                    user_fullname=user_str,
                    user_role='cm',
                    action_type='ATTENDANCE',
                    target_module='ATTENDANCE',
                    target_id=class_name,
                    description=f"Chốt điểm danh lớp {class_name} ngày {attendance_date} (Sĩ số {len(records)} học sinh)"
                )
            return jsonify(res)
        else:
            class_name = request.args.get('class_name', '').strip()
            attendance_date = request.args.get('date', '').strip()
            res = get_attendance_db(class_name, attendance_date)
            return jsonify(res)
    except Exception as e:
        logger.error(f"Error in handle_attendance: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# Grade Entry Endpoints
# ============================================================

@api_bp.route('/grades/save', methods=['POST'])
def save_grades():
    """API Nhập & Cập nhật điểm bài thi cho học sinh."""
    try:
        body = request.get_json() or {}
        grades_list = body.get('grades', [])
        if not grades_list:
            return jsonify({'success': False, 'error': 'Danh sách điểm không được trống.'}), 400

        from services.db_service import save_or_update_grade_db, log_activity_db
        res = save_or_update_grade_db(grades_list)
        if res.get('success'):
            sample_class = grades_list[0].get('class_name', '') if grades_list else ''
            sample_test = grades_list[0].get('unit_name', '') if grades_list else ''
            created_by = body.get('created_by') or body.get('username') or 'cm'
            log_activity_db(
                username=created_by,
                user_fullname=created_by,
                user_role='cm',
                action_type='GRADE',
                target_module='GRADE',
                target_id=sample_class,
                description=f"Cập nhật bảng điểm {sample_test} lớp {sample_class} cho {len(grades_list)} học sinh"
            )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in save_grades: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# AI Assessment & Export Endpoints
# ============================================================

@api_bp.route('/students/<student_code>/ai-assessment', methods=['GET'])
def get_student_ai_assessment(student_code):
    """API Lấy bài đánh giá tiến độ học tập tổng hợp AI."""
    try:
        from services.db_service import get_student_detail_db
        res = get_student_detail_db(student_code)
        if not res.get('success'):
            return jsonify(res), 404
        return jsonify({'success': True, 'ai_assessment': res.get('ai_assessment', {})})
    except Exception as e:
        logger.error(f"Error in get_student_ai_assessment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/students/<student_code>/export', methods=['GET'])
def export_student_report(student_code):
    """API Xuất Báo Cáo Học Tập ra file PDF / HTML printable, Word (.doc) hoặc Excel (.csv)."""
    try:
        fmt = request.args.get('format', 'pdf').strip().lower()
        from services.db_service import get_student_detail_db
        res = get_student_detail_db(student_code)
        if not res.get('success'):
            return jsonify(res), 404

        student = res.get('student', {})
        homework = res.get('homework', [])
        grades = res.get('grades', [])
        cm_notes = res.get('cm_notes', [])
        ai_assessment = res.get('ai_assessment', {})

        from services.export_service import (
            generate_printable_html_report,
            generate_word_report,
            generate_excel_report
        )

        import unicodedata
        import re

        raw_name = student.get('name', 'hoc_sinh')
        norm_name = unicodedata.normalize('NFD', raw_name)
        unaccented = re.sub(r'[\u0300-\u036f]', '', norm_name).replace('đ', 'd').replace('Đ', 'D')
        st_name_clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', unaccented)
        st_name_clean = re.sub(r'_+', '_', st_name_clean).strip('_') or 'hoc_sinh'

        if fmt == 'word':
            word_bytes = generate_word_report(student, homework, grades, cm_notes, ai_assessment)
            from flask import Response
            return Response(
                word_bytes,
                mimetype='application/msword',
                headers={'Content-Disposition': f'attachment; filename="Bao_Cao_Hoc_Tap_{student_code}_{st_name_clean}.doc"'}
            )
        elif fmt == 'excel':
            excel_bytes = generate_excel_report(student, homework, grades, cm_notes, ai_assessment)
            from flask import Response
            return Response(
                excel_bytes,
                mimetype='text/csv; charset=utf-8',
                headers={'Content-Disposition': f'attachment; filename="Bao_Cao_Hoc_Tap_{student_code}_{st_name_clean}.csv"'}
            )
        else:
            # HTML printable for PDF
            html_content = generate_printable_html_report(student, homework, grades, cm_notes, ai_assessment)
            from flask import Response
            return Response(html_content, mimetype='text/html; charset=utf-8')

    except Exception as e:
        logger.error(f"Error in export_student_report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule', methods=['GET'])
def get_schedule():
    """
    API Lấy thời khóa biểu lớp học (Tab SCHEDULE):
    - Đưa lớp của CM đang đăng nhập / chọn lọc lên đầu tiên.
    """
    try:
        cm_staff = request.args.get('cm_staff_name', '').strip()
        day = request.args.get('day', '').strip()
        class_name = request.args.get('class_name', '').strip()
        search = request.args.get('search', '').strip()

        from services.db_service import get_schedules_db
        res = get_schedules_db(cm_staff_name=cm_staff, day=day, class_name=class_name, search=search)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule/matrix', methods=['GET'])
def get_schedule_matrix():
    """API Lấy Thời khóa biểu ma trận 7 ngày x 2 ca học (MT5 & MT6)."""
    try:
        cm_staff = request.args.get('cm_staff_name', '').strip()
        from services.db_service import get_schedule_matrix_db
        res = get_schedule_matrix_db(cm_staff_name=cm_staff)
        
        # Nếu chưa có bản ghi trong DB, thử nạp lại thời khóa biểu tự động
        if not res.get('matrix') or len(res.get('matrix', [])) == 0:
            try:
                from test.run_schedule_migration_standalone import migrate_schedule
                migrate_schedule()
                res = get_schedule_matrix_db(cm_staff_name=cm_staff)
            except Exception as e_mig:
                logger.warning(f"Could not auto-migrate schedule: {e_mig}")

        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_schedule_matrix: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule/class-detail', methods=['GET'])
def get_schedule_class_detail():
    """API Lấy Pop-up Nhật ký bài học 24 buổi của 1 lớp học."""
    try:
        class_name = request.args.get('class_name', '').strip()
        if not class_name:
            return jsonify({'success': False, 'error': 'Vui lòng cung cấp tên lớp học'}), 400

        from services.db_service import get_class_lesson_log_db
        res = get_class_lesson_log_db(class_name)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_schedule_class_detail: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule/delay-lesson', methods=['POST'])
def delay_schedule_lesson():
    """API Bật/Tắt Lùi Lịch cho 1 buổi học cụ thể của lớp học."""
    try:
        data = request.get_json() or {}
        class_name = data.get('class_name', '').strip()
        lesson_num = data.get('lesson_num')
        if not class_name or not lesson_num:
            return jsonify({'success': False, 'error': 'Vui lòng cung cấp class_name và lesson_num'}), 400

        from services.db_service import toggle_delay_class_lesson_db, get_class_lesson_log_db
        toggle_res = toggle_delay_class_lesson_db(class_name, int(lesson_num))
        if not toggle_res.get('success'):
            return jsonify(toggle_res), 500

        # Refetch updated class lesson log
        updated_log = get_class_lesson_log_db(class_name)
        return jsonify(updated_log)
    except Exception as e:
        logger.error(f"Error in delay_schedule_lesson: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule/holiday-shift/preview', methods=['POST'])
def preview_holiday_shift():
    """API Tính trước tác động của đợt nghỉ lễ / lùi lịch."""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        affected_classes = data.get('affected_classes', ['ALL'])
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Vui lòng cung cấp start_date và end_date'}), 400

        from services.db_service import preview_holiday_shift_db
        res = preview_holiday_shift_db(start_date, end_date, affected_classes)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in preview_holiday_shift: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule/holiday-shift', methods=['POST'])
def create_holiday_shift():
    """API Áp dụng đợt nghỉ lễ / lùi lịch mới."""
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        holiday_type = data.get('holiday_type', 'Nghỉ lễ cố định').strip()
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        affected_classes = data.get('affected_classes', ['ALL'])
        note = data.get('note', '').strip()
        created_by = data.get('created_by', 'Admin').strip()

        if not title or not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Vui lòng điền đầy đủ tiêu đề, ngày bắt đầu và ngày kết thúc'}), 400

        from services.db_service import create_holiday_shift_db
        res = create_holiday_shift_db(title, holiday_type, start_date, end_date, affected_classes, note, created_by)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in create_holiday_shift: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule/holiday-history', methods=['GET'])
def get_holiday_history():
    """API Lấy danh sách nhật ký đợt nghỉ lễ / lùi lịch."""
    try:
        from services.db_service import get_holiday_history_logs_db
        res = get_holiday_history_logs_db()
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_holiday_history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/schedule/holiday-shift/cancel', methods=['POST'])
def cancel_holiday_shift():
    """API Hủy đợt nghỉ lễ / lùi lịch và hoàn tác hạn học sinh."""
    try:
        data = request.get_json() or {}
        holiday_id = data.get('holiday_id')
        if not holiday_id:
            return jsonify({'success': False, 'error': 'Vui lòng cung cấp holiday_id'}), 400

        from services.db_service import cancel_holiday_shift_db
        res = cancel_holiday_shift_db(int(holiday_id))
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in cancel_holiday_shift: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



def _format_comment_html(comment_text, default_text=""):
    """Format comment text for PDF output with support for multiline, bold (**text**), italic (*text*), and bullet points (- item)."""
    import html as html_lib
    import re
    
    text = (comment_text or '').strip()
    if not text:
        text = default_text
    if not text:
        return '<p style="margin: 0; font-size: 13.5px; color: #64748b; font-style: italic;">(Chưa có nhận xét cho bài kiểm tra này)</p>'

    escaped = html_lib.escape(text)

    # Bold **text** -> <strong>text</strong>
    escaped = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped)
    # Italic *text* -> <em>text</em>
    escaped = re.sub(r'\*(.*?)\*', r'<em>\1</em>', escaped)

    lines = escaped.split('\n')
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('&bull; ') or stripped.startswith('• '):
            if stripped.startswith('- '):
                content = stripped[2:]
            elif stripped.startswith('&bull; '):
                content = stripped[7:]
            else:
                content = stripped[2:]
            formatted_lines.append(
                f'<div style="padding-left: 10px; margin-top: 3px; display: flex; align-items: flex-start;">'
                f'<span style="margin-right: 6px; font-weight: bold; color: #0284c7;">•</span>'
                f'<span>{content}</span></div>'
            )
        else:
            formatted_lines.append(line)

    final_html = '<br>'.join(formatted_lines)
    return f'<div style="margin: 0; font-size: 13.5px; color: #0f172a; line-height: 1.5; font-weight: 500;">{final_html}</div>'


@api_bp.route('/students/<student_code>/test-report-pdf', methods=['GET'])
def get_student_unit_test_pdf(student_code):
    """
    Tạo và render File HTML/PDF Báo Cáo Kết Quả Bài Kiểm Tra Bài Thi chuẩn mẫu SUN UNIT TEST.
    """
    try:
        from services.db_service import get_student_detail_db
        res = get_student_detail_db(student_code)
        if not res.get('success'):
            return f"<h1>Không tìm thấy học sinh mã {student_code}</h1>", 404

        st = res.get('student', {})
        test_name = request.args.get('test_name', 'Unit 01')
        class_name = request.args.get('class_name', st.get('class_name', ''))
        is_moon = request.args.get('is_moon', '0') == '1' or class_name.lower().startswith('moon')

        exam_date_raw = request.args.get('exam_date', '')
        if exam_date_raw:
            try:
                parts = exam_date_raw.split('-')
                if len(parts) == 3:
                    today_str = f"{parts[2]}/{parts[1]}/{parts[0]}"
                else:
                    today_str = exam_date_raw
            except Exception:
                today_str = datetime.date.today().strftime('%d/%m/%Y')
        else:
            today_str = datetime.date.today().strftime('%d/%m/%Y')

        teacher_name = st.get('teacher') or 'Teacher Miguel'

        if is_moon:
            tot_vocab = float(request.args.get('tot_vocab', 20))
            corr_vocab = float(request.args.get('corr_vocab', 0))
            phonics = float(request.args.get('phonics', 9.0))
            comment = request.args.get('comment', '')

            # Load official Moon syllabus JSON
            syllabus_json_path = os.path.join(current_app.root_path, 'static', 'js', 'moon_syllabus_db.json')
            moon_syllabus_map = {}
            if os.path.exists(syllabus_json_path):
                try:
                    with open(syllabus_json_path, 'r', encoding='utf-8') as f:
                        moon_syllabus_map = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading moon_syllabus_db.json: {e}")

            # Determine Level Key & Unit Key
            level_key = "Moon 1"
            cls_lower = class_name.lower()
            if "moon 2" in cls_lower: level_key = "Moon 2"
            elif "moon 3" in cls_lower: level_key = "Moon 3"
            elif "moon 4" in cls_lower: level_key = "Moon 4"
            elif "moon 5" in cls_lower: level_key = "Moon 5"
            elif "moon 6" in cls_lower: level_key = "Moon 6"

            unit_key = "Unit 01"
            if "02" in test_name or "2" in test_name: unit_key = "Unit 02"
            elif "03" in test_name or "3" in test_name: unit_key = "Unit 03"
            elif "04" in test_name or "4" in test_name: unit_key = "Unit 04"
            elif "05" in test_name or "5" in test_name: unit_key = "Unit 05"
            elif "06" in test_name or "6" in test_name: unit_key = "Unit 06"
            elif "07" in test_name or "7" in test_name: unit_key = "Unit 07"
            elif "08" in test_name or "8" in test_name: unit_key = "Unit 08"
            elif "09" in test_name or "9" in test_name: unit_key = "Unit 09"

            level_data = moon_syllabus_map.get(level_key, {})
            unit_data = level_data.get(unit_key, level_data.get("Unit 01", {}))

            moon_level_title = unit_data.get("title", f"{level_key.upper()} UNIT TEST")
            unit_subtitle = unit_data.get("subtitle", f"UNIT {unit_key.replace('Unit ', '')}: LESSON REVIEW")
            vocab_items = unit_data.get("vocab", ["Word 1", "Word 2"])
            phonics_items = unit_data.get("phonics", ["Letter A - /a/"])
            struct_items = unit_data.get("struct", ["Sample Structure"])

            # Build HTML rows for Vocabulary
            vocab_rows = ""
            for idx, item in enumerate(vocab_items):
                cell_cat = f'<td class="cat-vocab" rowspan="{len(vocab_items)}">Vocabulary<br><i style="font-size: 11px; font-weight: normal;">Từ vựng</i></td>' if idx == 0 else ''
                check_exc = '<td class="check-mark">✓</td><td></td><td></td>' if idx < len(vocab_items) - 1 else '<td></td><td class="check-mark">✓</td><td></td>'
                vocab_rows += f'<tr>{cell_cat}<td>{item}</td>{check_exc}</tr>'

            # Build HTML rows for Phonics
            phonics_rows = ""
            for idx, item in enumerate(phonics_items):
                cell_cat = f'<td class="cat-phonics" rowspan="{len(phonics_items)}">Phonics<br><i style="font-size: 11px; font-weight: normal;">Ngữ âm</i></td>' if idx == 0 else ''
                phonics_rows += f'<tr>{cell_cat}<td>{item}</td><td class="check-mark">✓</td><td></td><td></td></tr>'

            # Build HTML rows for Structures
            struct_rows = ""
            for idx, item in enumerate(struct_items):
                cell_cat = f'<td class="cat-struct" rowspan="{len(struct_items)}">Mẫu câu<br><i style="font-size: 11px; font-weight: normal;">Structures</i></td>' if idx == 0 else ''
                struct_rows += f'<tr>{cell_cat}<td>{item}</td><td class="check-mark">✓</td><td></td><td></td></tr>'

            moon_cmt_formatted = _format_comment_html(
                comment,
                default_text=f"Em {st.get('name')} rất ngoan, tiếp thu từ vựng tốt và phản xạ ngữ âm chính xác. Thầy/Cô khen ngợi tinh thần học tập khích lệ của em!"
            )

            html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{moon_level_title} - {st.get('name')}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">
    <style>
        @page {{ size: A4 portrait; margin: 10mm; }}
        body {{
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 10px;
            color: #000;
            background: #fff;
        }}
        .no-print {{ text-align: center; margin-bottom: 15px; }}
        .moon-box {{
            border: 2px solid #000;
            max-width: 820px;
            margin: 0 auto;
            background: #fff;
        }}
        .main-title {{
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            padding: 8px 0 4px;
            letter-spacing: 0.5px;
        }}
        .sub-title {{
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            padding-bottom: 8px;
            border-bottom: 2px solid #000;
        }}
        .info-bar {{
            display: flex;
            width: 100%;
            border-bottom: 2px solid #000;
            font-size: 14px;
            font-weight: bold;
        }}
        .info-cell {{
            padding: 6px 10px;
        }}
        .name-cell {{ flex: 1.5; background: #d9d2e9; border-right: 1px solid #000; }}
        .class-cell {{ flex: 1.2; background: #cfe2f3; border-right: 1px solid #000; }}
        .date-cell {{ flex: 1; background: #f4ccd3; }}

        .table-moon {{
            width: 100%;
            border-collapse: collapse;
        }}
        .table-moon th, .table-moon td {{
            border: 1px solid #000;
            padding: 5px 8px;
            font-size: 13px;
        }}
        .table-moon th {{
            background: #1f4e78;
            color: #fff;
            font-weight: bold;
            text-align: center;
        }}
        .cat-vocab {{ background: #548235; color: #fff; font-weight: bold; text-align: center; vertical-align: middle; width: 15%; }}
        .cat-phonics {{ background: #ed7d31; color: #fff; font-weight: bold; text-align: center; vertical-align: middle; width: 15%; }}
        .cat-struct {{ background: #7030a0; color: #fff; font-weight: bold; text-align: center; vertical-align: middle; width: 15%; }}
        .cat-comment {{ background: #333f48; color: #fff; font-weight: bold; text-align: center; vertical-align: middle; width: 15%; }}
        
        .check-mark {{ text-align: center; font-size: 15px; font-weight: bold; color: #1f4e78; }}

        .instructions {{
            padding: 8px 12px;
            font-size: 11.5px;
            line-height: 1.4;
            border-top: 2px solid #000;
            background: #fff;
        }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button onclick="window.print();" style="background: #1f4e78; color: #fff; border: none; padding: 10px 20px; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer;">
            🖨️ In Báo Cáo Moon (PDF Mẫu Chuẩn)
        </button>
    </div>

    <div class="moon-box">
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; border-bottom: 2px solid #000; background: #f8fafc;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 46px; height: 46px; object-fit: contain; border-radius: 4px;">
                <div>
                    <div style="font-size: 18px; font-weight: 900; color: #0432ff; letter-spacing: 0.5px; text-transform: uppercase;">TRUNG TÂM ANH NGỮ VICARE</div>
                    <div style="font-size: 11px; color: #e60000; font-weight: 800; letter-spacing: 0.3px;">VICARE ENGLISH CENTER</div>
                </div>
            </div>
            <div style="text-align: right; font-size: 11.5px; color: #475569; font-weight: 700;">
                BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG HỌC TẬP MOON
            </div>
        </div>

        <div class="main-title">{moon_level_title}</div>
        <div class="sub-title">{unit_subtitle}</div>

        <div class="info-bar">
            <div class="info-cell name-cell">Student name: <strong>{st.get('name')}</strong></div>
            <div class="info-cell class-cell">Class: <strong>{class_name}</strong></div>
            <div class="info-cell date-cell">Date: <strong>{today_str}</strong></div>
        </div>

        <table class="table-moon">
            <thead>
                <tr>
                    <th style="width: 15%;">Catergory</th>
                    <th style="width: 37%;">Content</th>
                    <th style="width: 16%;">Excellent</th>
                    <th style="width: 16%;">Satisfactory</th>
                    <th style="width: 16%;">Need support</th>
                </tr>
            </thead>
            <tbody>
                <!-- VOCABULARY SECTION (GREEN) -->
                {vocab_rows}

                <!-- PHONICS SECTION (ORANGE) -->
                {phonics_rows}

                <!-- STRUCTURES SECTION (PURPLE) -->
                {struct_rows}

                <!-- COMMENTS SECTION (DARK GRAY) -->
                <tr>
                    <td class="cat-comment">
                        Teacher comments<br><i style="font-size: 11px; font-weight: normal;">Nhận xét</i>
                    </td>
                    <td colspan="4" style="padding: 10px; font-size: 13px; line-height: 1.5; height: 60px; vertical-align: top;">
                        {moon_cmt_formatted}
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="instructions">
            <strong>Test instructions:</strong><br>
            - <strong>Excellent (2 points):</strong> Student can answer without any support<br>
            <span style="color: #444;">Xuất sắc (2 điểm): Học sinh có thể trả lời mà không cần sự hỗ trợ</span><br>
            - <strong>Satisfactory (1 point):</strong> Student can answer with a little support (first sound/word hint)<br>
            <span style="color: #444;">Đạt yêu cầu (1 điểm): Học sinh có thể trả lời với một chút trợ giúp (gợi ý âm/từ đầu tiên)</span><br>
            - <strong>Need Improvement (0 points):</strong> Student need support to repeat the answer<br>
            <span style="color: #444;">Cần ôn tập thêm (0 point): Học sinh cần hỗ trợ để đọc lại câu trả lời</span>
        </div>
    </div>

    <script>
        window.onload = function() {{
            setTimeout(function() {{
                window.print();
            }}, 500);
        }};
    </script>
</body>
</html>"""
            return html_content

        tot_lis = float(request.args.get('tot_lis', 0))
        tot_rw = float(request.args.get('tot_rw', 0))
        tot_spk = float(request.args.get('tot_spk', 0))

        corr_lis = float(request.args.get('corr_lis', 0))
        corr_rw = float(request.args.get('corr_rw', 0))
        corr_spk = float(request.args.get('corr_spk', 0))
        comment = request.args.get('comment', '')

        # Fallback to StudentGrade DB table if query parameters are missing/zero
        if tot_lis == 0 and tot_rw == 0 and tot_spk == 0:
            try:
                from database.models import StudentGrade
                from database.db_manager import db_manager
                with db_manager.session_scope() as session:
                    g_rec = session.query(StudentGrade).filter(
                        StudentGrade.student_code == student_code,
                        StudentGrade.test_name.ilike(f"%{test_name.strip()}%")
                    ).first()
                    if g_rec:
                        tot_lis = g_rec.listening_max or 25
                        tot_rw = g_rec.reading_writing_max or 35
                        tot_spk = g_rec.speaking_max or 10
                        corr_lis = g_rec.listening if g_rec.listening is not None else 0
                        corr_rw = g_rec.reading_writing if g_rec.reading_writing is not None else 0
                        corr_spk = g_rec.speaking if g_rec.speaking is not None else 0
            except Exception as ex:
                logger.error(f"Error fetching grade from DB for test report pdf: {ex}")

        # Check if speaking score exists
        has_speaking = (tot_spk > 0 or corr_spk > 0)

        # Calculate scores & overall
        tot_all = tot_lis + tot_rw + (tot_spk if has_speaking else 0)
        corr_all = corr_lis + corr_rw + (corr_spk if has_speaking else 0)
        p10 = round((corr_all / tot_all * 10), 1) if tot_all > 0 else 0.0

        def _fmt(val):
            return int(val) if float(val).is_integer() else val

        # Determine dynamic banner title based on class prefix
        cls_prefix = class_name.strip().upper()
        if cls_prefix.startswith('GALAX'):
            unit_title_banner = 'GALAX UNIT TEST'
        elif cls_prefix.startswith('MOON'):
            unit_title_banner = 'MOON UNIT TEST'
        else:
            unit_title_banner = 'SUN UNIT TEST'

        comment_section_html = _format_comment_html(comment)

        # Build Printable HTML matching the image template exactly
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo Cáo Bài Kiểm Tra - {st.get('name')}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #0f172a;
            background: #fff;
        }}
        .report-box {{
            border: 2px dashed #002060;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        .logo-text {{
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            font-size: 19px;
            font-weight: 800;
            color: #0432ff;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }}
        .logo-sub {{
            font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
            font-size: 11.5px;
            font-weight: 800;
            color: #e60000;
            letter-spacing: 0.3px;
        }}
        .title-text {{
            text-align: right;
            font-size: 24px;
            font-weight: bold;
            color: #002060;
            letter-spacing: 1px;
        }}
        .subtitle-text {{
            text-align: right;
            font-size: 19px;
            font-weight: bold;
            color: #002060;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        .info-table td {{
            padding: 8px 12px;
            font-size: 16px;
            border-bottom: 1px dotted #888;
        }}
        .info-label {{
            font-weight: bold;
            color: #002060;
            width: 35%;
        }}
        .info-val {{
            font-size: 17px;
            font-weight: bold;
            color: #002060;
            background: #e6ecf5;
        }}
        .section-header {{
            background: #002060;
            color: #fff;
            font-weight: bold;
            font-size: 15px;
            padding: 6px 10px;
            margin-top: 15px;
        }}
        .grid-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 5px;
        }}
        .grid-table th {{
            background: #d9e1f2;
            color: #002060;
            font-size: 15px;
            padding: 8px;
            border: 1px solid #b4c6e7;
            text-align: center;
        }}
        .grid-table td {{
            padding: 12px;
            border: 1px solid #b4c6e7;
            font-size: 15px;
            vertical-align: top;
            width: 50%;
        }}
        .score-box {{
            text-align: center;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            color: #002060;
            border: 1px solid #b4c6e7;
            background: #f2f5f9;
        }}
        .comment-content {{
            padding: 12px;
            border: 1px solid #b4c6e7;
            font-size: 14.5px;
            line-height: 1.6;
        }}
        @media print {{
            .no-print {{ display: none !important; }}
            .report-box {{ border: 2px dashed #002060; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="text-align: center; margin-bottom: 20px;">
        <button onclick="window.print();" style="background: #002060; color: #fff; border: none; padding: 12px 24px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            🖨️ In Báo Cáo Bài Test (Lưu Dạng File PDF)
        </button>
    </div>

    <div class="report-box">
        <!-- Header -->
        <table class="header-table">
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 54px; height: 54px; object-fit: contain; border-radius: 6px;">
                        <div>
                            <div class="logo-text">TRUNG TÂM ANH NGỮ VICARE</div>
                            <div class="logo-sub">VICARE ENGLISH CENTER</div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="title-text">{unit_title_banner}</div>
                    <div class="subtitle-text">{test_name.upper()}</div>
                </td>
            </tr>
        </table>

        <!-- Info Table -->
        <table class="info-table">
            <tr>
                <td class="info-label">Student Name (Họ và tên học sinh):</td>
                <td class="info-val">{st.get('name')}</td>
            </tr>
            <tr>
                <td class="info-label">Class (Tên lớp):</td>
                <td class="info-val">{class_name}</td>
            </tr>
            <tr>
                <td class="info-label">Date of examination (Ngày kiểm tra):</td>
                <td class="info-val">{today_str}</td>
            </tr>
            <tr>
                <td class="info-label">Teacher (Giáo viên):</td>
                <td class="info-val">{teacher_name}</td>
            </tr>
        </table>

        <!-- Result Section -->
        <div class="section-header">RESULT:</div>
        {f"""
        <table class="grid-table">
            <tr>
                <th style="width: 33.3%;">Listening</th>
                <th style="width: 33.3%;">Reading & Writing</th>
                <th style="width: 33.3%;">Speaking</th>
            </tr>
            <tr>
                <td style="width: 33.3%;">
                    - {test_name}: <strong>{_fmt(corr_lis)} / {_fmt(tot_lis)}</strong> câu đúng
                </td>
                <td style="width: 33.3%;">
                    - {test_name}: <strong>{_fmt(corr_rw)} / {_fmt(tot_rw)}</strong> câu đúng
                </td>
                <td style="width: 33.3%;">
                    - {test_name}: <strong>{_fmt(corr_spk)} / {_fmt(tot_spk)}</strong> điểm
                </td>
            </tr>
        </table>
        """ if has_speaking else f"""
        <table class="grid-table">
            <tr>
                <th style="width: 50%;">Listening</th>
                <th style="width: 50%;">Reading & Writing</th>
            </tr>
            <tr>
                <td style="width: 50%;">
                    - {test_name}: <strong>{_fmt(corr_lis)} / {_fmt(tot_lis)}</strong> câu đúng
                </td>
                <td style="width: 50%;">
                    - {test_name}: <strong>{_fmt(corr_rw)} / {_fmt(tot_rw)}</strong> câu đúng
                </td>
            </tr>
        </table>
        """}

        <!-- Overall Score Section -->
        <div class="section-header">OVERALL SCORE:</div>
        <div class="score-box">
            TỔNG ĐIỂM BÀI TEST: <strong>{_fmt(corr_all)} / {_fmt(tot_all)}</strong> câu/điểm &nbsp;|&nbsp; 🎯 THANG ĐIỂM 10: <strong style="color: #c00000; font-size: 22px;">{p10} / 10 điểm</strong>
        </div>

        <!-- Comments Section -->
        <div class="section-header">COMMENTS:</div>
        <div class="comment-content">
            {comment_section_html}
        </div>
    </div>

    <script>
        window.onload = function() {{
            setTimeout(function() {{
                window.print();
            }}, 500);
        }};
    </script>
</body>
</html>"""
        return html_content
    except Exception as e:
        logger.error(f"Error generating unit test pdf report: {e}")
        return f"<h1>Lỗi xuất báo cáo PDF: {str(e)}</h1>", 500


@api_bp.route('/interactions/update/<int:log_id>', methods=['POST'])
def update_parent_interaction(log_id):
    """API Chỉnh sửa nhật ký tương tác dành cho Admin."""
    try:
        from services.db_service import update_parent_interaction_log_db, log_activity_db
        payload = request.json or {}
        staff_name = payload.get('staff_name', '')
        note = payload.get('note', '')
        detail = payload.get('detail', '')
        student_code = payload.get('student_code', '')
        student_name = payload.get('student_name', '')

        interaction_date = payload.get('interaction_date') or payload.get('created_at') or payload.get('date')

        res = update_parent_interaction_log_db(
            log_id=log_id,
            staff_name=staff_name,
            note=note,
            detail=detail,
            student_code=student_code,
            student_name=student_name,
            interaction_date=interaction_date
        )
        if res.get('success'):
            log_activity_db(
                username=payload.get('username') or 'admin',
                user_fullname=staff_name or 'Admin',
                user_role='admin',
                action_type='UPDATE',
                target_module='INTERACTION',
                target_id=str(log_id),
                description=f"Chỉnh sửa nhật ký tương tác #{log_id} của học sinh {student_name} ({student_code})"
            )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error updating interaction #{log_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/interactions/delete/<int:log_id>', methods=['POST', 'DELETE'])
def delete_parent_interaction(log_id):
    """API Xóa nhật ký tương tác dành cho Admin."""
    try:
        from services.db_service import delete_parent_interaction_log_db, log_activity_db
        res = delete_parent_interaction_log_db(log_id=log_id)
        if res.get('success'):
            log_activity_db(
                username='admin',
                user_fullname='Admin',
                user_role='admin',
                action_type='DELETE',
                target_module='INTERACTION',
                target_id=str(log_id),
                description=f"Xóa nhật ký tương tác #{log_id}"
            )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error deleting interaction #{log_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/renewals/report-pdf', methods=['GET'])
def get_monthly_renewal_pdf_report():
    """
    Tạo và render Báo Cáo Tổng Hợp Tái Phí Học Sinh Hàng Tháng dạng HTML Printable / File PDF.
    Bao gồm KPI Tổng quan, danh sách học sinh và Nhật Ký Tương Tác Gần Nhất của từng học sinh.
    """
    try:
        from services.db_service import get_monthly_renewal_pdf_data_db
        month = request.args.get('month', type=int, default=datetime.date.today().month)
        year = request.args.get('year', type=int, default=datetime.date.today().year)
        cm_staff = request.args.get('cm_staff', type=str, default='').strip()

        report_res = get_monthly_renewal_pdf_data_db(month=month, year=year, cm_staff=cm_staff)
        if not report_res.get('success'):
            return f"<h1>Lỗi tạo báo cáo PDF tái phí: {report_res.get('error')}</h1>", 500

        data = report_res.get('data', [])
        summary = report_res.get('summary', {})

        # Generate HTML rows
        rows_html = ""
        for idx, r in enumerate(data, 1):
            st_name = r.get('student_name', '—')
            st_code = r.get('student_code', '—')
            en_name = r.get('english_name', '')
            cls = r.get('class_name', '—')
            cm = r.get('cm_staff', '—')
            exp_date = r.get('expected_expiry_date', '—')
            fee_pkg = r.get('renewal_package', '—')
            status = r.get('status', 'pending')
            comp_date = r.get('completed_date', '—')
            latest_care = r.get('latest_interaction')

            status_badge_map = {
                'Renewed': '<span style="background: #e6f4ea; color: #137333; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🟢 Thành công</span>',
                'Early_Renewed': '<span style="background: #e8f0fe; color: #1a73e8; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🔵 Chồng phí</span>',
                'Upcoming': '<span style="background: #fef7e0; color: #b06000; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🟡 Chờ xử lý</span>',
                'Failed': '<span style="background: #fce8e6; color: #c5221f; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🔴 Thất bại</span>',
                'completed': '<span style="background: #e6f4ea; color: #137333; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🟢 Thành công</span>',
                'stacked': '<span style="background: #e8f0fe; color: #1a73e8; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🔵 Chồng phí</span>',
                'pending': '<span style="background: #fef7e0; color: #b06000; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🟡 Chờ xử lý</span>',
                'failed': '<span style="background: #fce8e6; color: #c5221f; padding: 4px 8px; border-radius: 6px; font-weight: 600;">🔴 Thất bại</span>',
            }
            status_html = status_badge_map.get(status, f'<span style="padding: 4px 8px; border-radius: 6px; font-weight: 600;">{status}</span>')

            care_html = '<em style="color: #888;">Chưa có nhật ký</em>'
            if latest_care:
                c_staff = latest_care.get('staff_name', 'CM')
                c_time = latest_care.get('created_at', '')
                c_detail = latest_care.get('detail', '')
                care_html = f'''
                    <div style="font-size: 11px; text-align: left;">
                        <strong style="color: #2b6cb0;">[{c_time}] {c_staff}:</strong>
                        <div style="color: #2d3748; margin-top: 2px;">{c_detail}</div>
                    </div>
                '''

            en_display = f'<span style="color: #718096; font-size: 11px;">({en_name})</span>' if en_name else ''

            rows_html += f'''
            <tr>
                <td style="text-align: center; font-weight: 600;">{idx}</td>
                <td><strong>{st_name}</strong> {en_display}</td>
                <td style="text-align: center; color: #4a5568; font-weight: 600;">{st_code}</td>
                <td style="text-align: center;">{cls}</td>
                <td style="text-align: center;">{cm}</td>
                <td style="text-align: center; font-weight: 600; color: #2e7d32;">{exp_date}</td>
                <td style="text-align: center;">{fee_pkg}</td>
                <td style="text-align: center;">{status_html}</td>
                <td style="text-align: center;">{comp_date}</td>
                <td style="padding: 6px 10px;">{care_html}</td>
            </tr>
            '''

        cm_filter_info = f" (CM: {cm_staff})" if cm_staff else ""

        html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo Cáo Tái Phí Tháng {month}/{year}</title>
    <style>
        @page {{
            size: A4 landscape;
            margin: 10mm;
        }}
        body {{
            font-family: 'Segoe UI', Arial, Roboto, sans-serif;
            color: #1a202c;
            background: #f8fafc;
            margin: 0;
            padding: 20px;
            font-size: 12px;
        }}
        .no-print {{
            position: fixed;
            top: 15px;
            right: 20px;
            z-index: 9999;
            background: #ffffff;
            padding: 8px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            gap: 10px;
        }}
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 13px;
        }}
        .btn-print {{ background: #2563eb; color: #fff; }}
        .btn-print:hover {{ background: #1d4ed8; }}
        .btn-close {{ background: #e2e8f0; color: #475569; }}

        .report-header {{
            text-align: center;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 12px;
            margin-bottom: 15px;
        }}
        .brand-title {{
            font-size: 18px;
            font-weight: 800;
            color: #1e3a8a;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .report-title {{
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 4px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }}
        .kpi-card {{
            background: #ffffff;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        .kpi-title {{ font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; }}
        .kpi-value {{ font-size: 18px; font-weight: 800; margin-top: 4px; color: #0f172a; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #cbd5e1;
        }}
        th {{
            background: #1e293b;
            color: #ffffff;
            padding: 8px 6px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            border: 1px solid #334155;
        }}
        td {{
            padding: 8px 6px;
            border: 1px solid #e2e8f0;
            vertical-align: middle;
            font-size: 11.5px;
        }}
        tr:nth-child(even) {{ background: #f8fafc; }}

        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: #fff; padding: 0; }}
            table {{ page-break-inside: auto; }}
            tr {{ page-break-inside: avoid; page-break-after: auto; }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn btn-print" onclick="window.print();">🖨️ In Báo Cáo / Lưu PDF</button>
        <button class="btn btn-close" onclick="window.close();">❌ Đóng</button>
    </div>

    <div class="report-header" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2.5px solid #2563eb; padding-bottom: 14px; margin-bottom: 18px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <img src="/static/images/logo.jpg" alt="Vicare Logo" style="width: 54px; height: 54px; object-fit: contain;">
            <div>
                <div class="brand-title" style="font-size: 20px; font-weight: 900; color: #0432ff; letter-spacing: 0.5px; text-transform: uppercase;">TRUNG TÂM ANH NGỮ VICARE</div>
                <div class="report-title" style="font-size: 13.5px; font-weight: 800; color: #0f172a; margin-top: 3px;">BÁO CÁO TỔNG HỢP THEO DÕI TÁI PHÍ HỌC SINH - THÁNG {month}/{year}{cm_filter_info}</div>
            </div>
        </div>
        <div style="font-size: 11.5px; color: #64748b; text-align: right; font-weight: 600; line-height: 1.4;">
            <strong>VICARE ENGLISH CENTER</strong><br>
            Hotline: 098.xxx.xxxx
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">📝 Đến Hạn</div>
            <div class="kpi-value" style="color: #2563eb;">{summary.get('due', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">🟢 Thành Công</div>
            <div class="kpi-value" style="color: #16a34a;">{summary.get('completed', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">🔵 Chồng Phí</div>
            <div class="kpi-value" style="color: #0284c7;">{summary.get('overlapping', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">🟡 Chờ Xử Lý</div>
            <div class="kpi-value" style="color: #d97706;">{summary.get('pending', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">🔴 Thất Bại</div>
            <div class="kpi-value" style="color: #dc2626;">{summary.get('failed', 0)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">📊 Tỷ Lệ Chuẩn</div>
            <div class="kpi-value" style="color: #9333ea;">{summary.get('rate', 0)}%</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 35px;">STT</th>
                <th style="width: 140px;">Học Sinh</th>
                <th style="width: 65px;">Mã HS</th>
                <th style="width: 80px;">Lớp Học</th>
                <th style="width: 80px;">CM Phụ Trách</th>
                <th style="width: 90px;">Hạn Hết Phí</th>
                <th style="width: 80px;">Gói Tái Phí</th>
                <th style="width: 95px;">Trạng Thái</th>
                <th style="width: 85px;">Ngày Hoàn Thành</th>
                <th>Nhật Ký Chăm Sóc & Tương Tác Gần Nhất</th>
            </tr>
        </thead>
        <tbody>
            {rows_html if rows_html else '<tr><td colspan="10" style="text-align: center; padding: 20px; color: #888;">Không có dữ liệu tái phí cho tháng này.</td></tr>'}
        </tbody>
    </table>

    <!-- Watermark Footer -->
    <div style="margin-top: 26px; border-top: 1.5px dashed #cbd5e1; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; color: #64748b;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <img src="/static/images/logo.jpg" style="width: 16px; height: 16px; object-fit: contain;">
            <strong>Trung tâm Anh ngữ Vicare</strong> - Hệ thống báo cáo theo dõi tái phí chính thức
        </div>
        <div>✨ Thiết kế bởi: <strong style="color: #0284c7; font-weight: 800;">Nhi Phương</strong></div>
    </div>
</body>
</html>'''
        return html
    except Exception as e:
        logger.error(f"Error generating renewal pdf report: {e}")
        return f"<h1>Lỗi xuất báo cáo PDF tái phí: {str(e)}</h1>", 500


# ============================================================
# ADMIN AUDIT LOGS & NOTIFICATIONS REST API ENDPOINTS
# ============================================================

@api_bp.route('/admin/audit-logs', methods=['GET'])
def get_admin_audit_logs_route():
    """
    API lấy danh sách Nhật ký hoạt động (Audit Logs) phân trang dành cho Admin.
    """
    try:
        from services.db_service import get_activity_logs_db
        username = request.args.get('username')
        action_type = request.args.get('action_type')
        target_module = request.args.get('target_module')
        search = request.args.get('search')
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)

        res = get_activity_logs_db(
            username=username,
            action_type=action_type,
            target_module=target_module,
            search=search,
            limit=limit,
            offset=offset
        )
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_admin_audit_logs_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/notifications', methods=['GET'])
def get_admin_notifications_route():
    """
    API lấy danh sách Thông báo thời gian thực & Unread Badge Count dành cho Admin.
    """
    try:
        from services.db_service import get_admin_notifications_db
        limit = request.args.get('limit', type=int, default=20)
        res = get_admin_notifications_db(limit=limit)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_admin_notifications_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/admin/notifications/mark-read', methods=['POST'])
def mark_admin_notifications_read_route():
    """
    API đánh dấu thông báo là đã đọc bởi Admin.
    """
    try:
        from services.db_service import mark_admin_notifications_read_db
        data = request.get_json(silent=True) or {}
        log_ids = data.get('log_ids')
        res = mark_admin_notifications_read_db(log_ids=log_ids)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in mark_admin_notifications_read_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/staff/list', methods=['GET'])
def get_staff_list_route():
    """
    API lấy danh sách Giáo viên (GV) và Phụ trách (CM) động từ CSDL SQLite.
    """
    try:
        from services.db_service import get_staff_list_db
        res = get_staff_list_db()
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in get_staff_list_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/staff/update', methods=['POST'])
def update_staff_name_route():
    """
    API đổi tên nhân sự (GV/CM) và tự động cascade cập nhật tất cả lớp học cũ.
    """
    try:
        from services.db_service import update_staff_name_db
        data = request.get_json(silent=True) or {}
        old_name = data.get('old_name')
        new_name = data.get('new_name')
        role = data.get('role')
        res = update_staff_name_db(old_name, new_name, role)
        return jsonify(res)
    except Exception as e:
        logger.error(f"Error in update_staff_name_route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500




