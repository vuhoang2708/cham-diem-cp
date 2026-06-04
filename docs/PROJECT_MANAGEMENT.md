# PROJECT MANAGEMENT HANDBOOK — SignalBoard VN
# Tài liệu cho Agent/PM kế tiếp

**Phiên bản:** 1.0  
**Ngày tạo:** 2026-06-04  
**Người tạo:** Claude AI (Sonnet 4.6)  
**Mục đích:** Để agent/PM khác có thể tiếp quản và tiếp tục phát triển dự án mà không cần hỏi lại từ đầu.

---

## 1. TRẠNG THÁI HIỆN TẠI (2026-06-04)

### Đã hoàn thành
- ✅ MVP chạy local: AmiBroker + FastAPI + SQLite + Frontend tĩnh
- ✅ 3 chỉ báo: MCDX (Banker), RRG (Quadrant), ADX
- ✅ Dynamic scoring UI: bật/tắt tiêu chí realtime
- ✅ Deploy public: https://cham-diem-cp.vercel.app (static JSON)
- ✅ Tài liệu đầy đủ: README, TECHNICAL_SPEC, HUONG_DAN, SCORING_EXTENSION
- ✅ Audit report: docs/AUDIT_REPORT.md
- ✅ Product Strategy & Master Plan: docs/PRODUCT_STRATEGY.md
- ✅ Phase 1 files:
  - `backend/cloud_pipeline.py` — vnstock-based data pipeline
  - `backend/auth.py` — JWT authentication
  - `backend/telegram_bot.py` — Telegram alerts
  - `backend/scheduler.py` — APScheduler daily refresh
  - `Dockerfile` — Container deployment
  - `requirements-cloud.txt` — Cloud dependencies
- ✅ UAT Scenarios: docs/UAT_SCENARIOS.yaml
- ✅ SQL injection fix: database.py:get_latest_scores

### Đang làm (Phase 1 — tiếp theo)
- 🔄 Tích hợp auth endpoints vào main.py
- 🔄 Tích hợp cloud_pipeline vào main_scorer.py khi DATA_SOURCE=cloud
- 🔄 Test cloud_pipeline với vnstock thực tế
- 🔄 Telegram webhook endpoint trong main.py
- 🔄 .env.example file
- 🔄 Landing page (frontend/landing.html)

### Backlog (Phase 2+)
- ⏳ Subscription system (VNPAY/Stripe)
- ⏳ VN100 via cloud pipeline
- ⏳ User portfolio tracking
- ⏳ Signal marketplace
- ⏳ Mobile responsive UI v2
- ⏳ AI signal explanation

---

## 2. KIẾN TRÚC KỸ THUẬT

### Codebase Structure
```
Cham diem co phieu/
├── backend/
│   ├── main.py              # FastAPI app — ENTRY POINT
│   ├── main_scorer.py       # Scoring orchestrator (AmiBroker + cloud)
│   ├── scoring.py           # Score formulas (MCDX/RRG/ADX)
│   ├── database.py          # SQLite CRUD
│   ├── cloud_pipeline.py    # [NEW P1] vnstock-based pipeline
│   ├── auth.py              # [NEW P1] JWT authentication
│   ├── telegram_bot.py      # [NEW P1] Telegram alerts
│   ├── scheduler.py         # [NEW P1] APScheduler
│   ├── run_amibroker_vn30.py # AmiBroker bridge (Windows-only)
│   └── ...legacy files...
├── frontend/
│   ├── index.html           # Dashboard
│   ├── app.js               # Dynamic scoring logic
│   └── style.css
├── data/
│   ├── scores.db            # SQLite database
│   └── vn30_symbols.json    # 30 mã VN30
├── docs/
│   ├── AUDIT_REPORT.md      # [NEW] Audit 2026-06-04
│   ├── PRODUCT_STRATEGY.md  # [NEW] 3 hướng + Master Plan
│   ├── UAT_SCENARIOS.yaml   # [NEW] Test scenarios
│   ├── PROJECT_MANAGEMENT.md # [NEW] File này
│   ├── TECHNICAL_SPEC.md
│   ├── SCORING_EXTENSION.md
│   └── PROPOSAL_ADX_SCORE.md
├── Dockerfile               # [NEW P1]
├── requirements.txt         # Windows/AmiBroker deps
├── requirements-cloud.txt   # [NEW P1] Cloud deps
└── README.md
```

### Environment Variables
```bash
# AmiBroker mode (local Windows only)
DATA_SOURCE=amibroker
AMIBROKER_TIMEOUT=360

# Cloud mode (production)
DATA_SOURCE=cloud
JWT_SECRET_KEY=<random-256-bit-string>
TELEGRAM_BOT_TOKEN=<from @BotFather>
DATABASE_URL=sqlite:///./data/scores.db  # or PostgreSQL URL
```

### API Endpoints (hiện tại)
| Endpoint | Method | Auth | Notes |
|---|---|---|---|
| `/api/scores` | GET | Public | `?category=vn30/vn100/custom` |
| `/api/history` | GET | Public | `?symbol=VCB&start_date=...` |
| `/api/status` | GET | Public | Refresh status |
| `/api/refresh` | POST | ⚠️ No auth | Cần thêm auth: require admin |
| `/api/import` | POST | ⚠️ No auth | Cần thêm auth |

### API Endpoints (cần thêm Phase 1)
| Endpoint | Method | Auth | Notes |
|---|---|---|---|
| `/auth/register` | POST | Public | Email + password |
| `/auth/login` | POST | Public | Returns JWT token |
| `/auth/me` | GET | Bearer | Current user info |
| `/telegram/webhook` | POST | Internal | Telegram update handler |

---

## 3. QUY TRÌNH LÀM VIỆC

### Cách chạy local (AmiBroker mode)
```powershell
# Bật AmiBroker trước, đảm bảo FireAnt plugin chạy
cd "Cham diem co phieu"
$env:DATA_SOURCE="amibroker"
$env:AMIBROKER_TIMEOUT="360"
.\venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
# Mở http://127.0.0.1:8000
```

### Cách chạy cloud mode (không cần AmiBroker)
```bash
DATA_SOURCE=cloud uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Cách chạy với Docker
```bash
docker build -t signalboard-vn .
docker run -p 8000:8000 \
  -e JWT_SECRET_KEY=your-secret \
  -e TELEGRAM_BOT_TOKEN=your-token \
  signalboard-vn
```

### Cách deploy lên Railway
```bash
# Sau khi có Railway account
railway login
railway link
railway up
```

---

## 4. KẾ HOẠCH SPRINT (PHASE 1)

### Sprint 1 (Tuần 1-2): Data Pipeline
- [ ] Verify cloud_pipeline.py với vnstock thực tế
- [ ] Test fetch_ohlcv("VCB") → trả đúng OHLCV
- [ ] Test compute_adx_indicators → so sánh với AmiBroker output
- [ ] Test compute_rrg_indicators → verify quadrant mapping
- [ ] Integrate vào main_scorer.py: `if DATA_SOURCE == "cloud": use cloud_pipeline`

### Sprint 2 (Tuần 3-4): Auth System
- [ ] Thêm `/auth/register`, `/auth/login` endpoints vào main.py
- [ ] Protect `/api/refresh` với `require_admin`
- [ ] Test auth flow end-to-end
- [ ] Tạo `.env.example`

### Sprint 3 (Tuần 5-6): Telegram Bot
- [ ] Tạo bot qua @BotFather, lấy token
- [ ] Thêm `/telegram/webhook` endpoint
- [ ] Set webhook: `POST https://api.telegram.org/bot{TOKEN}/setWebhook`
- [ ] Test `/top`, `/score VCB` commands
- [ ] Test broadcast alert khi score thay đổi ≥ 0.2

### Sprint 4 (Tuần 7-8): Docker + Deploy
- [ ] Build Docker image → test local
- [ ] Deploy lên Railway.app (free tier)
- [ ] Set environment variables
- [ ] Verify API endpoints on production URL
- [ ] Update Vercel static với real API URL

### Sprint 5 (Tuần 9-10): Scheduler + Monitoring
- [ ] Integrate scheduler.py vào main.py startup
- [ ] Test daily refresh trigger
- [ ] Thêm logging và error alerts
- [ ] Uptime monitoring (UptimeRobot free)

### Sprint 6 (Tuần 11-12): UI Polish + Demo
- [ ] Landing page
- [ ] Investor demo script
- [ ] Pitch deck (dùng PRODUCT_STRATEGY.md)
- [ ] Run UAT (docs/UAT_SCENARIOS.yaml)

---

## 5. QUYẾT ĐỊNH THIẾT KẾ QUAN TRỌNG

### Tại sao không dùng PostgreSQL ngay?
SQLite đủ cho MVP với 30 mã × 365 ngày × 3 năm = ~33k rows. Migrate lên PostgreSQL khi có multi-user production. Không nên over-engineer sớm.

### Tại sao MCDX cloud là proxy, không phải exact?
MCDX Banker là indicator proprietary của FireAnt/SSI. Để dùng chính xác, cần:
1. Xin phép FireAnt → partnership agreement, hoặc
2. Mua data feed từ SSI → tốn tiền nhưng accurate
3. Proxy (hiện tại) — volume-based approximation, không 100% giống nhưng đủ cho MVP cloud

**Action needed:** Contact FireAnt/SSI về data licensing trước Phase 2.

### Tại sao chọn Railway thay vì AWS/GCP?
- Railway free tier đủ cho MVP (500h/tháng)
- Deploy với `git push` — không cần DevOps knowledge
- Khi scale up → migrate sang fly.io hoặc AWS ECS

### Tại sao Telegram thay vì app riêng?
- 90% investor VN đã dùng Telegram
- Không cần build mobile app
- Alert qua Telegram channel = free marketing
- Khi user base lớn → build app riêng

---

## 6. RỦI RO VÀ BIỆN PHÁP

| Rủi ro | Xác suất | Mức độ | Biện pháp |
|---|---|---|---|
| FireAnt/SSI không cho phép dùng MCDX | Medium | High | Dùng proxy + liên hệ partnership sớm |
| vnstock rate limit bị block | Medium | High | Cache dữ liệu ngày, không fetch realtime |
| MCDX proxy không đủ chính xác | High | Medium | Validate bằng back-test, document rõ limitation |
| CORS lỗi trên production | Low | Medium | Set ALLOWED_ORIGINS env var |
| JWT secret bị lộ | Low | High | Rotate secret, dùng Vault/Railway secrets |

---

## 7. CHECKLIST TRƯỚC KHI HANDOFF

Nếu agent/PM mới tiếp quản, verify các điều này:

- [ ] `git log --oneline -10` — xem 10 commit gần nhất
- [ ] Đọc `docs/AUDIT_REPORT.md` — hiểu trạng thái kỹ thuật
- [ ] Đọc `docs/PRODUCT_STRATEGY.md` — hiểu định hướng sản phẩm
- [ ] Chạy server local và verify `/api/scores` trả dữ liệu
- [ ] Kiểm tra `backend/cloud_pipeline.py` đã được integrate chưa
- [ ] Kiểm tra `.env.example` đã tồn tại chưa
- [ ] Đọc `docs/UAT_SCENARIOS.yaml` và chạy smoke tests

---

## 8. LIÊN HỆ VÀ TÀI NGUYÊN

| Tài nguyên | Link/Info |
|---|---|
| GitHub | https://github.com/vuhoang2708 (inferred từ git config) |
| Vercel public | https://cham-diem-cp.vercel.app |
| vnstock docs | https://github.com/thinh-vu/vnstock |
| Railway deploy | https://railway.app |
| APScheduler docs | https://apscheduler.readthedocs.io |
| FastAPI docs | https://fastapi.tiangolo.com |
| Telegram Bot API | https://core.telegram.org/bots/api |

---

## 9. NGUYÊN TẮC CODE

1. **Không mock database trong tests** — luôn test với SQLite thật
2. **Pin versions trong requirements** — tránh break khi cài lại
3. **Không comment self-evident code** — chỉ comment WHY, không comment WHAT
4. **SQL parameterized queries** — không bao giờ f-string trong SQL
5. **Environment variables** — không hardcode secrets trong code
6. **No breaking changes** — khi thay đổi API, giữ backward compatibility hoặc version endpoint

---

*Document này cần được cập nhật sau mỗi sprint hoàn thành.*
