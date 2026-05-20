# Retest Checklist (AmiBroker via COM)

## Pre-flight

- [ ] AmiBroker 32-bit mở được bằng tay.
- [ ] FireAnt plugin load thành công trong UI.
- [ ] Python 32-bit + `pywin32` hoạt động.
- [ ] Xác nhận quyền ghi `C:\Windows\Temp` và `C:\Users\Public`.

## Batch A — xác nhận baseline COM

- [ ] `ab_com_probe.py` chạy OK, dump ra `artifacts/com_probe.json`.
- [ ] `AnalysisDocs.Open()` mở được APX template.
- [ ] `Run(scan)` có vòng đời `IsBusy: True -> False`.

## Batch B — retest blocker fopen

- [ ] Dùng APX trỏ `test_write.afl`, chạy qua COM.
- [ ] Kiểm tra `C:\Windows\Temp\ami_test.txt`.
- [ ] Chạy cùng formula bằng UI (Analysis -> Scan), so sánh kết quả.

## Batch C — luồng thay thế (không fopen)

- [ ] Exploration formula `test_exploration_export.afl` chạy được.
- [ ] Export CSV từ Analysis tạo file thật.
- [ ] Parse CSV lấy các cột: banker, rs_ratio, rs_mom, quadrant.

## Batch D — static var bridge

- [ ] Formula `test_staticvar_bridge.afl` chạy scan/exploration được.
- [ ] Xác nhận StaticVar tồn tại qua các symbol trong 1 run.
- [ ] Đánh giá có đọc được từ COM hay bắt buộc qua export.

## Exit criteria

- [ ] Có ít nhất 1 luồng ổn định cho 100 symbols dưới 5 phút.
- [ ] Ghi lại decision: giữ COM hay quay lại hybrid.
