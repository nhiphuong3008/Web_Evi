# 🚀 HUONG DAN TRIEN KHAI SERVER MOI TREN O D: (TRANG TINH)

> **Tai lieu chuyen giao he thong Vicare CRM Dashboard cho may Server Windows moi tai o dia `D:\Vicare_web`.**

---

## 📋 TONG QUAN QUY TRINH (3 BUOC DON GIAN)

```
[BUOC 1] Cai Git, Python va Mo khoa Defender ➔ [BUOC 2] Clone Code ve o D: ➔ [BUOC 3] Chay Server 24/7
```

---

## 📥 BUOC 1: Cai dat cong cu nen tang (Git & Python 3.12)

1. Tren may tinh Server moi, bam nut **Windows** (hoac o tim kiem goc trai duoi) ➔ go chu **`powershell`**.
2. **Nhap chuot phai** vao **Windows PowerShell** ➔ Chon **"Run as administrator"** (Chay duoi quyen Quan tri vien).
3. Copy toan bo doan lenh sau, dan vao cua so PowerShell roi bam **Enter**:

```powershell
# 1. Cai dat Git va Python 3.12 tu dong
winget install --id Git.Git -e --source winget; winget install --id Python.Python.3.12 -e --source winget

# 2. Them ngoai le cho thu muc D:\Vicare_web de Windows Defender khong chan cong cu mang
Add-MpPreference -ExclusionPath "D:\Vicare_web" -ErrorAction SilentlyContinue
Add-MpPreference -ExclusionPath "C:\Vicare_web" -ErrorAction SilentlyContinue
```

*(Cho khoang 1 phut cho may tai va cai dat hoan tat).*

---

## 📦 BUOC 2: Tai Ma Nguon & Toan Bo CSDL Ve O Dia D:

1. **Dong cua so PowerShell cu lai**.
2. **Mo mot cua so PowerShell moi** len.
3. Copy toan bo doan lenh sau, dan vao PowerShell roi bam **Enter**:

```powershell
git clone https://github.com/nhiphuong3008/Web_Evi.git D:\Vicare_web
cd D:\Vicare_web
.\1_CAI_DAT_SERVER_TU_DONG.bat
```

*(File cai dat se tu dong tao moi truong ao `venv`, cai day du thu vien `Flask`, `SQLAlchemy`, `openpyxl`, tai `ngrok.exe`, nap token ban quyen va mo cong Firewall 5001).*

---

## 🌟 BUOC 3: Khoi Chay Server & Mo Link Online 24/7

Tai thu muc `D:\Vicare_web`, ban chi can nhap dup chuot vao file:
👉 **`2_CHAY_SERVER_VA_LINK_ONLINE.bat`**

He thong se tu dong:
1. Bat Backend Server tren cong 5001.
2. Mo duong link Ngrok co dinh vinh vien:
   👉 **`https://hardy-porthole-wildland.ngrok-free.dev`**
3. Bat them duong link Cloudflare HTTPS du phong.
4. Tu dong mo trinh duyet len cho ban su dung ngay!

---

## 🧰 BO CONG CU VAN HANH 1-CLICK TAI `D:\Vicare_web`:

| Ten file `.bat` | Chuc nang |
| :--- | :--- |
| **`0_KIEM_TRA_SERVER.bat`** | 🔍 Ra soat toan bo 6 hang muc he thong (Python, venv, packages, SQLite, Ngrok, Port 5001). |
| **`1_CAI_DAT_SERVER_TU_DONG.bat`** | ⚙️ Tu dong cai dat moi truong tron goi tu A-Z tren o D. |
| **`2_CHAY_SERVER_VA_LINK_ONLINE.bat`** | 🚀 Khoi chay Server Backend va mo Link Online 24/7. |
| **`3_CAP_NHAT_CODE.bat`** | 🔄 Keo ma nguon va du lieu moi nhat tu GitHub ve may. |
| **`4_DUNG_SERVER.bat`** | 🛑 Tat hoan toan Server va cac duong link Tunnel an toan. |

---

## 🔑 THONG TIN DANG NHAP MAC DINH

- **Tai khoan Quan tri (Admin)**:
  - Ten dang nhap: `admin`
  - Mat khau: `admin123`
- **Tai khoan Class Manager (CM)**:
  - Ten dang nhap: `ngoccm` / `anhptt` / `anhnv`
  - Mat khau: `123456`
