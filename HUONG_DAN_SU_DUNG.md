# 📖 Hướng dẫn Sử dụng VN100 Stock Scorer (AmiBroker Version)

Hệ thống chấm điểm cổ phiếu tự động dựa trên **MCDX (Dòng tiền nhà cái)** và **RRG (Chu kỳ sức mạnh giá)** từ **AmiBroker**.

---

## 🚀 3 Bước Vận hành Hàng ngày

### Bước 1: Khởi động AmiBroker
- Mở ứng dụng **AmiBroker** (phải đang chạy để hệ thống lấy dữ liệu).
- Đảm bảo dữ liệu VN100 đã được load (File → Open → chọn database).

### Bước 2: Khởi động Dashboard
- Mở Terminal/PowerShell tại thư mục gốc dự án.
- Chạy lệnh:
  ```bash
  $env:DATA_SOURCE="amibroker"
  .\venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```
- Mở trình duyệt: `http://localhost:8000`

### Bước 3: Chấm điểm & Cập nhật
- Tại Dashboard, nhấn nút **"Cập nhật ngay"** cho danh mục mong muốn (VN30, VN100, Custom).
- Hệ thống sẽ lấy dữ liệu từ AmiBroker (~2 phút cho VN100).
- Kết quả hiển thị tự động sau khi hoàn thành.

---

## 🛠 Giải quyết sự cố thường gặp

1. **Lỗi "Cannot connect to AmiBroker"?**
   - Kiểm tra AmiBroker đã mở chưa.
   - Kiểm tra file `ami_bridge.afl` tồn tại tại `C:\Program Files (x86)\AmiBroker\Formulas\Custom\`.

2. **Điểm MCDX bằng 0?**
   - Kiểm tra FireAnt indicators đã cài trong AmiBroker (FA_MCDX, FA_RRG).
   - Mở AmiBroker Editor, chạy `ami_bridge.afl` thủ công để xem lỗi.

3. **Muốn dừng giữa chừng?**
   - Nhấn Ctrl+C trong Terminal để dừng server.

---

*Chúc bạn săn được những siêu cổ phiếu với dòng tiền cá mập mạnh nhất!* 📈
