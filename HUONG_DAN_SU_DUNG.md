# 📖 Hướng dẫn Sử dụng VN100 Stock Scorer

Hệ thống chấm điểm cổ phiếu tự động dựa trên **MCDX (Dòng tiền nhà cái)** và **RRG (Chu kỳ sức mạnh giá)**.

---

## 🚀 3 Bước Vận hành Hàng ngày

### Bước 1: Khởi động hệ thống
- Click đúp vào file **`CHAY_HE_THONG.bat`** ở thư mục gốc.
- Hệ thống sẽ tự động mở Chrome (đã bật sẵn Fireant) và Dashboard.

### Bước 2: Kiểm tra Đăng nhập
- Trong cửa sổ Chrome vừa hiện ra, hãy đảm bảo bạn đã **đăng nhập vào Fireant**.
- Script sẽ tự động thao tác trên chính cửa sổ này của bạn.

### Bước 3: Chấm điểm & Cập nhật
- Tại trang Dashboard (`http://localhost:8888`), nhấn nút **"Cập nhật ngay"**.
- **Quan sát**: Trình duyệt sẽ tự động nhảy tab, thêm chỉ báo MCDX và lấy số.
- Sau khi chạy xong (cho VN30 hoặc VN100), hệ thống sẽ tự động đẩy kết quả lên **Vercel** để bạn xem trên điện thoại hoặc khoe bạn bè.

---

## 🛠 Giải quyết sự cố thường gặp

1.  **Nút "Cập nhật" không chạy?**
    - Kiểm tra xem file `CHAY_HE_THONG.bat` có đang mở không.
    - Đảm bảo terminal không báo lỗi kết nối Chrome (Port 9222).

2.  **Điểm MCDX bằng 0?**
    - Đảm bảo trong Chrome đã load được biểu đồ Fireant.
    - Nếu script không tự thêm được chỉ báo, hãy thử nhấn phím `f(x)` trên biểu đồ và thêm "FA MCDX" thủ công một lần.

3.  **Muốn dừng giữa chừng?**
    - Tắt cửa sổ Terminal (màu đen) đang chạy là hệ thống sẽ dừng.

---
*Chúc bạn săn được những siêu cổ phiếu với dòng tiền cá mập mạnh nhất!* 📈
