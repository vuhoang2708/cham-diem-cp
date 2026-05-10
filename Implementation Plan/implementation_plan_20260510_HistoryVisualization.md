# Implementation Plan: History Tracking & Visualization (Retroactive)
*Created: 2026-05-10*

## 1. Mô tả yêu cầu (Requirement)
Bổ sung Tab Lịch sử cho Dashboard để theo dõi biến động 10 ngày gần nhất của một cổ phiếu dưới dạng Bảng dữ liệu và Biểu đồ đường.

## 2. Giải pháp kỹ thuật (Technical Solution)
- **Database**: Sử dụng hàm `get_history` truy vấn bảng `scores` theo `symbol` và sắp xếp giảm dần theo ngày.
- **Backend**: Thêm endpoint `/api/history` nhận tham số `symbol`.
- **Frontend**:
    - Sử dụng `Chart.js` để vẽ đồ thị.
    - Thiết kế layout `Split Screen` bằng CSS Flexbox (Trên: Table, Dưới: Chart).
    - Cập nhật `app.js` để xử lý sự kiện Tra cứu và Vẽ lại đồ thị (Destroy cũ, Create mới).

## 3. Các file ảnh hưởng (Affected Files)
- `backend/database.py`: Thêm hàm truy vấn lịch sử.
- `backend/main.py`: Thêm endpoint API.
- `frontend/index.html`: Thêm Tab "Lịch sử" và Canvas cho Chart.js.
- `frontend/style.css`: Thêm style cho Split Layout và Chart.
- `frontend/app.js`: Logic fetch dữ liệu lịch sử và render đồ thị.

## 4. Rủi ro & Cách xử lý (Risks)
- **Rủi ro**: Lỗi 405/404 khi serve static file cùng lúc với API.
- **Xử lý**: Di chuyển `app.mount` xuống cuối file `main.py` để không đè lên các route `/api`.
- **Rủi ro**: Đồ thị bị chồng chéo khi tra cứu mã mới liên tục.
- **Xử lý**: Dùng `chart.destroy()` trước khi khởi tạo biểu đồ mới.

## 5. Auditor Review
- Kiến trúc đáp ứng đúng nhu cầu trực quan hóa.
- Việc tách cột Banker giúp minh bạch dữ liệu đầu vào.
