# Bao cao retest AmiBroker runtime - 2026-05-20

## Muc tieu

Kiem tra lai that ky van de Claude fail truoc do: ket noi va xu ly du lieu trong AmiBroker thay vi dua vao FireAnt web scrape. Yeu cau la tao mot khu vuc thu nghiem rieng trong repo de khong lan voi cac file Claude dang xu ly.

Thu muc rieng da dung:

```text
experiments/amibroker_retest_20260520/
```

## Ket luan cuoi cung

Ket luan sau khi retest: **AmiBroker COM chay duoc, `fopen()` trong AFL chay duoc, va cac ham FA `FA_MCDX` / `FA_RRG` cung chay duoc qua COM**.

Loi Claude gap truoc do khong phai vi AmiBroker khong ket noi duoc hay `fopen` bi khoa. Nguyen nhan chinh la chuoi van de quanh APX/AFL import va lifecycle:

- APX co `FormulaPath` rong hoac tro sai lam AmiBroker hien modal loi va lam COM dung cho.
- `FormulaContent` trong APX neu encode sai se bi AmiBroker ghi thanh AFL loi.
- Raw `<` trong XML `FormulaContent` co the lam APX invalid.
- `"\n"` trong APX import co the bi bien thanh newline that ben trong chuoi AFL, gay loi cu phap.
- Cho `IsBusy=False` khong phai luc nao cung la dieu kien ket thuc tot nhat; voi bridge file nen cho output co `ready=1`.

Thanh cong cuoi cung la APX:

```text
experiments/amibroker_retest_20260520/apx/fa_bridge_oneline_current.apx
```

chay boi runner:

```text
experiments/amibroker_retest_20260520/scripts/run_retest_scan.py
```

va sinh output:

```text
C:\Users\Public\ag_fa_bridge_oneline_out.txt
```

Noi dung output thanh cong:

```text
symbol=VNINDEX;banker=11.240301;hotmoney=19.879290;rs_ratio=0.000000;rs_mom=0.000000;quadrant=3;tail_5d=0.000000;ready=1
```

CSV bang chung tu cung lan chay:

```csv
Ticker,Date/Time,symbol,banker,hotmoney,rs_ratio,rs_mom,quadrant,tail_5d,fh_ok
VNINDEX,5/20/2026 00:00:00,VNINDEX,11.240301,19.879290,0.000000,0.000000,3,0.000000,1
```

File bang chung CSV:

```text
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.csv
```

## Moi truong test

- OS: Windows 11
- Python: `C:\Users\Nguyen To Dung\AppData\Local\Programs\Python\Python312\python.exe`
- Python bitness: 64-bit
- `pywin32`: import duoc
- AmiBroker process quan sat duoc:

```text
D:\MetakitData\AmibrokerFA\EOD\Broker.exe
```

- AmiBroker COM ProgID:

```text
Broker.Application
```

Bang chung COM probe:

```text
experiments/amibroker_retest_20260520/artifacts/com_probe_64bit.json
```

Trich noi dung quan trong:

```json
{
  "python_bitness": "64bit",
  "probe": {
    "Version": { "ok": true, "repr": "'6.30.0'" },
    "AnalysisDocs": { "ok": true, "type": "CDispatch" },
    "Stocks": { "ok": true, "type": "CDispatch" },
    "Documents": { "ok": true, "type": "CDispatch" },
    "LoadDatabase": { "ok": true, "type": "method" },
    "RefreshAll": { "ok": true, "type": "method" },
    "Import": { "ok": true, "type": "method" }
  }
}
```

Mot so method khong co tren COM surface nay:

```text
CategoryAddSymbol
CategoryGetSymbols
SendCommand
ExecuteFormula
```

## File va artifact quan trong

Script:

```text
experiments/amibroker_retest_20260520/scripts/ab_com_probe.py
experiments/amibroker_retest_20260520/scripts/run_retest_scan.py
experiments/amibroker_retest_20260520/scripts/run_old_analysis.py
```

APX thanh cong:

```text
experiments/amibroker_retest_20260520/apx/force_rows_inline_current.apx
experiments/amibroker_retest_20260520/apx/simple_fopen_oneline_current.apx
experiments/amibroker_retest_20260520/apx/fa_bridge_oneline_current.apx
```

Artifact thanh cong:

```text
experiments/amibroker_retest_20260520/artifacts/force_rows_current.csv
experiments/amibroker_retest_20260520/artifacts/simple_fopen_oneline_current.csv
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.csv
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.stdout.log
```

Runtime output thanh cong ngoai repo:

```text
C:\Users\Public\ag_simple_fopen_oneline_out.txt
C:\Users\Public\ag_fa_bridge_oneline_out.txt
```

## Timeline retest chi tiet

### 1. Probe COM AmiBroker

Muc tieu: xac nhan Python co import duoc `win32com.client` va dispatch duoc `Broker.Application`.

Lenh y tuong:

```powershell
python experiments\amibroker_retest_20260520\scripts\ab_com_probe.py --out experiments\amibroker_retest_20260520\artifacts\com_probe_64bit.json
```

Ket qua:

- Pass.
- AmiBroker version `6.30.0`.
- `AnalysisDocs`, `Stocks`, `Documents`, `LoadDatabase`, `RefreshAll`, `Import` co mat.
- Python 64-bit van dung duoc voi COM AmiBroker tren may nay.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/com_probe_64bit.json
```

### 2. Thu lai APX cu `ag_bridge_all.apx`

Muc tieu: tai hien luong cu co `fopen` va FA functions trong `C:\Users\Public\ag_bridge_all.apx`.

Ket qua:

- COM dispatch duoc.
- `AnalysisDocs.Open()` duoc.
- Bi dung o buoc `doc.Run(...)`.
- Khong tao output `C:\Users\Public\ag_bridge_out.txt`.

Bang chung log:

```text
experiments/amibroker_retest_20260520/artifacts/ag_bridge_all_runner.stdout.log
```

Noi dung log:

```text
step=import_win32com
step=dispatch Broker.Application
step=open_analysis_doc apx=C:\Users\Public\ag_bridge_all.apx
step=run mode=scan apx=C:\Users\Public\ag_bridge_all.apx
```

Quan sat UI do user cung cap:

```text
C:\Users\Nguyen To Dung\Pictures\Screenshots\Screenshot 2026-05-20 212957.png
```

Modal AmiBroker bao:

```text
Can not open formula file:
'Formulas\Imported\'
```

Nhan dinh:

- COM khong chet.
- AmiBroker dang hien modal loi nen Python bi block.
- Loi la `FormulaPath`/APX import sai, chua phai loi `fopen`.

### 3. Instrument runner de biet ket o dau

Muc tieu: them log tung buoc va flush stdout de phan biet ket o `Dispatch`, `Open`, `Run`, hay `IsBusy`.

File sua:

```text
experiments/amibroker_retest_20260520/scripts/run_retest_scan.py
```

Thay doi chinh:

- Log `step=import_win32com`.
- Log `step=dispatch Broker.Application`.
- Log `step=open_analysis_doc`.
- Log `step=run`.
- Log `step=run_returned`.
- Poll `doc.IsBusy`.
- Them timeout va `doc.Abort` neu qua timeout.

Sau nay runner tiep tuc duoc sua them:

- `--action explore` dung `AnalysisDoc.Run(1)` cho Exploration.
- `--wait-file` de ket thuc khi AFL ghi `ready=1`.
- `--export` de goi `AnalysisDoc.Export()`.

### 4. Thu APX toi gian nhung `FormulaPath` rong

Muc tieu: tach loi `fopen`/FA khoi loi COM bang formula cuc don gian.

File tao:

```text
experiments/amibroker_retest_20260520/apx/simple_scan.apx
experiments/amibroker_retest_20260520/apx/simple_fopen.apx
```

Ket qua ban dau:

- Van bi AmiBroker modal `Can not open formula file: 'Formulas\Imported\'`.
- Nhan dinh: APX khong nen de `FormulaPath` rong theo cach nay.

Bang chung UI:

```text
C:\Users\Nguyen To Dung\Pictures\Screenshots\Screenshot 2026-05-20 212957.png
```

### 5. Thu dung AFL that trong `Formulas\CodexRetest`

Muc tieu: khong dung `FormulaContent` inline nua, ma tao AFL that de AmiBroker mo.

File tao trong repo:

```text
experiments/amibroker_retest_20260520/afl/simple_scan.afl
experiments/amibroker_retest_20260520/afl/simple_fopen.afl
```

Runtime copy sang AmiBroker:

```text
D:\MetakitData\AmibrokerFA\EOD\Formulas\CodexRetest\simple_scan.afl
D:\MetakitData\AmibrokerFA\EOD\Formulas\CodexRetest\simple_fopen.afl
```

Ket qua:

- `doc.Run()` da return, khong con modal formula path.
- Nhung `ApplyTo=All symbols` lam scan chay lau.
- Timeout 30 giay la binh thuong voi all-symbol.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/simple_scan_path_runner.stdout.log
```

Trich log:

```text
step=run_returned
elapsed=0.0s busy=True
...
elapsed=30.8s busy=True
TIMEOUT
```

Nhan dinh:

- Loi `FormulaPath` da duoc giai.
- Van can giam universe/range hoac co co che ket thuc som.

### 6. Thu `ApplyTo=current symbol`

Muc tieu: chay nhanh mot symbol thay vi all symbols.

Ket qua:

- Run ket thuc nhanh.
- Export chi co header, chua co row.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/simple_scan_results.csv
experiments/amibroker_retest_20260520/artifacts/simple_scan_runresult.csv
```

Noi dung dai dien:

```csv
Ticker,Date/Time
```

Nhan dinh:

- Current symbol/range/Formula import chua tao result row.
- Can tach tiep: formula co chay khong, cot co duoc import khong, filter co sinh row khong.

### 7. Thu inline `FormulaContent` va phat hien loi encode `&#13;&#10;`

Muc tieu: dung APX self-contained, de AmiBroker import formula tu `FormulaContent`.

File tao:

```text
experiments/amibroker_retest_20260520/apx/simple_scan_inline.apx
experiments/amibroker_retest_20260520/apx/simple_scan_inline_all_last.apx
```

Ket qua:

- Co luc export da hien cot `symbol,close`, chung to formula co duoc load toi muc nao do.
- Nhung runtime AFL trong `Formulas\Imported` co luc bi ghi literal `&#13;&#10;`.
- AmiBroker bao syntax Error 31.

Bang chung artifact:

```text
experiments/amibroker_retest_20260520/artifacts/simple_scan_inline.csv
experiments/amibroker_retest_20260520/artifacts/simple_scan_inline_all_last.csv
```

Bang chung UI:

```text
C:\Users\Nguyen To Dung\Pictures\Screenshots\Screenshot 2026-05-20 214440.png
C:\Users\Nguyen To Dung\Pictures\Screenshots\Screenshot 2026-05-20 214605.png
```

Loi quan sat:

```text
Error 31. Syntax error, unexpected $undefined, expecting IDENTIFIER
```

Nhan dinh:

- Khong dung `&#13;&#10;` trong `FormulaContent`.
- Dung multiline text that trong XML element.
- Tranh `_SECTION_BEGIN/_SECTION_END` trong APX generated test vi da gay parser noise trong qua trinh import.

### 8. Thu OLE cu `Broker.Application.Analysis`

Muc tieu: xem co the dung API cu thay `AnalysisDocs` hay khong.

File tao:

```text
experiments/amibroker_retest_20260520/scripts/run_old_analysis.py
```

Ket qua:

- `LoadFormula()` tra `True`.
- `Explore()` la synchronous va bi giu qua timeout.
- Khong tao CSV.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/old_analysis_simple_scan.stdout.log
experiments/amibroker_retest_20260520/artifacts/old_analysis_simple_scan_long.stdout.log
```

Trich log:

```text
LOAD_RESULT=True
settings=apply_to=1 range_mode=1 range_n=1
step=explore
```

Nhan dinh:

- API cu load formula duoc nhung khong reliable cho automation batch nay.
- Quay lai `AnalysisDocs` la hop ly hon.

### 9. Doi sang APX inline multiline that va force row

Muc tieu: xac nhan New Analysis + Export co the tao row neu AFL chac chan co `Filter=1`.

File:

```text
experiments/amibroker_retest_20260520/apx/force_rows_inline_current.apx
```

Ket qua: pass.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/force_rows_current.stdout.log
experiments/amibroker_retest_20260520/artifacts/force_rows_current.csv
```

CSV:

```csv
Ticker,Date/Time,symbol,dt,close,stocknum
VNINDEX,5/20/2026 00:00:00,VNINDEX,5/20/2026 00:00:00,1913.23,0
```

Nhan dinh:

- `AnalysisDoc.Run(1)` + `Export()` hoat dong.
- `ApplyTo=current symbol` tren UI luc do dang la `VNINDEX`, khong phai `VCB`.
- De lay ma cu the, can set current symbol trong AmiBroker hoac dung universe/filter rieng.

### 10. Thu `fopen` ban co `"\n"` va phat hien loi escape

Muc tieu: test rieng `fopen()`.

File:

```text
experiments/amibroker_retest_20260520/apx/simple_fopen_inline_current.apx
```

Ket qua:

- APX import `"\n"` thanh newline that ben trong string AFL.
- Runtime AFL bi hong string.
- CSV chi co header, khong co output file.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/simple_fopen_current.stdout.log
experiments/amibroker_retest_20260520/artifacts/simple_fopen_current.csv
```

Nhan dinh:

- Khong ket luan `fopen` fail o buoc nay duoc, vi AFL da bi import sai.
- Can viet output mot dong, khong dung `"\n"` trong `FormulaContent`.

### 11. Thu `fopen` mot dong, path forward-slash

Muc tieu: test dung rieng `fopen`, khong escape newline.

File:

```text
experiments/amibroker_retest_20260520/apx/simple_fopen_oneline_current.apx
```

Output runtime:

```text
C:\Users\Public\ag_simple_fopen_oneline_out.txt
```

Ket qua: pass.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/simple_fopen_oneline_current.stdout.log
experiments/amibroker_retest_20260520/artifacts/simple_fopen_oneline_current.csv
```

CSV:

```csv
Ticker,Date/Time,symbol,dt,close,fh_ok
VNINDEX,5/20/2026 00:00:00,VNINDEX,5/20/2026 00:00:00,1913.23,1
```

Output file:

```text
symbol=VNINDEX;close=1,913.2300;ready=1
```

Nhan dinh:

- `fopen()` khong bi khoa.
- `fh_ok=1` xac nhan handle mo thanh cong.
- File bridge bang AFL la huong kha thi.

### 12. Thu bridge FA lan dau va gap XML invalid

Muc tieu: dua `FA_MCDX`, `FA_RRG`, `Foreign("VNINDEX","C")`, `fopen` vao mot APX bridge that.

File:

```text
experiments/amibroker_retest_20260520/apx/fa_bridge_oneline_current.apx
```

Loi ban dau:

- APX co raw `<` trong `FormulaContent` o logic quadrant.
- XML text khong chap nhan raw `<`.
- `AnalysisDocs.Open()` bi ket / khong tao runtime AFL.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/fa_bridge_oneline_current.stdout.log
```

Nhan dinh:

- Khong dung raw `<` trong XML `FormulaContent`.
- Sua logic dung `NOT` thay vi `<`, hoac encode can than.

### 13. Sua bridge FA, file output duoc ghi nhung IsBusy con giu

Sua:

- Bo raw `<`.
- Ghep chuoi output qua bien `out`.
- Dung output mot dong.
- Dung path `C:/Users/Public/ag_fa_bridge_oneline_out.txt`.

Ket qua:

- File output bridge duoc ghi thanh cong.
- Nhung runner van cho `IsBusy=False` qua 90 giay nen timeout, khong export CSV luc do.

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/fa_bridge_oneline_current_v2.stdout.log
```

Output file da duoc ghi:

```text
C:\Users\Public\ag_fa_bridge_oneline_out.txt
```

Noi dung:

```text
symbol=VNINDEX;banker=11.240301;hotmoney=19.879290;rs_ratio=0.000000;rs_mom=0.000000;quadrant=3;tail_5d=0.000000;ready=1
```

Nhan dinh:

- FA functions da chay.
- `fopen` da chay.
- Khong nen cho duy nhat theo `IsBusy`; nen cho `ready=1` trong file.

### 14. Them `--wait-file` va chay bridge thanh cong cuoi

Sua runner:

```text
experiments/amibroker_retest_20260520/scripts/run_retest_scan.py
```

Them option:

```text
--wait-file "C:\Users\Public\ag_fa_bridge_oneline_out.txt"
```

Dieu kien pass:

- File ton tai.
- Noi dung co `ready=1`.

Lenh pass:

```powershell
python experiments\amibroker_retest_20260520\scripts\run_retest_scan.py `
  --apx "experiments\amibroker_retest_20260520\apx\fa_bridge_oneline_current.apx" `
  --action explore `
  --timeout 90 `
  --wait-file "C:\Users\Public\ag_fa_bridge_oneline_out.txt" `
  --export "experiments\amibroker_retest_20260520\artifacts\fa_bridge_waitfile_current.csv"
```

Bang chung:

```text
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.stdout.log
experiments/amibroker_retest_20260520/artifacts/fa_bridge_waitfile_current.csv
C:\Users\Public\ag_fa_bridge_oneline_out.txt
```

Stdout:

```text
step=import_win32com
step=dispatch Broker.Application
step=open_analysis_doc apx=...\fa_bridge_oneline_current.apx
step=run action=explore run_mode=1 apx=...\fa_bridge_oneline_current.apx
step=run_returned result=1
WAIT_FILE_READY path=C:\Users\Public\ag_fa_bridge_oneline_out.txt
step=export path=...\fa_bridge_waitfile_current.csv
EXPORT_RESULT=1
```

CSV:

```csv
Ticker,Date/Time,symbol,banker,hotmoney,rs_ratio,rs_mom,quadrant,tail_5d,fh_ok
VNINDEX,5/20/2026 00:00:00,VNINDEX,11.240301,19.879290,0.000000,0.000000,3,0.000000,1
```

## Nhung bai hoc ky thuat

1. `Broker.Application` COM dung duoc trong moi truong hien tai.
2. `AnalysisDocs.Open()` + `AnalysisDoc.Run(1)` la duong nen dung cho New Analysis/Exploration.
3. `Run(1)` la Exploration; runner cu dat ten `--mode scan` de gay nham, nen da them `--action explore`.
4. `fopen()` khong fail; test pass voi `fh_ok=1`.
5. APX generated can cuc ky can than voi XML:
   - Khong raw `<`.
   - Khong entity newline `&#13;&#10;` neu AmiBroker ghi lai literal vao AFL.
   - Khong `"\n"` trong string khi import qua APX nay.
6. Output file mot dong voi separator `;` la cach on dinh nhat.
7. File bridge nen co marker `ready=1`.
8. Python nen doc output file khi thay `ready=1`, thay vi doi AmiBroker `IsBusy=False`.
9. Neu can data cho symbol cu the, phai dam bao current symbol/universe dung. Lan pass hien tai chay tren `VNINDEX`, vi current symbol UI luc do la `VNINDEX`.
10. `rs_ratio=0` va `rs_mom=0` trong lan pass khong chung minh cong thuc RRG dung/sai cho toan bo universe; no chi chung minh ham `FA_RRG` chay va tra ve gia tri trong symbol hien tai. Can retest tiep tren cac symbol muc tieu nhu `VCB`, `HPG`, v.v.

## Trang thai file hien tai

Repo hien tai van thay ca thu muc la untracked:

```text
?? experiments/
```

Chua commit trong lan retest nay.

## Huong tiep theo de dua vao backend

De bien thanh flow production:

1. Tao APX template rieng cho one-symbol bridge.
2. Python truoc khi chay phai set/bao dam current symbol dung, hoac tao universe/filter rieng.
3. AFL ghi output mot dong co `ready=1`.
4. Python xoa output cu truoc khi chay.
5. Python chay `AnalysisDoc.Run(1)`.
6. Python poll file output toi khi thay `ready=1`.
7. Parse key-value `symbol=...;banker=...;...`.
8. Neu qua timeout, goi `doc.Abort` va tra loi co log.

