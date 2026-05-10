# Tài liệu Kỹ thuật: Hệ thống Chấm điểm Cổ phiếu VN100

Tài liệu này mô tả chi tiết thuật toán và quy trình xử lý dữ liệu cho Dashboard Chấm điểm Cổ phiếu.

## 1. Quy trình lấy dữ liệu MCDX Banker (Fireant)

Đây là quy trình mô phỏng thao tác người dùng trên trình duyệt Chrome (thông qua Playwright/CDP).

### Các bước thực hiện:
1.  **Điều hướng**: Truy cập trực tiếp vào URL biểu đồ của mã CP: `https://fireant.vn/dashboard/content/symbols/{symbol}`.
2.  **Chuyển Tab**: Click vào tab **"Biểu đồ"**.
3.  **Thêm chỉ báo (Workflow f(x))**:
    *   Click vào nút **Chỉ báo (f(x))** trên thanh công cụ biểu đồ.
    *   Nhập từ khóa **"MCDX"** vào ô tìm kiếm.
    *   Click chọn chỉ báo **"FireAnt - MCDX"** (hoặc FA MCDX).
    *   Nhấn phím **ESC** để đóng cửa sổ danh sách chỉ báo.
4.  **Đợi tính toán**: Chờ 5 giây để chỉ báo load và vẽ dữ liệu trên Canvas.
5.  **Trích xuất Legend**:
    *   Tìm thẻ `div` chứa nội dung chú giải có từ khóa **"MCDX"**.
    *   Bóc tách dãy số hiển thị sau các tham số đầu vào.
    *   **Vị trí Banker**: Lấy giá trị **thứ 2 hoặc thứ 3 tính từ phải qua** trong dãy số chính (trước các ký hiệu lưới ∅).
6.  **Quy đổi điểm MCDX**:
    *   Sử dụng nội suy tuyến tính dựa trên giá trị Banker (0-20):
        *   0 -> 0.0 điểm
        *   3 -> 0.2 điểm
        *   8 -> 0.4 điểm
        *   12 -> 0.6 điểm
        *   16 -> 0.8 điểm
        *   20 -> 1.0 điểm

## 2. Quy trình tính toán RRG (Relative Rotation Graph)

Dữ liệu được tính toán dựa trên giá đóng cửa lịch sử (100 phiên gần nhất) lấy từ API `vnstock` (nguồn TCBS).

### Các bước tính toán:
1.  **Chuẩn bị**: Lấy giá đóng cửa của Mã CP và VNINDEX.
2.  **Relative Strength (RS)**: `RS = Price_Stock / Price_Index`.
3.  **RS-Ratio (Trục X)**:
    *   `WMA_RS = Weighted_Moving_Average(RS, 14)`.
    *   `RS_Ratio = 100 * (RS / WMA_RS)`.
4.  **RS-Momentum (Trục Y)**:
    *   `WMA_Ratio = Weighted_Moving_Average(RS_Ratio, 14)`.
    *   `RS_Mom = 100 * (RS_Ratio / WMA_Ratio)`.
5.  **Xác định Vùng RRG**:
    *   **Leading (Tăng giá)**: `RS_Ratio >= 100` AND `RS_Mom >= 100` -> **1.0 điểm**.
    *   **Improving (Tích lũy)**: `RS_Ratio < 100` AND `RS_Mom >= 100` -> **0.75 điểm**.
    *   **Weakening (Suy yếu)**: `RS_Ratio >= 100` AND `RS_Mom < 100` -> **0.5 điểm**.
    *   **Lagging (Giảm giá)**: `RS_Ratio < 100` AND `RS_Mom < 100` -> **0.25 điểm**.
6.  **Tail 5D**: Khoảng cách Euclidean giữa các điểm (Ratio, Mom) của 5 phiên gần nhất.

## 3. Tổng hợp điểm số (Total Score)

`Tổng điểm = Điểm RRG + Điểm MCDX`
*   **Điểm tối đa**: 2.0 điểm.
*   **Sắp xếp**: Dashboard hiển thị danh sách sort từ cao xuống thấp theo Tổng điểm.

## 4. Cơ chế cập nhật & Public

1.  **Local**: Chạy script batch và python server trên máy để lấy session Fireant.
2.  **Export**: Kết quả được xuất ra file `frontend/data.json`.
3.  **Sync**: Tự động chạy `git push` để đẩy dữ liệu lên GitHub.
4.  **Vercel**: Tự động redeploy và hiển thị dữ liệu mới nhất cho người xem công khai.
