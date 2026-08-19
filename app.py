"""
EVI Dashboard - Main Application
Flask server chính cho hệ thống quản lý trung tâm tiếng Anh.
"""

import os
import sys
import logging
from flask import Flask, send_from_directory

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from flask_cors import CORS
from config import get_config
from services.google_sheets import GoogleSheetsService
from services.data_parser import DataParser, get_demo_data
from routes.api import api_bp, init_api

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Factory function tạo Flask app."""
    config = get_config()

    app = Flask(
        __name__,
        static_folder='static',
        static_url_path='/static'
    )
    app.config.from_object(config)

    # CORS - cho phép frontend gọi API
    CORS(app)

    # =========================================================
    # Khởi tạo CSDL SQLite & Background Sync Scheduler
    # =========================================================
    from database.db_manager import init_db
    init_db()

    sheets_service = GoogleSheetsService(
        credentials_file=config.GOOGLE_SHEETS_CREDENTIALS_FILE,
        spreadsheet_id=config.GOOGLE_SHEETS_SPREADSHEET_ID,
    )
    connected = sheets_service.connect()
    app.config['SHEETS_SERVICE'] = sheets_service

    if connected:
        logger.info("✅ Kết nối Google Sheets API thành công (dành cho Background Sync).")
    else:
        logger.warning("⚠️ Không tìm thấy credentials.json hoặc kết nối Google Sheets không thành công. Sử dụng 100% dữ liệu SQLite CSDL local.")

    # Khởi tạo API (Dữ liệu phục vụ 100% từ CSDL SQLite)
    init_api({})

    # =========================================================
    # Bật Background Sync Scheduler (Tự động quét Sheet ➔ DB 1 tiếng/lần)
    # =========================================================
    from services.sync_scheduler import start_background_sync
    start_background_sync(app, interval_seconds=3600)

    # =========================================================
    # Register Blueprints
    # =========================================================
    app.register_blueprint(api_bp)

    # =========================================================
    # Serve Frontend
    # =========================================================
    @app.route('/')
    def index():
        """Trang chính."""
        return send_from_directory('static', 'index.html')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            from database.db_manager import db_session
            db_session.remove()
        except Exception:
            pass

    return app


# =========================================================
# WSGI Application Instance & Main Entry
# =========================================================
app = create_app()
application = app

if __name__ == '__main__':
    config = get_config()

    # Tự động đồng bộ CSDL từ Production Host khi chạy trực tiếp trên máy Local
    is_cloud_host = 'PYTHONANYWHERE_DOMAIN' in os.environ or 'PYTHONANYWHERE_SITE' in os.environ
    if getattr(config, 'AUTO_SYNC_DB_ON_STARTUP', False) and not is_cloud_host:
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            try:
                from services.sync_host_db import sync_db_from_host
                sync_db_from_host(
                    host_url=getattr(config, 'PRODUCTION_HOST_URL', 'https://vicarecrm.pythonanywhere.com'),
                    secret_token=getattr(config, 'SYNC_SECRET_TOKEN', 'evi_secure_sync_token_2026_x9k2'),
                    verbose=True
                )
            except Exception as sync_err:
                logger.warning(f"Không thể tự động đồng bộ DB từ Host lúc khởi động: {sync_err}")

    print("\n" + "=" * 60)
    print("  🏫 Trung tâm Anh ngữ Vicare - Hệ Thống Quản Lý Trung Tâm")
    print("=" * 60)
    print(f"  🌐 Server: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"  📊 API:    http://{config.FLASK_HOST}:{config.FLASK_PORT}/api/health")
    print(f"  🔧 Debug:  {config.FLASK_DEBUG}")
    print("=" * 60 + "\n")

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
    )

