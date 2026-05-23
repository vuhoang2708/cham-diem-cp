# BẢN KẾ HOẠCH THỰC THI (IMPLEMENTATION PLAN)
## Tác vụ: Bổ sung Checkbox tại Tiêu đề Bảng (Table Header) & Đồng bộ Trạng thái
**Ngày tạo:** 2026-05-23
**Dự án:** VN100 Stock Scorer

---

## 1. MÔ TẢ YÊU CẦU (PROBLEM STATEMENT)
**Nhu cầu của người dùng:** 
Thay vì chỉ thao tác bật/tắt (Tick/Untick) ở các nút trên thanh Header Công thức, người dùng muốn thao tác trực tiếp ngay tại **Tiêu đề của Bảng xếp hạng (Table Header)**.
Khi người dùng Untick một tiêu chí tại Bảng:
1. Toàn bộ cột dữ liệu bên dưới của tiêu chí đó sẽ **bị làm mờ đi (Dimmed out)**.
2. Dấu tick trên thanh Công thức (Criteria Pills) phía trên cùng cũng phải **tự động bỏ tick (Đồng bộ 2 chiều - Two-way binding)**.
3. Điểm số tự động tính toán lại.

## 2. GIẢI PHÁP KỸ THUẬT (TECHNICAL SOLUTION)

Để giải quyết tinh tế yêu cầu UX/UI này, tôi sẽ áp dụng giải pháp đồng bộ hóa trạng thái (State Sync) như sau:

**1. Sửa đổi `index.html`:**
*   Thêm trực tiếp thẻ `<input type="checkbox">` vào bên trong 3 thẻ `<th>` của bảng: `MCDX Score`, `RRG Score` và `ADX Score`.
*   **Quan trọng (Failsafe):** Gắn thuộc tính `onclick="event.stopPropagation()"` vào checkbox để khi người dùng click vào ô vuông, nó không vô tình kích hoạt lệnh Sắp xếp (Sort) cột của bảng.

**2. Sửa đổi `style.css`:**
*   Bổ sung thêm một CSS class mới: `.dimmed-col { opacity: 0.25; filter: grayscale(1); transition: all 0.3s ease; }`.
*   Class này sẽ được dùng để làm mờ toàn bộ văn bản và số liệu của cột bị bỏ tick.

**3. Sửa đổi `app.js` (Logic cốt lõi):**
*   Viết hàm `toggleCriteria(type, event)`: Hàm này sẽ nhận diện người dùng vừa tick/untick ở tiêu chí nào, sau đó tự động **đồng bộ (sync)** trạng thái giữa checkbox ở Tiêu đề Bảng (Header Bảng) và checkbox ở Công thức (Criteria Pills ở trên cùng).
*   Chỉnh sửa hàm `renderTable()`: Trong quá trình lặp (map) dữ liệu để vẽ các thẻ `<td>`, tôi sẽ thêm class `.dimmed-col` vào các thẻ `<td>` tương ứng nếu tiêu chí đó đang trong trạng thái `Untick`. (Ví dụ: Nếu `dynamicOptions.mcdx = false` thì thẻ `<td>` chứa điểm MCDX sẽ bị gắn class mờ).

---

## 3. CÁC TỆP BỊ ẢNH HƯỞNG (AFFECTED FILES)
1.  `frontend/index.html` (Thêm checkboxes vào thead th).
2.  `frontend/style.css` (Thêm class làm mờ cột `.dimmed-col`).
3.  `frontend/app.js` (Hàm đồng bộ Checkbox 2 chiều và chèn class mờ khi render table).

---

## 4. RỦI RO TIỀM ẨN & KẾ HOẠCH ROLLBACK (RISKS)
*   **Rủi ro:** Khi thêm Checkbox vào trong thẻ `<th>` vốn đã có sự kiện click để Sắp xếp (Sort), việc bấm nhầm có thể gây xung đột sự kiện.
*   **Giải pháp:** Áp dụng `event.stopPropagation()` bắt buộc trên mọi Checkbox để cách ly sự kiện click.
*   **Rollback:** Nếu không tương thích, dùng lệnh `git restore` hoặc checkout lại nhánh `main` mới nhất để quay về bản cũ.

---

## 5. MỤC KIỂM TOÁN (AUDITOR REVIEW)
*   [ ] Đảm bảo cơ chế đồng bộ 2 chiều (Two-way binding): Click ở Table Header thì Formula Header cũng thay đổi, và ngược lại.
*   [ ] Toàn bộ cột của bảng phải mờ đi rõ rệt để báo hiệu trực quan cho người dùng.
*   [ ] Đã tuân thủ Rule 1.1 & Rule 1.4, lưu kế hoạch vào thư mục chuẩn `Implementation Plan`.

---
> [!IMPORTANT]
> **HARD-GATE APPROVAL REQUIRED (Rule 1.2)**
> Thiết kế UX/UI cho Table Header đã sẵn sàng. Bạn vui lòng gõ **"Đồng ý"**, **"OK"** hoặc **"Approve"** để tôi bắt tay vào gõ code triển khai tính năng tuyệt vời này!
