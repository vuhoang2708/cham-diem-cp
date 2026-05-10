# Kế hoạch nâng cấp Giao diện 3 Tab & Lưu lịch sử dữ liệu

Hệ thống sẽ được nâng cấp để hỗ trợ 3 nhóm cổ phiếu riêng biệt (VN30, VN100, Import) và lưu trữ lịch sử biến động theo từng ngày.

## 1. Thay đổi Database (Lưu trữ lịch sử & Phân loại)

### [MODIFY] [database.py](file:///C:/Users/Nguyen%20To%20Dung/.gemini/antigravity/scratch/Cham%20diem%20co%20phieu/backend/database.py)
*   Cập nhật bảng `scores`:
    *   Thêm cột `category` (TEXT): VN30, VN100, CUSTOM.
    *   Cấu trúc Primary Key mới: `(symbol, category, updated_date)` để lưu dữ liệu theo từng ngày cho mỗi nhóm.
*   Cập nhật hàm `save_score`: Tự động tách ngày từ `datetime.now()` để làm mốc lịch sử.
*   Cập nhật hàm `get_latest_scores(category)`: Chỉ lấy dữ liệu mới nhất của mỗi mã trong nhóm để hiển thị lên bảng.

## 2. Thay đổi Logic Xử lý (Cập nhật toàn diện)

### [MODIFY] [main_scorer.py](file:///C:/Users/Nguyen%20To%20Dung/.gemini/antigravity/scratch/Cham%20diem%20co%20phieu/backend/main_scorer.py)
*   Hàm `run_scoring(category, symbols)`:
    *   Thực hiện đầy đủ: 
        1. Lấy dữ giá lịch sử -> Tính RRG (RS Ratio, RS Momentum).
        2. Chạy Scraper -> Lấy Banker (MCDX).
        3. Tổng hợp điểm.
    *   Lưu vào DB với nhãn `category` và thời gian hiện tại.

## 3. Cập nhật API Server

### [MODIFY] [main.py](file:///C:/Users/Nguyen%20To%20Dung/.gemini/antigravity/scratch/Cham%20diem%20co%20phieu/backend/main.py)
*   `GET /api/scores?category=...`: Trả về danh sách nến mới nhất của nhóm đó.
*   `POST /api/refresh?category=...`: Kích hoạt tiến trình chạy lại toàn bộ tiêu chí cho nhóm được chọn.
*   `POST /api/import`: Nhận danh sách mã CP (string hoặc file) và lưu vào danh sách `custom_symbols.json`.

## 4. Giao diện (3 Tab & Nút bấm riêng)

### [MODIFY] [index.html](file:///C:/Users/Nguyen%20To%20Dung/.gemini/antigravity/scratch/Cham%20diem%20co%20phieu/frontend/index.html) & [app.js](file:///C:/Users/Nguyen%20To%20Dung/.gemini/antigravity/scratch/Cham%20diem%20co%20phieu/frontend/app.js)
*   Thiết kế Tab: VN30 | VN100 | Danh mục tùy chỉnh.
*   Nút "Cập nhật toàn bộ": Gửi lệnh refresh kèm category tương ứng.
*   Tab Tùy chỉnh: Thêm Textarea và nút "Lưu danh sách" để người dùng nhập mã CP.

## 5. Auditor Review
*   **Root Cause**: User cần theo dõi nhiều danh mục và muốn xem lại biến động trong quá khứ.
*   **Technical Solution**: Chuyển từ "Update/Replace" sang "Append" trong database với mốc thời gian.
*   **Risk**: Dung lượng Database sẽ tăng theo thời gian. Tuy nhiên với 100-200 mã CP thì SQLite vẫn xử lý cực tốt trong vài năm.

---
**Vui lòng xác nhận "Đồng ý" để tôi bắt đầu thực hiện.**
