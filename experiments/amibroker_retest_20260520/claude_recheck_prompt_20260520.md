# Prompt de dua cho Claude kiem tra lai

Ban hay review lai ket qua retest AmiBroker trong repo nay. Muc tieu la kiem tra doc lap xem ket luan "AmiBroker COM + AFL fopen + FA_MCDX/FA_RRG bridge da chay duoc" co dung khong, va chi ra neu co loi logic, artifact khong du, hoac rui ro khi dua vao backend.

Thu muc lam viec:

```text
experiments/amibroker_retest_20260520/
```

Doc truoc cac file:

```text
experiments/amibroker_retest_20260520/full_runtime_retest_report_20260520.md
experiments/amibroker_retest_20260520/runtime_retest_results_20260520.md
experiments/amibroker_retest_20260520/scripts/run_retest_scan.py
experiments/amibroker_retest_20260520/apx/fa_bridge_oneline_current.apx
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.stdout.log
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.csv
experiments/amibroker_retest_20260520/artifacts/simple_fopen_oneline_current.csv
experiments/amibroker_retest_20260520/artifacts/force_rows_current.csv
experiments/amibroker_retest_20260520/artifacts/com_probe_64bit.json
```

Ket qua pass can verify:

```text
C:\Users\Public\ag_fa_bridge_oneline_out.txt
```

Noi dung pass da quan sat:

```text
symbol=VNINDEX;banker=11.240301;hotmoney=19.879290;rs_ratio=0.000000;rs_mom=0.000000;quadrant=3;tail_5d=0.000000;ready=1
```

CSV pass:

```text
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.csv
```

Noi dung:

```csv
Ticker,Date/Time,symbol,banker,hotmoney,rs_ratio,rs_mom,quadrant,tail_5d,fh_ok
VNINDEX,5/20/2026 00:00:00,VNINDEX,11.240301,19.879290,0.000000,0.000000,3,0.000000,1
```

Lenh pass can review:

```powershell
python experiments\amibroker_retest_20260520\scripts\run_retest_scan.py `
  --apx "experiments\amibroker_retest_20260520\apx\fa_bridge_oneline_current.apx" `
  --action explore `
  --timeout 90 `
  --wait-file "C:\Users\Public\ag_fa_bridge_oneline_out.txt" `
  --export "experiments\amibroker_retest_20260520\artifacts\fa_bridge_waitfile_current.csv"
```

Nhung diem toi muon ban kiem tra ky:

1. Ket luan `fopen()` khong bi chan co duoc chung minh du bang `simple_fopen_oneline_current.csv` va output file khong?
2. Ket luan `FA_MCDX` / `FA_RRG` chay trong AmiBroker qua COM co duoc chung minh du bang `fa_bridge_waitfile_current.csv` va output file khong?
3. Co rui ro gi khi dung `ready=1` file marker thay vi doi `IsBusy=False`?
4. APX `FormulaContent` hien tai co rui ro XML/import nao nua khong?
5. Viec output hien tai la `VNINDEX` co anh huong ket luan khong? Can lam gi de chay dung symbol nhu `VCB`, `HPG`, hoac danh sach VN100?
6. Co nen tach bridge thanh template APX/AFL rieng va de Python set current symbol/universe khong?
7. Co test thieu nao truoc khi dua vao backend that?

Hay tra loi theo format:

```text
Verdict:
- Pass / Partial / Fail

Evidence checked:
- ...

Issues found:
- Severity, file/path, reason

Recommended next implementation:
- ...

Minimal retest command:
- ...
```

Khong sua file backend cu. Neu can tao file test moi, chi tao trong:

```text
experiments/amibroker_retest_20260520/
```

