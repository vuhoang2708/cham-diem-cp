# AmiBroker Runtime Retest Results - 2026-05-20

## Environment

- AmiBroker COM dispatch: OK
- AmiBroker version: 6.30.0
- Python: 64-bit Python 3.12 with pywin32
- AmiBroker executable observed: `D:\MetakitData\AmibrokerFA\EOD\Broker.exe`

## Key findings

1. `Broker.Application` COM works from Python 64-bit on this machine.
2. `AnalysisDocs.Open()` and `AnalysisDoc.Run(1)` work when the APX is valid.
3. `fopen()` is not blocked. It successfully wrote:
   `C:\Users\Public\ag_simple_fopen_oneline_out.txt`
4. FA functions also execute inside AmiBroker via COM:
   `FA_MCDX`, `FA_RRG`, `Foreign`, `LastValue`, `AddColumn`, and `fopen` all ran in the bridge formula.
5. The reliable bridge pattern is:
   - Use `AnalysisDoc.Run(1)` for Exploration.
   - Write output from AFL to a one-line file.
   - Python watches for `ready=1` instead of waiting only for `IsBusy=False`.
   - Optionally call `Export()` after `ready=1` to capture the result list CSV.

## Confirmed artifacts

- `artifacts/com_probe_64bit.json`
- `artifacts/force_rows_current.csv`
- `artifacts/simple_fopen_oneline_current.csv`
- `artifacts/fa_bridge_waitfile_current.csv`
- Runtime output:
  `C:\Users\Public\ag_fa_bridge_oneline_out.txt`

Last successful bridge output:

```text
symbol=VNINDEX;banker=11.240301;hotmoney=19.879290;rs_ratio=0.000000;rs_mom=0.000000;quadrant=3;tail_5d=0.000000;ready=1
```

CSV export from the same run:

```csv
Ticker,Date/Time,symbol,banker,hotmoney,rs_ratio,rs_mom,quadrant,tail_5d,fh_ok
VNINDEX,5/20/2026 00:00:00,VNINDEX,11.240301,19.879290,0.000000,0.000000,3,0.000000,1
```

## Traps found during retest

- Empty or directory-only `FormulaPath` causes AmiBroker modal errors and blocks COM.
- APX `FormulaContent` should use real multiline text, not `&#13;&#10;`; AmiBroker may write those numeric entities literally into the imported AFL.
- Avoid `_SECTION_BEGIN/_SECTION_END` in these generated APX tests; a previous imported file produced parser noise around the leading `_`.
- Do not put raw `<` inside XML `FormulaContent`. Rewrite logic to avoid `<`, or encode carefully.
- Do not use `"\n"` in APX `FormulaContent` for this import path. AmiBroker imported it as a real newline inside the string. Use one-line output or another separator.
- Use forward-slash paths in generated AFL, for example `C:/Users/Public/out.txt`.

## Current best command

```powershell
python experiments\amibroker_retest_20260520\scripts\run_retest_scan.py `
  --apx "experiments\amibroker_retest_20260520\apx\fa_bridge_oneline_current.apx" `
  --action explore `
  --timeout 90 `
  --wait-file "C:\Users\Public\ag_fa_bridge_oneline_out.txt" `
  --export "experiments\amibroker_retest_20260520\artifacts\fa_bridge_waitfile_current.csv"
```

