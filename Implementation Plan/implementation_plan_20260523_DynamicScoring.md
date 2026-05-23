# BẢN KẾ HOẠCH THỰC THI (IMPLEMENTATION PLAN)
## Tác vụ: Tính năng Chấm điểm Tổng Động (Dynamic Scoring Calculation)
**Ngày tạo:** 2026-05-23
**Người lập kế hoạch:** Agent
**Dự án:** VN100 Stock Scorer (Chấm điểm cổ phiếu)

---

## 1. MÔ TẢ VẤN ĐỀ VÀ NHU CẦU (PROBLEM STATEMENT & ROOT CAUSE)
**Hạn chế hiện tại:** Hệ thống đang tính toán Tổng điểm (Total Score) và Điểm tuyệt đối (Score Max = 2.50) bằng cách cộng "cứng" (hardcode) tất cả 3 chỉ số (MCDX, RRG, ADX). Cả phía DB và Frontend đều sử dụng giá trị fix này. 
**Vấn đề:** Điều này gây thiếu linh hoạt. Nếu người dùng chỉ muốn xem xếp hạng theo MCDX và ADX (bỏ qua RRG), họ không thể loại trừ điểm RRG ra khỏi Tổng điểm và không thể sort lại bảng xếp hạng dựa trên tiêu chí mới.

## 2. GIẢI PHÁP KỸ THUẬT (TECHNICAL SOLUTION)
Vì dữ liệu đầu vào (từng điểm thành phần `mcdx_score`, `rrg_score`, `adx_score`) đã được Backend cung cấp đầy đủ và tách biệt qua API/JSON, chúng ta **không cần thay đổi Backend hay Database**. Toàn bộ logic tính toán "Động" sẽ được xử lý ở Client-Side (Frontend - JavaScript) để đảm bảo tốc độ phản hồi ngay lập tức (Real-time UI).

**Các bước triển khai chi tiết:**

1.  **Chỉnh sửa Giao diện (`frontend/index.html` & `style.css`):**
    *   Chuyển đổi khu vực `criteria-pills` (MCDX Banker, RRG Quadrant) trên Header thành các khối **Checkbox Toggles** có thể click bật/tắt (Tick/Untick).
    *   Bổ sung thêm 1 khối Toggle cho **ADX Score**.
    *   Thêm CSS cho trạng thái `:checked` và `:not(:checked)` của các nút này (ví dụ: Làm mờ nút bị untick).

2.  **Cập nhật Logic tính điểm (`frontend/app.js`):**
    *   Khởi tạo bộ trạng thái (State) quản lý các tiêu chí được chọn: 
        `let activeIndicators = { mcdx: true, rrg: true, adx: true };`
    *   Viết hàm mới `recalculateDynamicScores()`: Lặp qua toàn bộ mảng `allData`, tự động tính toán lại 2 tham số:
        *   `d.dynamic_total = (mcdx ? d.mcdx_score : 0) + (rrg ? d.rrg_score : 0) + (adx ? d.adx_score : 0)`
        *   **Dynamic Max:** Do JSON hiện tại chỉ lưu tổng `score_max` (ví dụ 2.5) và điểm đạt được trong `score_components`, ta sẽ tính động trần của ADX bằng cách lấy tổng trần trừ đi 2.0 (của MCDX và RRG).
        *   `let adx_max = d.score_max - 2.0;`
        *   `dynamic_max = (mcdx ? 1.0 : 0) + (rrg ? 1.0 : 0) + (adx ? adx_max : 0)`
    *   Sửa đổi hàm Sort, Render Table, Export CSV để sử dụng `dynamic_total` thay vì `total_score` tĩnh từ DB.

3.  **Đồng bộ Biểu đồ Lịch sử (History Chart):**
    *   Khi người dùng đang ở tab "Lịch sử 10 ngày", đường (line) của Tổng điểm màu Vàng trong biểu đồ cũng phải được vẽ lại bằng cách tính tổng dựa trên cấu hình tiêu chí đang được tick.

4.  **Bảo vệ an toàn (Failsafe):**
    *   Trường hợp user Untick tất cả 3 tiêu chí $\rightarrow$ `dynamic_max = 0`. Sẽ gây lỗi chia cho 0 (Divide by Zero) khi vẽ thanh Progress bar.
    *   *Cách xử lý:* Bắt buộc phải có ít nhất 1 tiêu chí được chọn (Vô hiệu hóa việc bỏ tick nếu chỉ còn 1 tiêu chí đang active), hoặc gán `dynamic_max = 1` nếu bằng 0 để tránh lỗi NaN.

---

## 3. CÁC TỆP BỊ ẢNH HƯỞNG (AFFECTED FILES)
1.  `C:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu\frontend\index.html`
2.  `C:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu\frontend\style.css`
3.  `C:\Users\Nguyen To Dung\.gemini\antigravity\scratch\Cham diem co phieu\frontend\app.js`

---

## 4. RỦI RO TIỀM ẨN & KẾ HOẠCH ROLLBACK (RISKS & ROLLBACK)
*   **Rủi ro:** Khi tính lại tổng điểm, nếu người dùng click liên tục (spam clicks), có thể gây giật lag đồ thị Chart.js.
*   **Xử lý:** Hàm tính lại điểm rất nhẹ vì chỉ loop qua 100 object (VN100), nên thao tác này chạy chỉ tốn `~1ms`. Đồ thị Chart.js đã có sẵn hàm `destroy()` trước khi vẽ lại nên không lo tràn bộ nhớ.
*   **Rollback:** Nếu lỗi giao diện, chỉ cần `git checkout frontend/` về trạng thái cũ.

---

## 5. MỤC KIỂM TOÁN (AUDITOR REVIEW)
*   [ ] Đảm bảo **Không chạm vào Backend** (`main_scorer.py` hay CSDL `scores.db`). Đây thuần túy là UI Feature.
*   [ ] Cột Tổng điểm (`Total Score`) trên bảng phải tự động "nhảy" số (cập nhật động) khi Tick/Untick ngay lập tức mà không cần F5 trình duyệt.
*   [ ] Đã thêm thư mục con `Implementation Plan` chuẩn quy tắc Rule 1.4.

---
**HARD-GATE APPROVAL:** Đã lập xong bản thiết kế kỹ thuật. Chờ lệnh **"Đồng ý", "Approve", "OK"** từ User để tiến hành gõ Code thay đổi giao diện.
