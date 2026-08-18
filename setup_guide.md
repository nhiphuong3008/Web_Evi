# Hướng Dẫn Cài Đặt EVI Dashboard

## 1. Cài đặt Python Dependencies

```bash
cd c:\Users\nhiph\OneDrive\Documents\Web_Evi
pip install -r requirements.txt
```

## 2. Cài đặt Google Sheets API (Service Account)

### Bước 1: Tạo Google Cloud Project
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Đặt tên: `EVI Dashboard` → **Create**

### Bước 2: Bật APIs
1. Vào **APIs & Services** → **Library**
2. Tìm và bật:
   - **Google Sheets API**
   - **Google Drive API**

### Bước 3: Tạo Service Account
1. Vào **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"Service Account"**
3. Đặt tên: `evi-dashboard` → **Create and Continue**
4. Role: Bỏ qua (Skip) → **Done**

### Bước 4: Download Credentials
1. Click vào Service Account vừa tạo
2. Tab **"Keys"** → **"Add Key"** → **"Create New Key"**
3. Chọn **JSON** → **Create**
4. File JSON sẽ tự download

### Bước 5: Đặt file credentials
1. Đổi tên file download thành `credentials.json`
2. Copy vào thư mục project: `c:\Users\nhiph\OneDrive\Documents\Web_Evi\`

### Bước 6: Chia sẻ Google Sheet
1. Mở file `credentials.json`, tìm trường `client_email` (dạng: `xxx@xxx.iam.gserviceaccount.com`)
2. Mở Google Sheet, click **Share** (Chia sẻ)
3. Thêm email Service Account với quyền **Editor**

## 3. Chạy ứng dụng

```bash
python app.py
```

Mở browser: **http://127.0.0.1:5000**

## 4. Chế độ Demo

Nếu chưa setup Google Sheets credentials, ứng dụng sẽ chạy ở **chế độ Demo** với dữ liệu mẫu (lấy từ dữ liệu thực trên Google Sheet). Bạn vẫn có thể xem giao diện dashboard đầy đủ.

## Lưu ý bảo mật

⚠️ **KHÔNG BAO GIỜ commit file `credentials.json` lên Git!**
File `.gitignore` đã được cấu hình để bỏ qua file này.
