# AUDIT REPORT — Chấm Điểm Cổ Phiếu VN30

**Ngày audit:** 2026-06-04  
**Auditor:** Claude AI (Sonnet 4.6)  
**Phiên bản:** commit `6ca2867`  
**Môi trường:** Windows 11, Python/FastAPI backend, Vanilla JS frontend

---

## 1. TỔNG QUAN DỰ ÁN

| Mục | Giá trị |
|---|---|
| Mục tiêu | Dashboard chấm điểm & xếp hạng 30 cổ phiếu VN30 theo chỉ báo kỹ thuật |
| Nguồn dữ liệu | AmiBroker COM + FireAnt AFL functions |
| Chỉ báo | MCDX (Banker), RRG (Quadrant), ADX/DI+/DI- |
| Backend | FastAPI + SQLite + Python |
| Frontend | Vanilla HTML/CSS/JS (static deploy on Vercel) |
| Deploy public | https://cham-diem-cp.vercel.app |
| Loại project | Internal tool / MVP prototype |

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1 Data Flow

```
AmiBroker (AFL runtime)
    ↓ write file
C:\Users\Public\ag_vn30_bridge\ami_vn30_<SYMBOL>.txt  (key=value format)
    ↓ parse (run_amibroker_vn30.py)
SQLite (data/scores.db)
    ↓ export
frontend/data_vn30.json  →  Vercel (public, static fallback)
    ↑
FastAPI /api/scores  →  Frontend local
```

### 2.2 Component Map

| File | Vai trò | Trạng thái |
|---|---|---|
| `backend/main.py` | FastAPI app, 5 endpoints | Stable |
| `backend/main_scorer.py` | Orchestrator AmiBroker/Fireant | Stable |
| `backend/scoring.py` | Công thức quy đổi điểm | Stable |
| `backend/database.py` | SQLite CRUD + JSON export | Stable |
| `backend/run_amibroker_vn30.py` | AmiBroker batch bridge | Stable |
| `backend/scraper_amibroker.py` | AmiBroker COM connector | Stable |
| `backend/scraper_mcdx.py` | Legacy Playwright/Fireant | Legacy (fallback) |
| `backend/calculator_rrg.py` | RRG tính tay (Fireant mode) | Legacy |
| `frontend/app.js` | Dynamic scoring UI logic | Stable |
| `frontend/index.html` | Dashboard layout | Stable |
| `frontend/style.css` | Theme + dimmed states | Stable |

---

## 3. SCORING ENGINE — AUDIT

### 3.1 Công thức hiện tại

```
total_score = mcdx_score + rrg_score + adx_score
score_max   = 2.5  (MCDX: 1.0 + RRG: 1.0 + ADX: 0.5)
```

### 3.2 MCDX Score (Banker Value)

| Banker Value | Score |
|---|---|
| ≤ 0 | 0.00 |
| 3 | 0.20 |
| 8 | 0.40 |
| 12 | 0.60 |
| 16 | 0.80 |
| ≥ 20 | 1.00 |

**Đánh giá:** Logic tuyến tính, hợp lý. Không có vấn đề kỹ thuật.

### 3.3 RRG Score (Quadrant)

| Quadrant | Tên | Score |
|---|---|---|
| 1 | TĂNG GIÁ | 1.00 |
| 4 | TÍCH LŨY | 0.75 |
| 2 | SUY YẾU | 0.50 |
| 3 | GIẢM GIÁ | 0.25 |

**Đánh giá:** Đơn giản, nhất quán. Cần xem xét thêm `tail_5d` (xu hướng ngắn hạn) trong tương lai.

### 3.4 ADX Score

**Điều kiện bắt buộc:** DI+ > DI- (ngược lại = 0)

| ADX Range | Base Score |
|---|---|
| < 15 | 0.00 |
| 15–20 | 0.10 |
| 20–25 | 0.30 |
| 25–40 | 0.60 |
| 40–50 | 0.80 |
| ≥ 50 | 0.90 |

**Adjustments:**
- +0.10 nếu slope_1d > 0 AND slope_3d > 2 (xu hướng tăng tốc)
- +0.05 nếu chỉ slope_3d > 2
- −0.05 nếu slope_1d < 0 (ADX đang suy yếu ngắn hạn)
- −0.05 nếu slope_3d < −2 (suy yếu trung hạn)
- +0.05 nếu (DI+ − DI−) ≥ 10 (khoảng cách rõ ràng)

**Final:** `raw_score × 0.5` (capped 0.5 max)

**Đánh giá:** Thiết kế thận trọng (cap ở 0.5 tránh double-count với RRG). Hợp lý.

---

## 4. API ENDPOINTS — AUDIT

| Endpoint | Method | Input | Output | Trạng thái |
|---|---|---|---|---|
| `/api/scores` | GET | `category=vn30` | JSON array records | OK |
| `/api/history` | GET | `symbol`, `start_date`, `end_date` | JSON array | OK |
| `/api/status` | GET | `category` | `{is_running, progress, current_symbol}` | OK |
| `/api/refresh` | POST | `category=vn30` | `{message}` | OK |
| `/api/import` | POST | `{symbols: []}` | `{message, count}` | OK |
| `/` | GET | — | Static frontend | OK |

**Vấn đề phát hiện:**
- CORS: `allow_origins=["*"]` — chấp nhận được cho internal tool, cần restrict khi deploy production.
- `/api/refresh`: không có authentication — ai cũng có thể trigger scoring.
- `/api/import`: không validate ký tự input (tiềm ẩn path traversal nếu symbol được dùng để tạo file).

---

## 5. FRONTEND — AUDIT

### 5.1 Dynamic Scoring

**Cơ chế:**
1. Tải data từ API, cache `_orig_mcdx/rrg/adx/max/total`
2. Khi toggle checkbox → `applyDynamicScoring()` tính lại `total_score` và `score_max` trực tiếp trên data
3. Re-render table, progress bar, history chart

**Đánh giá:** Logic đúng, sync 2 chiều (header pills ↔ table header checkboxes) hoạt động tốt. Không có bug phát hiện.

### 5.2 Fallback Strategy

- Nếu API `/api/scores` fail → load từ `frontend/data_vn30.json`
- Cho phép Vercel deployment hoạt động dù không có backend

**Đánh giá:** Thiết kế thông minh cho MVP.

---

## 6. DATABASE — AUDIT

### 6.1 Schema (scores table)

```sql
symbol TEXT, category TEXT, updated_date TEXT,
banker_value REAL, banker_left REAL, banker_right REAL,
quadrant INTEGER, rs_ratio REAL, rs_mom REAL, tail_5d REAL,
mcdx_score REAL, rrg_score REAL, adx_score REAL,
extra_score REAL, total_score REAL, score_max REAL,
score_components TEXT (JSON),
adx_value REAL, di_plus REAL, di_minus REAL,
adx_1d REAL, adx_3d REAL,
updated_at TEXT,
PRIMARY KEY (symbol, category, updated_date)
```

**Đánh giá:**
- Lưu trữ đầy đủ raw values + computed scores → tốt cho debug và audit
- Primary key theo ngày → hỗ trợ history natively
- Không có index phụ → có thể chậm khi data lớn (VN100 × nhiều ngày)

---

## 7. TECHNICAL DEBT & ĐIỂM CẦN CẢI THIỆN

| # | Vấn đề | Mức độ | Ghi chú |
|---|---|---|---|
| 1 | Dependency `AmiBroker` — platform lock-in Windows | High | Không deploy được trên server Linux/cloud |
| 2 | CORS `allow_origins=["*"]` | Medium | OK cho dev, cần fix trước production |
| 3 | No authentication trên API | Medium | Bất kỳ ai có URL đều refresh được |
| 4 | `scraper_mcdx.py` (Playwright) chậm ~90 phút cho VN100 | High | Legacy, cần thay thế |
| 5 | `requirements.txt` không pin version (trừ vnstock) | Low | Có thể break khi cài lại |
| 6 | SQLite không có index phụ | Low | OK với 30 stocks, cần index nếu mở rộng |
| 7 | `hotmoney` field có trong AFL output nhưng không được dùng trong scoring | Medium | Tiềm năng thêm indicator |
| 8 | Không có unit tests cho scoring functions | Medium | `test_*.py` tồn tại nhưng chủ yếu là integration |
| 9 | Frontend không có error boundary khi API trả lỗi | Low | UX degrades gracefully qua fallback |
| 10 | Public deploy (Vercel) chỉ dùng JSON tĩnh, không real-time | High | Cần WebSocket hoặc polling API thật |

---

## 8. ĐIỂM MẠNH

1. **Kiến trúc modular:** Mỗi component (scoring, database, AmiBroker bridge) tách biệt rõ ràng.
2. **Dynamic scoring UI:** Real-time toggle mà không cần reload — UX tốt.
3. **Dual deploy:** Local (real-time) + Vercel (demo public) — linh hoạt.
4. **Extensible scoring framework:** `build_score_payload(extra_components={...})` cho phép thêm indicator dễ dàng.
5. **Tài liệu đầy đủ:** README, TECHNICAL_SPEC, HUONG_DAN, SCORING_EXTENSION — hiếm thấy ở dự án cá nhân.
6. **Historical tracking:** SQLite với primary key theo ngày → có sẵn data cho backtest/history chart.
7. **Hotmoney field trong raw data** — chưa được khai thác, tiềm năng cao.

---

## 9. KẾT LUẬN AUDIT

**Tổng đánh giá:** MVP vững chắc, đủ để demo cho nhà đầu tư giai đoạn seed/angel. Codebase sạch, tài liệu tốt hơn mức trung bình của project cá nhân. Điểm yếu chính là platform dependency (AmiBroker trên Windows) và thiếu authentication — cả hai đều có giải pháp rõ ràng.

**Sẵn sàng để:** Demo nội bộ, pitching nhà đầu tư, Phase 1 productization.

**Chưa sẵn sàng để:** Production multi-user, SaaS deployment, institutional use.
