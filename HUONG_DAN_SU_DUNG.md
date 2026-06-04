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

### 4. Bật/tắt tiêu chí trên dashboard

Dashboard hiện có 3 tiêu chí:

```text
MCDX Banker + RRG Quadrant + ADX Trend = Tổng điểm
```

Có thể bật/tắt từng tiêu chí ở:

- Thanh tiêu chí trên header.
- Checkbox ngay trong table header của các cột `MCDX Score`, `RRG Score`, `ADX Score`.

Khi tắt một tiêu chí:

- `total_score` được tính lại ngay trên frontend.
- `score_max` co lại theo tiêu chí còn bật.
- Cột bị tắt sẽ mờ đi để dễ nhận biết.
- Bảng xếp hạng và chart lịch sử vẽ lại theo điểm động.
- Hệ thống không cho tắt cả 3 tiêu chí cùng lúc.

Lưu ý: thao tác bật/tắt này chỉ là phân tích trên giao diện, không ghi đè dữ liệu gốc trong SQLite hoặc JSON.

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
symbol=VCB;banker=6.387589;hotmoney=17.873365;rs_ratio=-0.638458;rs_mom=1.340996;quadrant=4;tail_5d=2.147165;adx=32.935825;di_plus=34.524944;di_minus=11.045899;adx_1d=31.506115;adx_3d=28.602303;ready=1
```

## Cách hiểu điểm

- `mcdx_score`: điểm dòng tiền Banker, tối đa 1.0.
- `rrg_score`: điểm vùng RRG, tối đa 1.0.
- `adx_score`: điểm xu hướng nội tại từ ADX/DI, tối đa 0.5 trong V1.
- `extra_score`: tổng các điểm mở rộng ngoài MCDX/RRG, hiện gồm ADX.
- `total_score = mcdx_score + rrg_score + adx_score`.
- `score_max = 2.5`.
- Checkbox trên giao diện có thể tạm loại một hoặc nhiều component khỏi `total_score` để so sánh ranking.

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
