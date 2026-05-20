# AmiBroker Retest Workspace (2026-05-20)

Thư mục này chứa **toàn bộ thử nghiệm mới** để kiểm tra lại hướng lấy dữ liệu từ AmiBroker (không phụ thuộc FireAnt web scrape), tách biệt khỏi code trước đó để tránh nhầm lẫn.

## Mục tiêu retest

1. Xác nhận lại đường đi bị fail trước đây (`fopen` qua COM scan).
2. Thử các luồng thay thế không cần `fopen`:
   - Exploration output (AddColumn + export CSV từ Analysis)
   - StaticVarSet/Get để truyền dữ liệu trong AFL runtime
   - Trigger theo lô symbol có giới hạn thay vì all-symbol scan
3. Chuẩn hóa checklist để chạy lại trên máy Windows có AmiBroker.

## Cấu trúc

- `retest_checklist.md`: checklist chạy retest theo thứ tự.
- `amibroker_flows_matrix.md`: ma trận các luồng dữ liệu khả thi + rủi ro + tiêu chí pass/fail.
- `scripts/ab_com_probe.py`: probe COM API surface chi tiết hơn bản trước.
- `scripts/run_retest_scan.py`: runner COM cho APX với logging + timeout.
- `afl/test_exploration_export.afl`: công thức Exploration-only để thử export không dùng `fopen`.
- `afl/test_staticvar_bridge.afl`: công thức thử bridge qua StaticVar.

## Cách dùng nhanh

> Chạy trên **Windows + Python 32-bit + pywin32** cùng môi trường AmiBroker 32-bit.

1. Chạy probe API:

```bash
python scripts/ab_com_probe.py --out artifacts/com_probe.json
```

2. Chạy scan retest với APX trỏ đến AFL tương ứng:

```bash
python scripts/run_retest_scan.py --apx "C:\\Users\\Public\\test_export.apx" --mode scan --timeout 600
```

3. Ghi kết quả vào `artifacts/` và cập nhật `retest_checklist.md`.

## Nguyên tắc

- Không sửa/đè các file cũ trong `backend/` trừ khi đã xác nhận đường mới pass.
- Mọi thử nghiệm mới phải ghi log có timestamp trong `artifacts/`.
