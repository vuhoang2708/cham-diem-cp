# Technical Specification: VN30 AmiBroker Scoring Dashboard

## 1. Baseline

Hệ thống hiện lấy dữ liệu từ AmiBroker để chấm điểm tập hợp cổ phiếu trong rổ VN30.

- Data source chính: AmiBroker COM automation.
- AFL functions: `FA_MCDX`, `FA_RRG`.
- Backend: FastAPI, SQLite.
- Frontend: HTML/CSS/JS tĩnh, dùng API local hoặc fallback JSON.
- Public deployment: Vercel đọc `frontend/data_vn30.json`.

## 2. Data Flow

1. `backend/run_amibroker_vn30.py` đọc danh sách mã từ `data/vn30_symbols.json`.
2. Script ghi AFL runtime vào AmiBroker Formulas folder.
3. Script ghi APX runtime vào `C:\Users\Public\ag_vn30_bridge.apx`.
4. `AnalysisDoc.Run(1)` chạy Exploration.
5. AFL chỉ ghi file cho symbol nằm trong VN30.
6. Python đợi đủ `ready=1` cho 30 output files.
7. Python parse key-value output, tính điểm, lưu SQLite.
8. `database.export_to_json("vn30")` ghi `frontend/data_vn30.json`.

## 3. Database

SQLite file:

```text
data/scores.db
```

Table `scores`, primary key:

```text
(symbol, category, updated_date)
```

Các cột chính:

| Column | Meaning |
|---|---|
| `symbol` | Mã cổ phiếu |
| `category` | `vn30`, `vn100`, `custom` |
| `total_score` | Tổng điểm đã cộng các component |
| `mcdx_score` | Điểm MCDX Banker |
| `rrg_score` | Điểm RRG quadrant |
| `adx_score` | Điểm ADX V1, tối đa 0.5 |
| `extra_score` | Tổng điểm từ các component mở rộng, hiện gồm ADX |
| `score_max` | Điểm tối đa lý thuyết của bộ component hiện tại |
| `score_components` | JSON chi tiết từng component score |
| `banker_value`, `banker_left`, `banker_right` | Giá trị MCDX |
| `rrg_quadrant`, `rs_ratio`, `rs_mom`, `tail_5d` | Dữ liệu RRG |
| `adx_value`, `di_plus`, `di_minus`, `adx_1d`, `adx_3d` | Raw ADX/DMI audit fields |
| `updated_at`, `updated_date` | Timestamp lưu kết quả |

`init_db()` có migration nhẹ để thêm các cột scoring mở rộng nếu database cũ chưa có.

## 4. Scoring Engine

File trung tâm:

```text
backend/scoring.py
```

Baseline:

```text
total_score = mcdx_score + rrg_score + extra_score
```

Hiện tại:

- `mcdx_score`: 0.00 - 1.00.
- `rrg_score`: 0.25 - 1.00.
- `adx_score`: 0.00 - 0.50.
- `extra_score`: hiện bằng `adx_score`.
- `score_max`: 2.50.

MCDX Banker dùng breakpoints:

```text
0 -> 0.0
3 -> 0.2
8 -> 0.4
12 -> 0.6
16 -> 0.8
20 -> 1.0
```

RRG dùng output native của `FA_RRG`, trục chia tại `0`, không phải `100`.

| Quadrant | Condition | Score |
|---|---|---|
| TĂNG GIÁ | `rs_ratio >= 0` and `rs_mom >= 0` | 1.00 |
| TÍCH LŨY | `rs_ratio < 0` and `rs_mom >= 0` | 0.75 |
| SUY YẾU | `rs_ratio >= 0` and `rs_mom < 0` | 0.50 |
| GIẢM GIÁ | `rs_ratio < 0` and `rs_mom < 0` | 0.25 |

ADX V1:

- Nếu `DI+ <= DI-`: `adx_score = 0`.
- ADX base dùng thang bậc: `<15 = 0`, `15-20 = 0.10`, `20-25 = 0.30`, `25-40 = 0.60`, `40-50 = 0.80`, `50+ = 0.90`.
- Cộng/trừ theo `ADX_today - ADX_yesterday`, `ADX_today - ADX_3d`, và `DI+ - DI-`.
- Raw score được nhân `0.5`, nên ADX tối đa 0.5 điểm.

## 5. Adding New Indicators

Khi thêm chỉ báo mới:

1. Bổ sung giá trị raw vào AFL output hoặc Python connector.
2. Thêm hàm scoring trong `backend/scoring.py`.
3. Gọi `build_score_payload(extra_components={"new_indicator": score})`.
4. Nếu cần hiển thị raw value, thêm cột DB hoặc JSON field riêng.
5. Frontend không được tính RRG bằng `total_score - mcdx_score`; hiện đã dùng `rrg_score` riêng để tránh sai khi có component mới.

## 6. API

| Endpoint | Purpose |
|---|---|
| `GET /api/scores?category=vn30` | Lấy bảng điểm mới nhất |
| `GET /api/history?symbol=VCB` | Lấy lịch sử theo mã |
| `POST /api/refresh?category=vn30` | Chạy refresh local |
| `POST /api/import` | Lưu danh sách custom |

Với `DATA_SOURCE=amibroker` và `category=vn30`, refresh gọi trực tiếp `run_vn30_scoring()`.

## 7. Runtime Requirements

- Windows.
- AmiBroker đang mở.
- FireAnt plugin đã cài và chạy được `FA_MCDX`, `FA_RRG`.
- Python venv có `fastapi`, `uvicorn`, `pywin32`.
- AmiBroker formulas directory hiện dùng:

```text
D:\MetakitData\AmibrokerFA\EOD\Formulas
```
