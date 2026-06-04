# PRODUCT STRATEGY — 3 Hướng Phát Triển & Master Plan

**Ngày:** 2026-06-04  
**Dự án:** VN30 Stock Scoring Dashboard → Commercial Product  
**Cơ sở:** Audit report + nghiên cứu thị trường quốc tế

---

## PHẦN I: 3 HƯỚNG PHÁT TRIỂN

### Hướng 1: "VN Stock Screener" — Mở Rộng Sang Toàn Thị Trường

**Tầm nhìn:** Trở thành screener kỹ thuật chuẩn cho toàn thị trường VN (HOSE + HNX + UPCOM ~1,700 mã), benchmark so sánh theo rổ (VN30, VN100, VNMID, ngành).

**Core differentiator:** Dữ liệu VN bản địa (vnstock + FireAnt) + scoring multi-factor kết hợp kỹ thuật (MCDX/RRG/ADX) với cơ bản (P/E, ROE, tăng trưởng).

**Mô hình kinh doanh:** Freemium — Free (top 30 realtime + 3 tháng history) → Pro ($5–10/tháng, toàn thị trường + alert + export Excel) → API ($20–50/tháng, developer access).

**Stack cần thêm:** vnstock cho fundamental, PostgreSQL thay SQLite, task queue (Celery), Redis cache, WebSocket cho realtime.

**Ưu điểm:**
- Thị trường lớn nhất VN (~200,000 nhà đầu tư cá nhân tích cực)
- Giải quyết pain point thực tế: thiếu screener kỹ thuật tốt + rẻ cho VN
- Cạnh tranh được với Vietstock/Simplize bằng technical scoring chuyên sâu hơn

**Nhược điểm:**
- Cần giải quyết AmiBroker dependency (không scale được cho multi-user)
- Chi phí data (vnstock có rate limit, cần deal với data provider)
- Competition: Vietstock, Simplize, FiinTrade đã có user base lớn

---

### Hướng 2: "Quant Alpha Engine" — Công Cụ Cho Quỹ & Prop Trader

**Tầm nhìn:** Nền tảng factor research + backtesting cho quỹ nhỏ, family office, prop trading VN. Tập trung vào institutional users thay vì retail.

**Core differentiator:** Multi-factor scoring có thể tùy chỉnh + backtesting tích hợp + API cho trading system tích hợp.

**Mô hình kinh doanh:** B2B subscription ($200–500/tháng/user) + custom deployment + consulting. 10 khách institutional = $50k+ ARR.

**Stack cần thêm:** backtrader/vectorbt cho backtesting, TimescaleDB cho time-series, REST API cho trading system integration, report generation (PDF).

**Ưu điểm:**
- Willingness-to-pay cao hơn nhiều (institutional > retail)
- Ít cạnh tranh ở phân khúc VN quant tools
- Defensible: đòi hỏi domain knowledge VAS + market microstructure VN

**Nhược điểm:**
- Sales cycle dài, khó acquire khách đầu
- Cần credibility (track record, bằng cấp)
- Market size nhỏ hơn (~500 quỹ nhỏ/family office tại VN)

---

### Hướng 3 ★ (ĐƯỢC CHỌN): "SignalBoard VN" — Social + Technical Alert Platform

**Tầm nhìn:** Platform kết hợp scoring kỹ thuật + social layer (tương tự TradingView nhưng VN-native), nơi trader chia sẻ signal và theo dõi danh mục nhau, monetize qua subscription + signal marketplace.

**Core differentiator:** VN30 scoring độc quyền (MCDX + RRG + ADX) làm "nguồn chân lý" + community trader VN chia sẻ thesis + Telegram/Zalo alert tích hợp (kênh quen thuộc của investor VN).

**Mô hình kinh doanh:**
- Free: xem ranking VN30, top signals
- Pro (99k–199k VND/tháng): alert realtime, filter nâng cao, unlimited history
- Signal Marketplace: creator bán signal → platform ăn 20–30% (như App Store)
- Premium Community (Telegram/Zalo): 99k–299k/tháng

**Tại sao đây là hướng phù hợp VN nhất:**
1. **Zalo/Telegram culture:** Investor VN chủ yếu dùng Zalo group và Telegram để chia sẻ cổ phiếu — platform này đáp ứng đúng workflow sẵn có.
2. **Signal economy:** Có hàng trăm "chuyên gia" FB/Zalo bán tín hiệu cổ phiếu, chưa có marketplace chính thức và minh bạch.
3. **Price point phù hợp:** 99k–199k VND/tháng (~$4–8) phù hợp khả năng chi trả của nhà đầu tư retail VN.
4. **Network effects:** Càng nhiều trader chia sẻ → platform càng có giá trị → user tăng → circular.
5. **Regulatory advantage:** Không bán financial advice (tránh luật chứng khoán) mà bán công cụ và cộng đồng.

**Nhược điểm:**
- Cần critical mass để social layer có giá trị (chicken-and-egg)
- Content moderation (tránh pump-and-dump scheme)
- Cần team marketing/community building song song với tech

---

## PHẦN II: MASTER PLAN — "SignalBoard VN"

### Vision Statement

> SignalBoard VN là nền tảng scoring kỹ thuật + cộng đồng tín hiệu đầu tư dành riêng cho thị trường chứng khoán Việt Nam, giúp nhà đầu tư cá nhân ra quyết định dựa trên dữ liệu thay vì tin đồn.

### OKRs (Objectives & Key Results)

**Year 1 (2026):**
- O1: Có sản phẩm production-ready đủ để pitch Series A
  - KR1: 500 MAU trả phí
  - KR2: NPS ≥ 40
  - KR3: Revenue ≥ $2,000/tháng
- O2: Thoát khỏi AmiBroker dependency
  - KR1: Data pipeline chạy trên cloud (không cần Windows)
  - KR2: Uptime ≥ 99%

**Year 2 (2027):**
- O1: Market leader trong technical scoring cho nhà đầu tư cá nhân VN
  - KR1: 5,000 MAU trả phí
  - KR2: Revenue ≥ $20,000/tháng
  - KR3: Signal Marketplace có ≥ 50 creator tích cực

---

### ROADMAP THEO PHASE

```
Phase 1 (Tháng 1–3): Cloud-Ready MVP
├── Thoát AmiBroker → vnstock pipeline
├── User authentication (JWT)
├── Telegram bot alerts cơ bản
└── Deploy production trên Vercel + Railway

Phase 2 (Tháng 4–6): Monetization Foundation  
├── Subscription system (Stripe/VNPAY)
├── Mở rộng sang VN100
├── Alert hệ thống (email + Telegram)
└── Mobile-responsive UI v2

Phase 3 (Tháng 7–9): Community Layer
├── User profiles + portfolio tracking
├── Signal sharing (public/private)
├── Signal Marketplace v1
└── Zalo Mini App integration

Phase 4 (Tháng 10–12): Scale & Pitch
├── AI-assisted signal explanation
├── Backtest signal performance
├── Investor deck + pitch materials
└── Series A preparation
```

---

## PHẦN III: PHASE 1 — CHI TIẾT TRIỂN KHAI

### Mục tiêu Phase 1

Chuyển từ internal Windows tool → cloud-deployable product với authentication và Telegram alerts.

### Deliverables Phase 1

| # | Deliverable | Mô tả |
|---|---|---|
| P1.1 | Data pipeline cloud-native | Thay AmiBroker bằng vnstock + pandas-ta |
| P1.2 | Auth system | JWT + user roles (admin/pro/free) |
| P1.3 | Telegram bot alert | Notify khi score thay đổi đáng kể |
| P1.4 | Docker deployment | Container hóa backend |
| P1.5 | Scheduled refresh | APScheduler chạy update hàng ngày 4:30PM |
| P1.6 | Investor Demo | Polish UI + landing page |

### Kiến trúc Phase 1

```
[Data Pipeline]          [Backend]              [Frontend]
vnstock (TCBS)    →    FastAPI + JWT    →    Dashboard (enhanced)
pandas-ta (ADX/        PostgreSQL              Landing page
  MCDX proxy)          Redis cache             Telegram bot
APScheduler            Docker/Railway          Vercel
```

### Thay thế AmiBroker

| Chỉ báo AmiBroker | Thay thế cloud |
|---|---|
| `FA_MCDX` Banker | Tính xấp xỉ: Net buying volume (vnstock) normalized qua 50 periods |
| `FA_RRG` Quadrant | `pandas-ta` với RS-Ratio/RS-Momentum so benchmark VNINDEX |
| `ADX/PDI/MDI` | `pandas-ta ADX(14)` — tương đương 100% |
| Hotmoney | Net foreign buying (vnstock `trading.foreign_trading`) |

**Lưu ý:** MCDX Banker là proprietary indicator của FireAnt. Cloud version cần dùng proxy indicator hoặc xin phép FireAnt/SSI. Đây là điểm rủi ro cần clarify sớm.

### Milestone & Timeline Phase 1

```
Week 1–2:  Setup vnstock pipeline + ADX/RRG cloud equivalent
Week 3–4:  JWT auth + user management API
Week 5–6:  Telegram bot alerts
Week 7–8:  Docker + Railway deployment  
Week 9–10: Scheduled refresh + monitoring
Week 11–12: UI polish + landing page + demo prep
```

---

## PHẦN IV: INVESTOR PITCH SUMMARY

**Problem:** ~250,000 nhà đầu tư cá nhân VN thiếu công cụ kỹ thuật bản địa, phải dùng TradingView ($15/tháng, không có indicator VN) hoặc Vietstock (chậm, UX kém).

**Solution:** SignalBoard VN — scoring dashboard kết hợp chỉ báo kỹ thuật VN-specific + cộng đồng tín hiệu, giá $4–8/tháng.

**Traction (hiện tại):**
- MVP đang chạy tại https://cham-diem-cp.vercel.app
- 3 chỉ báo tích hợp (MCDX, RRG, ADX) với dynamic scoring UI
- Data pipeline qua AmiBroker + FireAnt

**Market Size:**
- SAM: ~250,000 nhà đầu tư cá nhân tích cực trên sàn VN
- Target: 1% = 2,500 users Pro × 99k VND = ~$10k MRR Year 1

**Team (cần xây):**
- 1 Full-stack dev (hiện tại: 1 người)
- 1 Marketing/Community lead
- 1 Financial analyst/advisor (để tăng credibility)

**Ask (Seed Round):**
- $50,000–100,000 để build Phase 1–2 và 6 tháng runway
- Sử dụng: 60% dev (cloud infra + features), 30% marketing, 10% legal/compliance
