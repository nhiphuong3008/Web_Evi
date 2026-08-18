"""
EVI Dashboard - Google Sheets Service
Kết nối và thao tác dữ liệu với Google Sheets API.
Hỗ trợ đọc/ghi dữ liệu qua Service Account.
"""

import gspread
from google.oauth2.service_account import Credentials
import os
import logging

logger = logging.getLogger(__name__)

# Scopes cần thiết cho đọc/ghi Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
]


class GoogleSheetsService:
    """Service class để tương tác với Google Sheets API."""

    def __init__(self, credentials_file, spreadsheet_id):
        """
        Khởi tạo service.

        Args:
            credentials_file: Đường dẫn đến file credentials JSON (Service Account)
            spreadsheet_id: ID của Google Spreadsheet
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
        self._connected = False

    def connect(self):
        """Kết nối đến Google Sheets API."""
        try:
            if not os.path.exists(self.credentials_file):
                logger.warning(
                    f"Credentials file not found: {self.credentials_file}. "
                    "Running in demo mode with sample data."
                )
                self._connected = False
                return False

            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES
            )
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            self._connected = True
            logger.info("Successfully connected to Google Sheets API")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            self._connected = False
            return False

    @property
    def is_connected(self):
        """Kiểm tra trạng thái kết nối."""
        return self._connected

    def get_all_sheets(self):
        """
        Lấy danh sách tất cả sheets trong spreadsheet.

        Returns:
            list: Danh sách dict {title, id, index}
        """
        if not self._connected:
            return []

        try:
            worksheets = self.spreadsheet.worksheets()
            return [
                {
                    'title': ws.title,
                    'id': ws.id,
                    'index': ws.index,
                    'row_count': ws.row_count,
                    'col_count': ws.col_count,
                }
                for ws in worksheets
            ]
        except Exception as e:
            logger.error(f"Error getting sheets list: {e}")
            return []

    def read_sheet(self, sheet_name=None, sheet_index=0, cell_range=None, spreadsheet_id=None):
        """
        Đọc dữ liệu từ một sheet (hỗ trợ chỉ định spreadsheet_id khác).

        Args:
            sheet_name: Tên sheet (ưu tiên nếu có)
            sheet_index: Index của sheet (mặc định 0)
            cell_range: Range cụ thể (ví dụ: 'A1:F10'), None = toàn bộ
            spreadsheet_id: ID của spreadsheet khác (nếu cần)

        Returns:
            list: Danh sách các hàng (mỗi hàng là list các giá trị)
        """
        if not self._connected:
            return []

        try:
            target_spreadsheet = self.spreadsheet
            if spreadsheet_id and spreadsheet_id != self.spreadsheet_id:
                target_spreadsheet = self.client.open_by_key(spreadsheet_id)

            if sheet_name:
                worksheet = target_spreadsheet.worksheet(sheet_name)
            else:
                worksheet = target_spreadsheet.get_worksheet(sheet_index)

            if cell_range:
                data = worksheet.get(cell_range)
            else:
                data = worksheet.get_all_values()

            return data

        except Exception as e:
            logger.error(f"Error reading sheet: {e}")
            return []

    def write_sheet(self, sheet_name, cell_range, data):
        """
        Ghi dữ liệu vào sheet.

        Args:
            sheet_name: Tên sheet
            cell_range: Vị trí bắt đầu ghi (ví dụ: 'A1')
            data: List of lists - dữ liệu cần ghi

        Returns:
            bool: True nếu thành công
        """
        if not self._connected:
            logger.error("Not connected to Google Sheets")
            return False

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            worksheet.update(cell_range, data)
            logger.info(f"Successfully wrote data to {sheet_name}!{cell_range}")
            return True

        except Exception as e:
            logger.error(f"Error writing to sheet: {e}")
            return False

    def append_row(self, sheet_name, row_data):
        """
        Thêm một hàng mới vào cuối sheet.

        Args:
            sheet_name: Tên sheet
            row_data: List giá trị cho hàng mới

        Returns:
            bool: True nếu thành công
        """
        if not self._connected:
            return False

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            worksheet.append_row(row_data)
            logger.info(f"Successfully appended row to {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error appending row: {e}")
            return False

    def update_cell(self, sheet_name, cell, value):
        """
        Cập nhật giá trị một ô cụ thể.

        Args:
            sheet_name: Tên sheet
            cell: Địa chỉ ô (ví dụ: 'A1')
            value: Giá trị mới

        Returns:
            bool: True nếu thành công
        """
        if not self._connected:
            return False

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            worksheet.update_acell(cell, value)
            logger.info(f"Successfully updated {sheet_name}!{cell}")
            return True

        except Exception as e:
            logger.error(f"Error updating cell: {e}")
            return False

    def batch_update(self, sheet_name, updates):
        """
        Cập nhật nhiều ô cùng lúc.

        Args:
            sheet_name: Tên sheet
            updates: List of dict [{range: 'A1', values: [[...]]}]

        Returns:
            bool: True nếu thành công
        """
        if not self._connected:
            return False

        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            worksheet.batch_update(updates)
            logger.info(f"Successfully batch updated {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error batch updating: {e}")
            return False
