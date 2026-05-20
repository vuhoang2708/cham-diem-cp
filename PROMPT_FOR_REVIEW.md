# Prompt: Đánh giá và thử lại AmiBroker COM Automation

## Bối cảnh

Tôi đang phát triển một hệ thống chấm điểm cổ phiếu VN100 chạy local (FastAPI + SQLite + HTML/JS). Hệ thống cần lấy 2 chỉ báo từ AmiBroker:

- **FA_MCDX** (Banker Smart Money) — hàm proprietary của plugin FireAnt
- **FA_RRG** (Relative Rotation Graph) — hàm proprietary của plugin FireAnt

Hiện tại hệ thống đang dùng Playwright scrape web Fireant (~75 phút cho 100 symbols). Mục tiêu là chuyển sang lấy trực tiếp từ AmiBroker qua COM automation để giảm xuống ~2 phút.

Tôi đã dành 1 ngày thử implement nhưng gặp blocker chưa giải quyết được. Cần bên ngoài đánh giá lại và thử các hướng tiếp cận mới.

---

## Tài liệu cần đọc (theo thứ tự)

### 1. Incident Report — đọc trước tiên
**File**: `INCIDENT_20260517.md`

Mô tả đầy đủ những gì đã thử, exact error messages, môi trường, và blocker cốt lõi. Đặc biệt chú ý:
- **Section 4.6** — `fopen()` trong AFL không ghi file khi trigger qua COM (core blocker)
- **Section 5** — bảng COM API surface: cái gì có, cái gì không có
- **Section 6** — câu hỏi mở quan trọng nhất cần verify

### 2. Technical Spec
**File**: `TECHNICAL_SPEC.md`

Kiến trúc tổng thể của hệ thống, scoring logic, database schema. Đọc để hiểu context rộng hơn.

### 3. Implementation Plan gốc
**File**: `Implementation Plan/implementation_plan_20260516_SwitchDataSourceToAmiBroker.md`

Plan ban đầu khi bắt đầu task — mô tả approach dự kiến và các rủi ro đã nhận diện từ trước.

### 4. Implementation Plan chi tiết
**File**: `Implementation Plan/implementation_plan_20260517_AmiConnector_Detailed.md`

Script thực thi chi tiết, pre-conditions, và trạng thái từng file trước khi bắt đầu.

### 5. Code hiện tại
Các file Python liên quan:
- `backend/scraper_amibroker.py` — connector hiện tại (dùng OHLCV trực tiếp, không qua AFL)
- `backend/create_apx.py` — generate .apx XML file đúng format
- `backend/test_ami_connector.py` — test COM connection
- `backend/setup_option_d.py` — test Option D (confirmed failed)
- `backend/ami_file_reader.py` — reader cho per-symbol export files

### 6. AFL Formulas
- `C:\Program Files (x86)\AmiBroker\Formulas\Custom\ami_bridge.afl` — formula chính
- `C:\Program Files (x86)\AmiBroker\Formulas\Custom\vn100_export.afl` — export formula
- `C:\Program Files (x86)\AmiBroker\Formulas\Custom\test_write.afl` — minimal fopen test

---

## Môi trường

- **OS**: Windows 11 Home 10.0.26200
- **AmiBroker**: 6.30.0, 32-bit, bản crack (unofficial)
- **FireAnt plugin**: đã cài, FA_MCDX và FA_RRG hoạt động bình thường từ UI
- **Python**: 32-bit bắt buộc (venv32 tại project root), pywin32 đã cài
- **COM ProgID**: `Broker.Application`
- **Symbols**: 100 symbols VN100, danh sách tại `data/vn100_symbols.json`

---

## Blocker cốt lõi cần giải quyết

`fopen()` trong AFL **không ghi được file** khi scan được trigger qua `AnalysisDocs.Run()` từ Python COM. Scan chạy bình thường (IsBusy=True → False), không có exception, nhưng không có file nào được tạo ra. Đã test với:
- Nhiều output paths (`C:\Windows\Temp`, `C:\Users\Public`)
- AFL đơn giản chỉ có `fopen` + `fputs("hello")` + `Filter=1`
- Scan 5 phút trên 8887 symbols

Khi chạy formula tương tự từ AmiBroker UI (click Scan thủ công) — **chưa test**, đây là điều cần verify đầu tiên.

---

## Câu hỏi cần trả lời

**Câu hỏi 1 (quan trọng nhất)**: Chạy `test_write.afl` thủ công từ AmiBroker UI (Analysis → Scan) — file `C:\Windows\Temp\ami_test.txt` có được tạo không? Nếu có → `fopen` hoạt động từ UI nhưng không từ COM → cần tìm cách khác trigger. Nếu không → vấn đề nằm ở AFL hoặc permissions.

**Câu hỏi 2**: Trên bản AmiBroker **licensed** (không phải crack), `fopen` trong AFL có hoạt động khi trigger qua COM không? Đây là điểm mấu chốt để xác định nguyên nhân là crack hay là giới hạn của AmiBroker nói chung.

**Câu hỏi 3**: Có cách nào khác để Python lấy giá trị FA_MCDX và FA_RRG từ AmiBroker mà không cần `fopen`? Ví dụ: đọc từ AmiBroker database files trực tiếp, dùng DDE, dùng clipboard, hoặc cơ chế IPC khác?

---

## Yêu cầu

1. Đọc `INCIDENT_20260517.md` trước khi làm bất cứ điều gì
2. Verify câu hỏi 1 bằng cách chạy `test_write.afl` thủ công từ UI
3. Đề xuất và thử các hướng tiếp cận mới nếu blocker hiện tại không giải quyết được
4. Không cần giữ backward compatibility với Playwright scraper — có thể thay thế hoàn toàn
5. Kết quả mong muốn: lấy được `banker` (float), `rs_ratio` (float), `rs_mom` (float), `quadrant` (int 1-4) cho mỗi symbol trong VN100, trong tổng thời gian < 5 phút
