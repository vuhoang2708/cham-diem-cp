# AmiBroker Data Flow Matrix

| Flow | Mô tả | Phụ thuộc | Ưu điểm | Rủi ro | Tiêu chí pass |
|---|---|---|---|---|---|
| F1: COM Scan + `fopen` | Chạy `AnalysisDocs.Run(scan)` và AFL tự ghi file | `fopen` usable | Đơn giản, nhanh | Đã fail trước đó qua COM | Có file output ổn định mỗi lần chạy |
| F2: COM Exploration + Export CSV | AFL dùng `AddColumn`, sau đó export kết quả Analysis | Analysis export engine | Không cần `fopen` trong AFL | Có thể cần automation thao tác UI / command không có trong COM | CSV đủ cột cho 100 mã |
| F3: COM + StaticVar bridge | AFL set `StaticVarSet`, bước khác đọc lại | AFL runtime state | Tránh file I/O trực tiếp | Có thể không persist giữa context | Đọc được dữ liệu nhất quán theo symbol |
| F4: OHLCV direct + tái hiện chỉ báo | Python đọc quotations, tự tính chỉ báo | Công thức FA_MCDX/FA_RRG tương đương | Không lệ thuộc scan/export | FA_* là proprietary, khó clone | Sai số trong ngưỡng chấp nhận |
| F5: Hybrid UI macro | COM mở Analysis, AutoHotkey macro export | UI automation | Vượt hạn chế COM API | Mong manh theo UI, dễ flaky | Chạy 3 lần liên tiếp đều pass |

## Khuyến nghị thứ tự thử

1. F1 để xác nhận blocker còn tồn tại hay không.
2. F2 vì khả năng khả thi cao nhất nếu `fopen` vẫn fail.
3. F3 để kiểm chứng giới hạn runtime.
4. F5 như phương án cuối cùng trước khi bỏ COM.
