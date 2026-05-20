# Implementation Plan: Switch Data Source from Fireant (Web) to AmiBroker (OLE/COM)

## 1. Mô tả Root Cause & Ngữ cảnh (Context)
*   **Vấn đề hiện tại**: Việc cào dữ liệu MCDX từ Fireant bằng Playwright đang gặp các hạn chế:
    *   **Tốc độ chậm**: Mất khoảng 45-60 giây cho mỗi mã cổ phiếu (~75 phút cho VN100).
    *   **Kém ổn định**: Phụ thuộc vào giao diện web (Selector có thể vỡ) và tốc độ mạng.
    *   **Tốn tài nguyên**: Phải mở trình duyệt và tương tác UI liên tục.
*   **Giải pháp đề xuất**: Chuyển sang lấy dữ liệu trực tiếp từ ứng dụng **AmiBroker** đang chạy trên máy thông qua cổng **OLE Automation (COM)**. 
    *   AmiBroker đã có sẵn dữ liệu và chỉ báo (MCDX, RRG) thông qua các file AFL của Fireant.
    *   Python sẽ "hỏi" trực tiếp giá trị biến từ AmiBroker mà không cần mở trình duyệt.

## 2. Giải pháp kỹ thuật (Technical Solution)
*   **Công cụ**: Sử dụng thư viện `pywin32` để Python giao tiếp với AmiBroker COM Object.
*   **Cơ chế "Cầu nối" (The Bridge)**:
    1.  Tạo một file AFL `backend/ami_bridge.afl` chứa logic gọi hàm `FA_MCDX` và `FA_RRG`.
    2.  Python sẽ ra lệnh cho AmiBroker:
        *   Load mã cổ phiếu cần chấm điểm.
        *   Chạy file AFL cầu nối.
        *   Đọc giá trị của các biến `mcdx_Banker`, `rrg_Quadrant`, v.v. trả về từ bộ nhớ của AmiBroker.
*   **Ưu điểm**: 
    *   Tốc độ: < 1 giây/mã (VN100 chỉ mất < 2 phút thay vì 75 phút).
    *   Ổn định 100% vì không phụ thuộc vào UI web.

## 3. Các file bị ảnh hưởng (Affected Files)
*   `requirements.txt`: Thêm `pywin32`.
*   `backend/ami_bridge.afl` (Mới): File công thức để AmiBroker tính toán và xuất dữ liệu cho Python.
*   `backend/scraper_amibroker.py` (Mới): Module Python thực hiện kết nối COM.
*   `backend/main_scorer.py`: Chỉnh sửa để ưu tiên lấy dữ liệu từ module AmiBroker mới.

## 4. Rủi ro tiềm ẩn (Potential Risks)
*   **AmiBroker phải đang mở**: Nếu phần mềm AmiBroker không chạy, Python sẽ báo lỗi kết nối.
*   **Phiên bản AmiBroker**: Yêu cầu AmiBroker bản 6.0 trở lên (bản Crack vẫn hoạt động tốt).
*   **AFL Dependency**: AmiBroker cần cài sẵn các bộ chỉ báo FireAnt (đã xác nhận là máy bạn đã có).

## 5. Quy trình thực hiện (Execution Steps)
1.  **Bước 1**: Cập nhật `requirements.txt` và cài đặt `pywin32`.
2.  **Bước 2**: Tạo file `backend/ami_bridge.afl` với nội dung trích xuất từ các file AFL gốc đã tìm thấy.
3.  **Bước 3**: Xây dựng module `backend/scraper_amibroker.py` để kết nối và test lấy dữ liệu cho mã VCB.
4.  **Bước 4**: Tích hợp vào `main_scorer.py` và cập nhật Dashboard.

## 6. Kiểm tra & Xác nhận (Verification)
*   Chạy lệnh test lấy điểm VCB từ AmiBroker.
*   So sánh giá trị Banker và Vùng RRG giữa Dashboard và màn hình AmiBroker để đảm bảo khớp 100%.

## 7. Auditor Review (Codex rà soát)
*   Đảm bảo việc kết nối COM không gây treo (hang) ứng dụng AmiBroker.
*   Xử lý lỗi (Exception handling) khi AmiBroker chưa được mở hoặc mã CP không tồn tại trong database của AmiBroker.

---
**Agent: Antigravity**
**Date: 2026-05-16**
