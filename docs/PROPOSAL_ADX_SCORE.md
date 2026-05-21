# Đề xuất kỹ thuật: Tích hợp ADX Score

**Ngày:** 2026-05-21  
**Trạng thái:** Đã implement công thức V1

---

## 1. Bối cảnh

Hệ thống hiện tại có 2 component chính:

| Component | Max | Nguồn |
|---|---|---|
| `mcdx_score` | 1.0 | FA_MCDX — dòng tiền Banker/HotMoney |
| `rrg_score` | 1.0 | FA_RRG — sức mạnh tương đối so với VNINDEX |
| **Total** | **2.0** | |

ADX bổ sung chiều thứ 3: **xu hướng giá nội tại của cổ phiếu**, độc lập với benchmark.

---

## 2. Lý thuyết ADX + DI+/DI-

Ba đường của hệ thống Wilder DMI (mặc định period = 14):

- **ADX**: đo **độ mạnh** xu hướng, không phân biệt hướng. Range 0–100.
- **DI+**: áp lực mua (upward directional movement)
- **DI-**: áp lực bán (downward directional movement)

### Ngưỡng ADX chuẩn

| ADX | Ý nghĩa |
|---|---|
| < 20 | Sideway, không xu hướng |
| 20–25 | Xu hướng yếu / đang hình thành |
| 25–50 | Xu hướng mạnh |
| 50+ | Xu hướng rất mạnh |

### ADX Slope

`adx_slope = ADX[hôm nay] - ADX[N ngày trước]`

- **Slope > 0**: xu hướng đang tăng tốc → tín hiệu tốt hơn
- **Slope < 0**: xu hướng đang suy yếu → cẩn thận dù ADX vẫn cao
- ADX = 22 đang tăng có thể tốt hơn ADX = 35 đang giảm

---

## 3. Công thức tính điểm đề xuất

### 3.1 Điều kiện loại (score = 0 ngay)

```
DI- >= DI+  →  adx_score = 0.0
```

Cổ phiếu đang trong xu hướng giảm không được điểm, bất kể ADX bao nhiêu.

### 3.2 Điểm nền từ ADX hiện tại (khi DI+ > DI-)

```
ADX < 15       → adx_base = 0.00
15 <= ADX < 20 → adx_base = 0.10
20 <= ADX < 25 → adx_base = 0.30
25 <= ADX < 40 → adx_base = 0.60
40 <= ADX < 50 → adx_base = 0.80
ADX >= 50      → adx_base = 0.90
```

Lý do dùng thang bậc thay vì tuyến tính `ADX / 50`:

- ADX dưới 15 gần như nhiễu, không nên cộng điểm.
- ADX 15–20 vẫn là vùng yếu, chỉ cộng rất nhẹ.
- ADX 25+ mới là vùng xu hướng đáng tin hơn.
- ADX quá cao không tự động là điểm tuyệt đối vì có rủi ro mua đuổi.

### 3.3 Điều chỉnh theo ADX hôm qua và 3 ngày trước

```
slope_1d = ADX[hôm nay] - ADX[hôm qua]
slope_3d = ADX[hôm nay] - ADX[3 ngày trước]

Nếu slope_1d > 0 và slope_3d > +2  → adj += 0.10
Ngược lại nếu slope_3d > +2         → adj += 0.05

Nếu slope_1d < 0                    → adj -= 0.05
Nếu slope_3d < -2                   → adj -= 0.05
```

Ý nghĩa:

- So với hôm qua (`slope_1d`) để biết trend có đang mạnh lên ngay phiên mới nhất không.
- So với 3 ngày (`slope_3d`) để tránh phản ứng quá nhiễu với một phiên đơn lẻ.
- Nếu ADX 3 ngày vẫn tăng nhưng hôm nay đã quay đầu giảm, chỉ thưởng nhẹ hoặc bị phạt nhẹ tùy case.

### 3.4 Điều chỉnh theo độ rộng DI

```
di_spread = DI+ - DI-

Nếu di_spread >= 10  → adj += 0.05
```

DI+ chỉ cần lớn hơn DI- là đủ điều kiện vào scoring, nhưng nếu khoảng cách đủ rộng thì xu hướng tăng đáng tin hơn.

### 3.5 Tổng hợp

```
adx_raw_score = clamp(adx_base + adj, 0.0, 1.0)
```

Giai đoạn V1 dùng trọng số thận trọng:

```
adx_score = adx_raw_score * 0.5
```

Tức ADX đóng góp tối đa `0.5` điểm. Sau khi chạy vài phiên và xem phân phối điểm, có thể nâng trọng số lên `1.0` nếu thấy hợp lý.

### Ví dụ minh họa

| ADX | 1D | 3D | DI+ vs DI- | Spread | base | adj | raw | final |
|---|---|---|---|---|---|---|---|---|
| 35 | +1 | +5 | DI+ > DI- | 12 | 0.60 | +0.15 | 0.75 | **0.375** |
| 35 | -1 | +5 | DI+ > DI- | 12 | 0.60 | 0.00 | 0.60 | **0.300** |
| 22 | +1 | +4 | DI+ > DI- | 6 | 0.30 | +0.10 | 0.40 | **0.200** |
| 50 | +2 | +6 | DI+ > DI- | 15 | 0.90 | +0.15 | 1.00 | **0.500** |
| 30 | +1 | +3 | DI- > DI+ | — | — | — | — | **0.000** |
| 15 | +1 | +1 | DI+ > DI- | 5 | 0.10 | 0.00 | 0.10 | **0.050** |

---

## 4. Tác động lên tổng điểm

```
total_score = mcdx_score + rrg_score + adx_score
score_max   = 2.5
```

Tỷ trọng giai đoạn V1:

| Component | Max |
|---|---:|
| MCDX | 1.0 |
| RRG | 1.0 |
| ADX | 0.5 |
| **Total** | **2.5** |

Lý do không để ADX bằng MCDX/RRG ngay từ đầu: ADX và RRG đều thuộc nhóm xu hướng/sức mạnh giá, dễ bị double-count trend. Sau khi chạy vài phiên và kiểm phân phối điểm VN30, có thể cân nhắc nâng ADX lên max 1.0.

---

## 5. Nguồn dữ liệu

ADX, DI+, DI- là chỉ báo chuẩn, có sẵn trong AmiBroker AFL:

```afl
period = 14;
adx_val  = ADX(period);
dip_val  = PDI(period);   // DI+
dim_val  = MDI(period);   // DI-
adx_1d   = Ref(ADX(period), -1);
adx_3d   = Ref(ADX(period), -3);
adx_slope_1d = adx_val - adx_1d;
adx_slope_3d = adx_val - adx_3d;
```

Không cần plugin FireAnt — tính từ OHLC thuần túy.

### Thêm vào AFL bridge (ag_bridge.apx)

```afl
period = 14;
adx_val   = LastValue(ADX(period));
dip_val   = LastValue(PDI(period));
dim_val   = LastValue(MDI(period));
adx_1d    = LastValue(Ref(ADX(period), -1));
adx_3d    = LastValue(Ref(ADX(period), -3));

out = out + ";adx="      + NumToStr(adx_val, 1.4);
out = out + ";di_plus="  + NumToStr(dip_val, 1.4);
out = out + ";di_minus=" + NumToStr(dim_val, 1.4);
out = out + ";adx_1d="   + NumToStr(adx_1d, 1.4);
out = out + ";adx_3d="   + NumToStr(adx_3d, 1.4);
```

---

## 6. Thay đổi code cần làm

### backend/scoring.py
Thêm hàm:
```python
def score_adx(adx: float, di_plus: float, di_minus: float, adx_1d: float, adx_3d: float) -> float:
    if di_plus <= di_minus:
        return 0.0

    if adx < 15:
        base = 0.0
    elif adx < 20:
        base = 0.10
    elif adx < 25:
        base = 0.30
    elif adx < 40:
        base = 0.60
    elif adx < 50:
        base = 0.80
    else:
        base = 0.90

    slope_1d = adx - adx_1d
    slope_3d = adx - adx_3d

    adj = 0.0
    if slope_1d > 0 and slope_3d > 2:
        adj += 0.10
    elif slope_3d > 2:
        adj += 0.05

    if slope_1d < 0:
        adj -= 0.05
    if slope_3d < -2:
        adj -= 0.05

    if di_plus - di_minus >= 10:
        adj += 0.05

    raw_score = max(0.0, min(1.0, base + adj))
    return round(raw_score * 0.5, 4)
```

### backend/create_apx.py / run_amibroker_vn30.py
Thêm AFL output: `adx`, `di_plus`, `di_minus`, `adx_1d`, `adx_3d`.

### backend/main_scorer.py / run_amibroker_vn30.py
Parse 5 field mới từ output file, truyền vào `build_score_payload(extra_components={"adx": adx_score})`.

### backend/database.py
Thêm cột raw: `adx_value`, `di_plus`, `di_minus`, `adx_1d`, `adx_3d` (optional, cho audit).

### frontend/app.js
Tùy chọn: hiển thị `adx_score` thành cột riêng trong bảng.

---

## 7. Tham số đã chốt

| Tham số | Giá trị | Lý do |
|---|---|---|
| Period ADX | 14 | Chuẩn Wilder |
| Slope window | 1 ngày và 3 ngày | 1D bắt tín hiệu hôm qua, 3D giảm nhiễu |
| slope_adj tăng | +0.10 nếu 1D và 3D cùng tăng, +0.05 nếu chỉ 3D tăng rõ | Thưởng xu hướng đang tăng tốc |
| slope_adj giảm | -0.05 cho 1D giảm, -0.05 cho 3D giảm rõ | Phạt nhẹ khi trend yếu đi |
| Ngưỡng nhiễu | ±2 điểm | ADX dao động ±1-2/ngày là bình thường |
| DI spread bonus | +0.05 nếu `DI+ - DI- >= 10` | Thưởng xu hướng tăng có độ rộng rõ |
| Weight | ADX max 0.5 trong V1 | Tránh double-count trend với RRG; total max = 2.5 |

---

## 8. Rủi ro / hạn chế

- ADX là **lagging** — xác nhận xu hướng đã hình thành, không dự báo sớm
- Trong thị trường sideway (VN30 hay có giai đoạn tích lũy), ADX thấp → nhiều cổ phiếu bị điểm thấp dù fundamentals tốt
- Cần kiểm tra phân phối điểm trên toàn VN30 sau khi thêm để tránh score bị lệch
