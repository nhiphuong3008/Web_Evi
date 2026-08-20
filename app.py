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
    # Khởi tạo CSDL SQLite (100% Standalone SQLite - Go-Live Mode)
    # =========================================================
    from database.db_manager import init_db
    init_db()

    logger.info("🚀 Hệ thống EVI Dashboard hoạt động 100% trên CSDL SQLite cục bộ (Chế độ Go-Live Server độc lập).")

    # Khởi tạo API (Dữ liệu phục vụ 100% từ CSDL SQLite)
    init_api({})

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

