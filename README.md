# Chấm điểm cổ phiếu VN30

Dashboard chấm điểm và xếp hạng **30 cổ phiếu trong rổ VN30** bằng dữ liệu lấy trực tiếp từ AmiBroker.

Baseline hiện tại sau retest ngày 2026-05-20:

- Nguồn dữ liệu chính: AmiBroker COM + FireAnt AFL functions.
- Chỉ báo đang dùng: `FA_MCDX`, `FA_RRG`, `ADX/PDI/MDI`.
- Dashboard local: FastAPI + SQLite + frontend tĩnh.
- Dashboard public: https://cham-diem-cp.vercel.app

## Luồng chính

1. `backend/run_amibroker_vn30.py` đọc `data/vn30_symbols.json`.
2. Script tạo AFL runtime tại `D:\MetakitData\AmibrokerFA\EOD\Formulas\Imported\ag_vn30_bridge.afl`.
3. Script tạo APX runtime tại `C:\Users\Public\ag_vn30_bridge.apx`.
4. AmiBroker chạy Exploration cho toàn bộ database nhưng AFL chỉ ghi output cho 30 mã VN30.
5. Mỗi mã ghi một file chứng cứ tại `C:\Users\Public\ag_vn30_bridge\ami_vn30_<SYMBOL>.txt`.
6. Python parse output, lưu SQLite, export `frontend/data_vn30.json`.
7. Frontend đọc API local hoặc fallback sang JSON tĩnh trên Vercel.

## Cách chạy local

Mở AmiBroker trước, đảm bảo database EOD và FireAnt plugin đã sẵn sàng.

```powershell
cd backend
$env:DATA_SOURCE="amibroker"
$env:AMIBROKER_TIMEOUT="360"
..\venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở dashboard:

```text
http://127.0.0.1:8000/
```

Có thể chạy batch VN30 trực tiếp:

```powershell
.\venv\Scripts\python backend\run_amibroker_vn30.py --timeout 360
```

## Scoring hiện tại

Điểm tổng hiện được cộng từ các component trong `backend/scoring.py`.

| Component | Nguồn | Thang điểm |
|---|---|---|
| `mcdx_score` | `FA_MCDX(50, 1.5, 50, 20)` Banker | 0.00 - 1.00 |
| `rrg_score` | Quadrant từ `FA_RRG(C, VNINDEX, ...)` | 0.25 - 1.00 |
| `adx_score` | `ADX(14)` + `PDI(14)`/`MDI(14)` | 0.00 - 0.50 |
| `extra_score` | Tổng các điểm mở rộng ngoài MCDX/RRG | Hiện gồm ADX |

Quy đổi RRG:

| Vùng | Điều kiện FA_RRG native | Điểm |
|---|---|---|
| TĂNG GIÁ | `rs_ratio >= 0`, `rs_mom >= 0` | 1.00 |
| TÍCH LŨY | `rs_ratio < 0`, `rs_mom >= 0` | 0.75 |
| SUY YẾU | `rs_ratio >= 0`, `rs_mom < 0` | 0.50 |
| GIẢM GIÁ | `rs_ratio < 0`, `rs_mom < 0` | 0.25 |

### ADX V1

ADX chỉ cộng điểm khi `DI+ > DI-`. Điểm nền dùng thang bậc, có thưởng/phạt theo ADX hôm qua và ADX 3 ngày trước. V1 giới hạn ADX tối đa `0.5` điểm để tránh double-count xu hướng với RRG.

```text
total_score = mcdx_score + rrg_score + adx_score
score_max = 2.5
```

## Chuẩn bị mở rộng chỉ báo

Khi cần cộng thêm chỉ báo mới vào điểm:

1. Lấy thêm giá trị trong AFL runtime hoặc Python connector.
2. Viết hàm quy đổi giá trị đó thành điểm 0-1 trong `backend/scoring.py`.
3. Truyền component mới vào `build_score_payload(extra_components={...})`.
4. Lưu qua `database.save_score`; schema đã có `extra_score`, `score_max`, `score_components`.
5. Frontend đã đọc `rrg_score` riêng và dùng `score_max`, nên thêm điểm mới không làm sai cột RRG.

## File quan trọng

- `backend/run_amibroker_vn30.py`: batch bridge AmiBroker cho VN30.
- `backend/scoring.py`: nơi quản lý công thức cộng điểm.
- `backend/database.py`: SQLite + JSON export.
- `backend/main_scorer.py`: endpoint refresh gọi bridge AmiBroker khi `DATA_SOURCE=amibroker`.
- `frontend/data_vn30.json`: dữ liệu public cho Vercel.
- `CHANGES_20260520.md`: ghi chú retest và nguyên nhân lỗi APX cũ.
