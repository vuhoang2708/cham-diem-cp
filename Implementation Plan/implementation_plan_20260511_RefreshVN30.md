# Implementation Plan: Refresh VN30 Data (2026-05-11)

## 1. Mô tả yêu cầu
Chạy lại toàn bộ quy trình chấm điểm cho 30 mã cổ phiếu VN30 để cập nhật dữ liệu mới nhất cho ngày 11/05/2026.

## 2. Các bước thực hiện
- Chạy lệnh `run_scoring` với tham số `category='vn30'`.
- Sử dụng Scraper đã được tối ưu hóa (hỗ trợ đa ký hiệu phân cách).
- Lưu kết quả vào SQLite và export ra `frontend/data.json`.

## 3. Các file ảnh hưởng
- `data/scores.db`: Thêm bản ghi mới cho ngày 11/05/2026.
- `frontend/data.json`: Cập nhật dữ liệu hiển thị.

## 4. Kiểm tra & Xác nhận
- Kiểm tra log để đảm bảo không có mã nào bị trả về Banker = 0.0 do lỗi parsing.
- Xác nhận file `data.json` đã chứa ngày mới.

## 5. Auditor Review
- Đảm bảo Chrome đang mở ở port 9222 để Scraper kết nối được.
