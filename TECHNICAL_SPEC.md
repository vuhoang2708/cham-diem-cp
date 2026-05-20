# TECHNICAL SPECIFICATION: Hệ thống Chấm điểm Cổ phiếu VN100 (V2.0)

## 1. Tổng quan Kiến trúc
Hệ thống được thiết kế theo mô hình Client-Server cục bộ, hỗ trợ quản lý đa danh mục (VN30, VN100, Custom) và theo dõi dữ liệu lịch sử.

## 2. Hạ tầng Dữ liệu (Database)
- **Công nghệ**: SQLite.
- **Schema bảng `scores`**:
    - `symbol` (TEXT): Mã cổ phiếu.
    - `category` (TEXT): Nhóm (vn30, vn100, custom).
    - `updated_date` (DATE): Ngày cập nhật (YYYY-MM-DD).
    - `total_score` (REAL): Điểm tổng hợp.
    - `mcdx_score` (REAL): Điểm từ chỉ báo MCDX (0 - 1.0).
    - `banker_left` (REAL): Giá trị Banker bên trái ký hiệu ∅.
    - `banker_right` (REAL): Giá trị Banker bên phải ký hiệu ∅ (Backup).
    - `rrg_quadrant` (TEXT): Vùng dòng tiền (Tăng giá, Tích lũy, Suy yếu, Giảm giá).
    - `rs_ratio` / `rs_mom` (REAL): Chỉ số RRG.
    - `tail_5d` (REAL): Độ dài đuôi 5 ngày.
- **Primary Key**: `(symbol, category, updated_date)` - Cho phép lưu trữ lịch sử biến động mỗi ngày của mỗi mã.

## 3. Backend (FastAPI)
- **Serving Static**: FastAPI phục vụ trực tiếp thư mục `frontend/` tại cổng 8000.
- **API Endpoints**:
    - `GET /api/scores?category=...`: Lấy bảng điểm mới nhất của một nhóm.
    - `GET /api/history?symbol=...`: Lấy dữ liệu 10 ngày gần nhất của một mã CP.
    - `POST /api/refresh?category=...`: Kích hoạt tiến trình quét dữ liệu ngầm.
    - `POST /api/import`: Lưu danh sách mã CP tùy chỉnh của người dùng.

## 4. Frontend & Visualization
- **Layout**: Split-screen (Chia đôi màn hình) cho Tab Lịch sử.
- **Thư viện đồ thị**: Chart.js.
- **Đồ thị Lịch sử (10 ngày)**:
    - Trục X: Ngày (MM-DD).
    - Trục Y: Điểm số (0 - 2.1).
    - 3 Đường biểu diễn: Tổng điểm (Vàng), MCDX (Xanh dương), RRG (Xanh lá).
- **Responsive**: Sử dụng Flexbox để đảm bảo bảng và biểu đồ tự động co giãn theo kích thước cửa sổ.

## 5. Quy trình Quét dữ liệu (Scoring Logic)
1.  **RRG Calculation**: Lấy dữ liệu từ AmiBroker qua OLE COM, tính RS-Ratio và RS-Momentum.
2.  **MCDX Scraping**:
    - Kết nối AmiBroker COM.
    - Chạy file AFL `ami_bridge.afl` để tính MCDX Banker.
    - Đọc giá trị từ StaticVar.
3.  **Final Scoring**: `Total = RRG_Score (0-1) + MCDX_Score (0-1)`.

### Prerequisites:
- AmiBroker 6.0+ (bản Crack hoạt động)
- FireAnt indicators cài trong AmiBroker
- pywin32 cài trong Python environment
