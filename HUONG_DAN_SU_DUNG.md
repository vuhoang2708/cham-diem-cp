# Hướng dẫn sử dụng dashboard VN30 AmiBroker

Mục tiêu hiện tại: chấm điểm **các cổ phiếu trong rổ VN30**, không tính giá trị chỉ số VN30.

## Vận hành hàng ngày

### 1. Mở AmiBroker

- Mở AmiBroker trước khi chạy backend.
- Đảm bảo database đang dùng có đủ mã VN30 và benchmark `VNINDEX`.
- Đảm bảo FireAnt plugin hoạt động trong AmiBroker: `FA_MCDX`, `FA_RRG`.

### 2. Chạy dashboard local

Từ thư mục gốc dự án:

```powershell
cd backend
$env:DATA_SOURCE="amibroker"
$env:AMIBROKER_TIMEOUT="360"
..\venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở:

```text
http://127.0.0.1:8000/
```

### 3. Cập nhật điểm

- Trong dashboard local, chọn tab VN30.
- Bấm **Cập nhật ngay**.
- Backend sẽ chạy `run_amibroker_vn30.py`, ghi 30 file output từ AmiBroker, lưu SQLite và export JSON.
- Trên Vercel, dashboard đọc `frontend/data_vn30.json` đã push lên GitHub.

Chạy tay nếu không muốn dùng nút dashboard:

```powershell
.\venv\Scripts\python backend\run_amibroker_vn30.py --timeout 360
```

## Link public

```text
https://cham-diem-cp.vercel.app
```

## File chứng cứ runtime

Khi batch chạy thành công, mỗi mã VN30 có một file:

```text
C:\Users\Public\ag_vn30_bridge\ami_vn30_<SYMBOL>.txt
```

Ví dụ nội dung:

```text
symbol=VCB;banker=5.891842;hotmoney=17.589798;rs_ratio=-1.213547;rs_mom=0.990822;quadrant=4;tail_5d=1.798761;ready=1
```

## Cách hiểu điểm

- `mcdx_score`: điểm dòng tiền Banker, tối đa 1.0.
- `rrg_score`: điểm vùng RRG, tối đa 1.0.
- `adx_score`: điểm xu hướng nội tại từ ADX/DI, tối đa 0.5 trong V1.
- `extra_score`: tổng các điểm mở rộng ngoài MCDX/RRG, hiện gồm ADX.
- `total_score = mcdx_score + rrg_score + adx_score`.
- `score_max = 2.5`.

## Lỗi thường gặp

### AmiBroker không chạy hoặc COM không kết nối

Mở AmiBroker trước, rồi chạy lại backend hoặc batch script.

### Dashboard không tự refresh

Kiểm tra backend local ở:

```text
http://127.0.0.1:8000/api/scores?category=vn30
```

Nếu chỉ mở Vercel thì nút refresh bị ẩn hoặc không chạy backend local. Muốn cập nhật Vercel thì chạy batch local, commit/push `frontend/data_vn30.json`.

### AmiBroker báo lỗi không mở formula

Bridge mới đã tránh lỗi `FormulaPath` rỗng. File runtime cần tồn tại ở:

```text
D:\MetakitData\AmibrokerFA\EOD\Formulas\Imported\ag_vn30_bridge.afl
C:\Users\Public\ag_vn30_bridge.apx
```
