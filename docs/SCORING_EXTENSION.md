# Scoring Extension Notes

File này là checklist ngắn để thêm chỉ báo mới vào hệ thống điểm.

## Nguyên tắc

- Mỗi chỉ báo mới phải được quy đổi thành một component score độc lập.
- Không tính RRG bằng `total_score - mcdx_score`.
- `total_score` chỉ là tổng của các component.
- Raw values và score values nên tách riêng để dễ kiểm chứng.

## Điểm hiện tại

```text
total_score = mcdx_score + rrg_score + adx_score + other_extra_scores
```

Trong đó:

- `mcdx_score`: từ Banker `FA_MCDX`.
- `rrg_score`: từ quadrant `FA_RRG`.
- `adx_score`: từ `ADX(14)` + `PDI(14)`/`MDI(14)`, max 0.5 trong V1.
- `extra_score`: tổng các component mở rộng ngoài MCDX/RRG, hiện gồm ADX.
- `score_max`: hiện là 2.5.

## Quy trình thêm chỉ báo

1. Đặt tên component, ví dụ `volume_score`, `trend_score`, `liquidity_score`.
2. Quy định raw input cần lấy từ đâu: AFL, AmiBroker quotations, hoặc nguồn ngoài.
3. Viết hàm quy đổi raw input thành điểm 0-1 trong `backend/scoring.py`.
4. Truyền điểm mới vào:

```python
payload = build_score_payload(
    mcdx_score=mcdx_score,
    rrg_score=rrg_score,
    extra_components={
        "volume": volume_score,
    },
    extra_component_maxes={
        "volume": 1.0,
    },
)
```

5. Lưu raw value riêng nếu cần audit.
6. Chạy lại batch và kiểm tra `score_components` trong `frontend/data_vn30.json`.

## Chỗ cần sửa thường gặp

- `backend/run_amibroker_vn30.py`: thêm raw value vào AFL output và parse.
- `backend/scoring.py`: thêm hàm tính điểm.
- `backend/database.py`: chỉ cần thêm cột nếu muốn lưu raw value mới.
- `frontend/app.js`: chỉ cần sửa nếu muốn hiển thị component mới thành cột riêng.
