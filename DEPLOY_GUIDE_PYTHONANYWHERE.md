# 🚀 HƯỚNG DẪN TRIỂN KHAI EVI DASHBOARD LÊN PYTHONANYWHERE (FREE 24/7)

> **Mục tiêu**: Đưa website EVI Dashboard lên đám mây PythonAnywhere chạy online 24/7 hoàn toàn miễn phí, lưu giữ CSDL SQLite (`evi_center.db`) an toàn không lo mất dữ liệu.

---

## 📌 BƯỚC 1: ĐĂNG KÝ TÀI KHOẢN MIỄN PHÍ

1. Truy cập đường link đăng ký: [https://www.pythonanywhere.com/registration/register/beginner/](https://www.pythonanywhere.com/registration/register/beginner/)
2. Điền thông tin:
   - **Username**: Tên viết liền không dấu (Ví dụ: `evicenter`, `vicareedu`...). 
     *(⚠️ Tên này sẽ quyết định link web của bạn: `https://<username>.pythonanywhere.com`)*
   - **Email & Mật khẩu**.
3. Nhấp vào link kích hoạt trong Email gửi về từ PythonAnywhere để xác thực.

---

## 📌 BƯỚC 2: TẢI CODE DỰ ÁN LÊN PYTHONANYWHERE

### Cách nhanh nhất (Dùng File Zip):
1. Trên máy tính của bạn, nén toàn bộ thư mục `Web_Evi` thành file `Web_Evi.zip` *(không cần nén thư mục rác nếu có)*.
2. Đăng nhập vào PythonAnywhere ➔ Vào mục **Files** trên thanh menu trên cùng.
3. Ở ô **Upload a file**, chọn file `Web_Evi.zip` và bấm **Upload**.
4. Vào mục **Consoles** trên thanh menu ➔ Bấm vào **Bash** để mở cửa sổ dòng lệnh Linux.
5. Gõ lệnh giải nén:
   ```bash
   unzip Web_Evi.zip -d Web_Evi
   ```

---

## 📌 BƯỚC 3: TẠO MÔI TRƯỜNG ẢO & CÀI ĐẶT THƯ VIỆN

Trong cửa sổ dòng lệnh **Bash Console** vừa mở ở Bước 2, gõ lần lượt 3 lệnh sau:

```bash
# 1. Tạo môi trường ảo Python
mkvirtualenv --python=/usr/bin/python3.10 evi-venv

# 2. Di chuyển vào thư mục code
cd ~/Web_Evi

# 3. Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```
*(Chờ khoảng 1-2 phút để hệ thống cài đặt xong toàn bộ Flask, SQLAlchemy, Google Auth...)*

---

## 📌 BƯỚC 4: CẤU HÌNH WEB APP TRÊN TAB "WEB"

1. Nhấp vào tab **Web** trên thanh menu của PythonAnywhere.
2. Bấm nút **Add a new web app** ➔ Chọn **Next** ➔ Chọn **Manual configuration** ➔ Chọn **Python 3.10** ➔ Bấm **Next**.
3. Sau khi tạo xong, cuộn xuống trang cấu hình và điền các mục sau:

### 🔹 Mục Code:
- **Source code**: `/home/<username>/Web_Evi` *(thay `<username>` bằng tên tài khoản của bạn)*
- **Working directory**: `/home/<username>/Web_Evi`

### 🔹 Mục Virtualenv:
- Nhấp vào ô nhập và điền: `/home/<username>/.virtualenvs/evi-venv`

### 🔹 Mục Static files (Để tải ảnh, CSS và JavaScript nhanh):
- Nhấp **Enter URL**: `/static/`
- Nhấp **Enter path**: `/home/<username>/Web_Evi/static`

### 🔹 Mục WSGI configuration file:
1. Nhấp vào đường link file màu xanh (Dạng: `/var/www/<username>_pythonanywhere_com_wsgi.py`).
2. Xóa sạch toàn bộ nội dung mặc định trong file đó, dán đoạn mã sau vào:

```python
import sys
import os

# Đường dẫn tới thư mục dự án của bạn
username = '<username>'  # Thay bằng tên tài khoản PythonAnywhere của bạn
project_home = f'/home/{username}/Web_Evi'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Nạp ứng dụng Flask
from app import app as application
```
3. Bấm nút **Save** (góc trên bên phải) để lưu lại.

---

## 📌 BƯỚC 5: KHỞI CHẠY VÀ TRUY CẬP WEBSITE

1. Quay lại tab **Web**.
2. Bấm vào nút màu xanh lá cây to: **Reload <username>.pythonanywhere.com**.
3. Truy cập vào link web của bạn:
   👉 **`https://<username>.pythonanywhere.com`**

Website của bạn hiện đã chạy online 24/7 trên Cloud, có sẵn chứng chỉ bảo mật HTTPS (khóa xanh) và lưu trữ dữ liệu SQLite hoàn toàn an toàn!
