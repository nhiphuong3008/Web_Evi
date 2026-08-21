# 🚀 HƯỚNG DẪN TRIỂN KHAI SERVER MỚI TỪ ĐẦU (TRẮNG TINH)

> **Tài liệu chuyển giao hệ thống Vicare CRM Dashboard cho máy Server Windows mới.**

---

## 📋 TỔNG QUAN QUY TRÌNH (3 BƯỚC CỰC KỲ ĐƠN GIẢN)

```
[BƯỚC 1] Cài Git & Python ➔ [BƯỚC 2] Clone Code & Dữ liệu CSDL ➔ [BƯỚC 3] Chạy Server 24/7
```

---

## 📥 BƯỚC 1: Cài đặt công cụ nền tảng (Git & Python 3.12)

1. Trên máy tính mới, bấm nút **Windows** (hoặc ô tìm kiếm góc trái dưới) ➔ gõ chữ **`powershell`**.
2. **Nhấp chuột phải** vào **Windows PowerShell** ➔ Chọn **"Run as administrator"** (Chạy dưới quyền Quản trị viên).
3. Copy toàn bộ đoạn lệnh sau, dán vào cửa sổ PowerShell rồi bấm **Enter**:

```powershell
# 1. Cài đặt Git và Python 3.12 tự động
winget install --id Git.Git -e --source winget; winget install --id Python.Python.3.12 -e --source winget

# 2. Thêm ngoại lệ cho thư mục C:\Vicare_web để Windows Defender không chặn công cụ mạng
Add-MpPreference -ExclusionPath "C:\Vicare_web" -ErrorAction SilentlyContinue
```

*(Chờ khoảng 1 phút cho máy tải và cài đặt hoàn tất).*

---

## 📦 BƯỚC 2: Tải Mã Nguồn & Toàn Bộ CSDL Về Ổ Đĩa C:

1. **Đóng cửa sổ PowerShell cũ lại**.
2. **Mở một cửa sổ PowerShell mới** (để máy tính nhận diện lệnh `git` và `python`).
3. Copy toàn bộ đoạn lệnh sau, dán vào PowerShell rồi bấm **Enter**:

```powershell
git clone https://github.com/nhiphuong3008/Web_Evi.git C:\Vicare_web
cd C:\Vicare_web
.\1_CAI_DAT_SERVER_TU_DONG.bat
```

*(File cài đặt sẽ tự động tạo môi trường ảo `venv`, cài đầy đủ thư viện `Flask`, `SQLAlchemy`, `openpyxl`, tải `ngrok.exe`, cấu hình token bản quyền và mở cổng Firewall 5001).*

---

## 🌟 BƯỚC 3: Khởi Chạy Server & Mở Link Online 24/7

Tại thư mục `C:\Vicare_web`, bạn chỉ cần nhấp đúp chuột vào file:
👉 **`2_CHAY_SERVER_VA_LINK_ONLINE.bat`**

Hệ thống sẽ tự động:
1. Bật Backend Server trên cổng 5001.
2. Mở đường link Ngrok cố định vĩnh viễn:
   👉 **`https://hardy-porthole-wildland.ngrok-free.dev`**
3. Bật thêm đường link Cloudflare HTTPS dự phòng.
4. Tự động mở trình duyệt lên cho bạn sử dụng ngay!

---

## 🧰 BỘ CÔNG CỤ VẬN HÀNH 1-CLICK TẠI `C:\Vicare_web`:

| Tên file `.bat` | Chức năng |
| :--- | :--- |
| **`0_KIEM_TRA_SERVER.bat`** | 🔍 Rà soát toàn bộ 6 hạng mục hệ thống (Python, venv, packages, SQLite, Ngrok, Port 5001). |
| **`1_CAI_DAT_SERVER_TU_DONG.bat`** | ⚙️ Tự động cài đặt môi trường trọn gói từ A-Z. |
| **`2_CHAY_SERVER_VA_LINK_ONLINE.bat`** | 🚀 Khởi chạy Server Backend và mở Link Online 24/7. |
| **`3_CAP_NHAT_CODE.bat`** | 🔄 Kéo mã nguồn và dữ liệu mới nhất từ GitHub về máy. |
| **`4_DUNG_SERVER.bat`** | 🛑 Tắt hoàn toàn Server và các đường link Tunnel an toàn. |

---

## 🔑 THÔNG TIN ĐĂNG NHẬP MẶC ĐỊNH

- **Tài khoản Quản trị (Admin)**:
  - Tên đăng nhập: `admin`
  - Mật khẩu: `admin123`
- **Tài khoản Class Manager (CM)**:
  - Tên đăng nhập: `ngoccm` / `anhptt` / `anhnv`
  - Mật khẩu: `123456`
