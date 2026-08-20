# 🚀 HƯỚNG DẪN CHUYỂN GIAO & CÀI ĐẶT EVI DASHBOARD TRÊN MÁY SERVER MỚI

Tài liệu này hướng dẫn chi tiết từng bước chuyển toàn bộ hệ thống Web EVI sang máy tính server mới (máy mới hoàn toàn chỉ có Antigravity/Windows).

---

## 📌 TỔNG QUAN QUY TRÌNH (3 BƯỚC SIÊU NHANH)

```
[Máy Hiện Tại (Dev)]                           [Máy Server Mới]
        │                                             │
        ▼ (1. Push Git)                               ▼ (2. Clone Git)
 GitHub Repository  ─────────────────────────►  Tải thư mục Web_Evi
 (Chứa Code + CSDL)                                   │
                                                      ▼ (3. Chạy 1-Click)
                                            1_CAI_DAT_SERVER_TU_DONG.bat
                                                      │
                                                      ▼ (Khởi chạy 24/7)
                                            2_CHAY_SERVER_VA_LINK_ONLINE.bat
```

---

## 🛠️ CHI TIẾT CÁC BƯỚC THỰC HIỆN TRÊN MÁY SERVER MỚI

### BƯỚC 1: Lấy Mã Nguồn Về Máy Server Mới (Bằng Git)

1. Trên máy Server mới, mở **Antigravity** (hoặc mở cửa sổ **Terminal / PowerShell**).
2. Kiểm tra Git (nếu máy mới chưa có Git, bạn có thể tải nhanh Git tại [git-scm.com](https://git-scm.com/download/win) hoặc chạy lệnh trong PowerShell: `winget install Git.Git`).
3. Chạy lệnh sau để clone toàn bộ dự án về máy:
   ```bash
   git clone https://github.com/nhiphuong3008/Web_Evi.git
   cd Web_Evi
   ```

---

### BƯỚC 2: Cài Đặt Môi Trường Tự Động 100% (Chỉ Làm 1 Lần Đầu)

1. Mở thư mục dự án `Web_Evi` vừa tải về trên máy Server.
2. **Nhấp đúp chuột vào file**:
   👉 `1_CAI_DAT_SERVER_TU_DONG.bat`

3. **Hệ thống sẽ tự động thực hiện toàn bộ:**
   - ✅ Tự tải và cài đặt Python 3.12 (nếu máy chưa có).
   - ✅ Tự tạo môi trường ảo `venv`.
   - ✅ Tự cài đặt toàn bộ thư viện backend (Flask, SQLAlchemy, Pandas/Openpyxl, Google Auth...).
   - ✅ Tự tải công cụ Cloudflare Tunnel (`cloudflared.exe`) để tạo link Online.
   - ✅ Tự tạo file cấu hình `.env`.
   - ✅ Tự mở cổng Firewall Windows (5001) cho mạng nội bộ.

*(Quá trình cài đặt mất khoảng 1-2 phút tùy tốc độ mạng).*

---

### BƯỚC 3: Khởi Chạy Server & Lấy Link Online 24/7

1. **Nhấp đúp chuột vào file**:
   👉 `2_CHAY_SERVER_VA_LINK_ONLINE.bat`

2. Màn hình console màu xanh sẽ hiện lên và cung cấp ngay **3 đường link truy cập**:

| Mục đích | Đường Link | Đối tượng sử dụng |
| :--- | :--- | :--- |
| **Máy Server này** | `http://127.0.0.1:5001` | Bạn xem trực tiếp trên máy chủ |
| **Mạng Wi-Fi nội bộ (LAN)** | `http://192.168.x.x:5001` | Các máy tính, điện thoại cùng bắt Wi-Fi trung tâm |
| **🌐 Link Online 24/7 (Public HTTPS)** | `https://xxxx-yyyy.trycloudflare.com` | **Giáo viên, CM, phụ huynh truy cập từ xa bất kỳ đâu (như PythonAnywhere)** |

> 💡 **Mẹo**: Cửa sổ này giữ mở để Server hoạt động 24/7. Bạn có thể thu nhỏ (Minimize) xuống thanh Taskbar.

---

### BƯỚC 4: Cách Cập Nhật Code Mới Sau Này (Như PythonAnywhere)

Mỗi khi bạn sửa code trên máy Dev và đẩy lên GitHub:
- Trên máy Server, bạn chỉ cần nhấp đúp file:
  👉 `3_CAP_NHAT_CODE.bat`
- Toàn bộ tính năng mới nhất sẽ được kéo về (`git pull`) và tự khởi động lại server trong 3 giây!

---

## 🔒 LƯU Ý VỀ FILE BẢO MẬT (`credentials.json` & `.env`)

1. **CSDL SQLite (`database/evi_center.db`)**: Đã được đồng bộ sẵn 100% trong Git, máy mới chạy ngay mà không cần cấu hình thêm CSDL.
2. **Google Sheets Sync (Nếu dùng)**: Nếu bạn muốn Server tự động đồng bộ Google Sheets 1 tiếng/lần, hãy copy file `credentials.json` từ máy cũ sang thư mục gốc của máy Server mới. Nếu không có file này, hệ thống vẫn chạy 100% ổn định trên CSDL SQLite độc lập.

---

## 🛑 CÁC FILE LỆNH NHANH (QUICK REFERENCE)

| File | Công Dụng |
| :--- | :--- |
| `1_CAI_DAT_SERVER_TU_DONG.bat` | Cài đặt toàn bộ môi trường từ đầu (chỉ chạy 1 lần đầu) |
| `2_CHAY_SERVER_VA_LINK_ONLINE.bat` | Bật Web Server + Mở link Online 24/7 |
| `3_CAP_NHAT_CODE.bat` | Kéo code mới nhất từ GitHub về máy Server |
| `4_DUNG_SERVER.bat` | Tắt Server và link Online khi không dùng |
