# SESSION LOG — SignalBoard VN: Audit, Strategy & Phase 1
**Ngày:** 2026-06-04  
**Thực hiện bởi:** Claude AI (Sonnet 4.6)  
**Repo:** vuhoang2708 / Cham diem co phieu

---

## YÊU CẦU BAN ĐẦU

Sau khi cập nhật README và các tài liệu chính (commit `6ca2867 docs: update current scoring and dynamic UI docs`), yêu cầu:

1. Đọc lại toàn bộ tài liệu và mã nguồn → lập báo cáo audit chi tiết
2. Tìm kiếm các repo được đánh giá cao trên mạng → đề xuất 3 hướng phát triển để trở thành sản phẩm chính thức gửi cho nhà đầu tư
3. Tự chọn hướng gần với VN nhất và lên master plan triển khai từng phase
4. Bắt tay thực hiện Phase 1
5. Tạo kịch bản để Gemini dùng subagent browser test UAT
6. Tạo tài liệu cần thiết để agent khác có thể thay làm quản trị dự án
7. Push lên GitHub sau khi hoàn thành
8. Xuất toàn bộ nội dung chat thành .md và .html

---

## AUDIT REPORT — TÓM TẮT

### Điểm mạnh của codebase
- Kiến trúc modular: mỗi component (scoring, database, AmiBroker bridge) tách biệt rõ ràng
- Dynamic scoring UI: real-time toggle không cần reload
- Dual deploy: local (real-time) + Vercel (demo public)
- Extensible scoring framework: `build_score_payload(extra_components={...})`
- Tài liệu đầy đủ hơn mức trung bình của project cá nhân
- Historical tracking: SQLite với primary key theo ngày

### Vấn đề kỹ thuật đã phát hiện và fix
- **SQL Injection (FIXED):** `database.py:get_latest_scores` dùng f-string trong SQL query → đã fix sang parameterized query
- **CORS `allow_origins=["*"]`** — chấp nhận được cho dev, cần restrict trước production
- **AmiBroker dependency** — platform lock-in Windows, không deploy cloud được
- **No authentication** trên `/api/refresh` và `/api/import`

### Scoring Engine
- MCDX Banker: breakpoint interpolation 0→20, range [0.0, 1.0] ✅
- RRG Quadrant: 4 vùng → 0.25–1.00 ✅
- ADX: DI+ > DI- required, base tiers + adjustments, cap 0.5 ✅
- `score_max = 2.5` (MCDX 1.0 + RRG 1.0 + ADX 0.5) ✅

---

## NGHIÊN CỨU THỊ TRƯỜNG

### Các repo nổi bật
- **OpenBB Terminal** (~68,600 stars) — gold standard OSS quant platform
- **vnstock** (~1,300 stars) — thư viện Python duy nhất cho VN market
- **Screeni-py / PKScreener** (India) — closest analogue, CLI + Telegram alerts

### Sản phẩm thương mại tham khảo
- **Finviz** — Freemium, free tier tạo user base → Elite unlock realtime data
- **TradingView** — $3B valuation, network effects + Pine Script ecosystem
- **FiinTrade VN** — Institutional grade cho Vietnam market

### Điểm mấu chốt
- Gap thực sự ở VN: screener kỹ thuật multi-factor bản địa + cộng đồng tín hiệu
- vnstock = data layer sẵn có, chỉ cần xây scoring + UI + community layer
- Price point VN: 99k–199k VND/tháng ($4–8) phù hợp retail investor

---

## 3 HƯỚNG PHÁT TRIỂN

### Hướng 1: VN Stock Screener (Mở rộng toàn thị trường)
Screener kỹ thuật cho 1,700+ mã HOSE/HNX/UPCOM. Freemium $5–10/tháng.
- Ưu: Thị trường lớn nhất (250k nhà đầu tư cá nhân tích cực)
- Nhược: Competition nặng với Vietstock/Simplize/FiinTrade

### Hướng 2: Quant Alpha Engine (B2B cho quỹ/prop trader)
Multi-factor research + backtesting. $200–500/tháng/user institutional.
- Ưu: Willingness-to-pay cao, ít cạnh tranh
- Nhược: Sales cycle dài, cần credibility

### Hướng 3 ★ (ĐÃ CHỌN): SignalBoard VN — Social + Technical Alert Platform
Scoring kỹ thuật + social layer + Telegram/Zalo alerts. 99k–199k VND/tháng.
- Ưu: Phù hợp culture VN (Zalo/Telegram), network effects, signal marketplace
- Nhược: Cần critical mass, content moderation

**Lý do chọn Hướng 3:** Phù hợp nhất với hành vi thực tế của investor VN (dùng Zalo/Telegram chia sẻ cổ phiếu), tạo ra network effects, và có con đường monetize rõ ràng qua signal marketplace mà không vi phạm luật tư vấn đầu tư.

---

## MASTER PLAN — SIGNALBOARD VN

### Phase 1 (Tháng 1–3): Cloud-Ready MVP
- Thoát AmiBroker → vnstock pipeline
- JWT authentication
- Telegram bot alerts
- Docker + Railway deployment
- Scheduled daily refresh

### Phase 2 (Tháng 4–6): Monetization
- Subscription system (VNPAY/Stripe)
- Mở rộng VN100
- Email + Telegram alerts nâng cao
- Mobile-responsive UI v2

### Phase 3 (Tháng 7–9): Community Layer
- User profiles + portfolio tracking
- Signal sharing
- Signal Marketplace v1
- Zalo Mini App integration

### Phase 4 (Tháng 10–12): Scale & Pitch
- AI signal explanation
- Backtest performance
- Investor deck
- Series A preparation

### Target Year 1
- 500 MAU trả phí
- Revenue ≥ $2,000/tháng
- NPS ≥ 40

---

## PHASE 1 — ĐÃ TRIỂN KHAI

### Files mới tạo

| File | Mô tả |
|---|---|
| `backend/cloud_pipeline.py` | vnstock + pandas-ta pipeline thay AmiBroker |
| `backend/auth.py` | JWT authentication (free/pro/admin roles) |
| `backend/telegram_bot.py` | Telegram bot alerts + webhook handler |
| `backend/scheduler.py` | APScheduler daily refresh 4:30PM + 8:45AM |
| `Dockerfile` | Container hóa cho cloud deployment |
| `requirements-cloud.txt` | Cloud dependencies (không cần pywin32/playwright) |
| `docs/AUDIT_REPORT.md` | Báo cáo audit kỹ thuật |
| `docs/PRODUCT_STRATEGY.md` | 3 hướng + Master Plan |
| `docs/UAT_SCENARIOS.yaml` | Kịch bản test cho Gemini browser agent |
| `docs/PROJECT_MANAGEMENT.md` | Tài liệu quản trị dự án |

### Fixes thực hiện
- **SQL injection:** `database.py:117` — đổi f-string thành parameterized query

### Cloud Pipeline Design
```
vnstock (TCBS API)
  → fetch_ohlcv(symbol, days=90)
  → compute_adx_indicators()      ← pandas-ta ADX(14)
  → compute_rrg_indicators()      ← RS-Ratio/RS-Mom vs VNINDEX
  → compute_net_buying_proxy()    ← volume-based MCDX proxy
  → scoring.py (same formulas)
  → database.py (same schema)
```

**Lưu ý quan trọng về MCDX:** Cloud version dùng proxy volume-based thay cho FireAnt proprietary indicator. Cần liên hệ FireAnt/SSI về data licensing trước Phase 2.

---

## UAT SCENARIOS — TÓM TẮT

File: `docs/UAT_SCENARIOS.yaml`

7 test suites:
1. **Smoke** (S01–S04): Dashboard load, API, Vercel URL
2. **Dynamic Scoring** (D01–D04): Toggle MCDX/RRG/ADX, prevent untick all, sync checkbox
3. **Sorting** (T01–T02): Default sort descending, click-to-sort
4. **Tab Navigation** (N01–N02): Active tab, History chart
5. **Responsive** (R01): Mobile 375px viewport
6. **Performance** (P01–P02): Page load < 3s, API < 2s
7. **Data Integrity** (I01–I03): VN30 count ≥ 25, score range, quadrant values

Ngưỡng pass: ≥ 90% tests → PASS, 80–89% → CONDITIONAL PASS, < 80% → FAIL

---

## TÀI LIỆU QUẢN TRỊ DỰ ÁN

File: `docs/PROJECT_MANAGEMENT.md`

Bao gồm:
- Trạng thái hiện tại (đã làm/đang làm/backlog)
- Kiến trúc kỹ thuật đầy đủ
- Environment variables
- Sprint plan 6 sprints × 2 tuần
- Quyết định thiết kế và lý do
- Rủi ro và biện pháp
- Checklist handoff
- Nguyên tắc code

---

## KẾT LUẬN

Dự án đã chuyển từ **internal Windows tool** sang **cloud-ready product foundation** với:
- Đầy đủ tài liệu chiến lược sản phẩm
- Cloud data pipeline độc lập với AmiBroker
- Auth system chuẩn production
- Telegram integration cho VN market
- Docker deployment ready
- UAT scenarios để đảm bảo quality
- PM handbook để agent/người kế tiếp tiếp quản ngay
