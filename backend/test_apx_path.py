"""Test AnalysisDocs.Open with FormulaPath pointing to real .afl file."""
import win32com.client, time, os, sys, html

sys.stdout.reconfigure(line_buffering=True)

OUTPUT_FILE = r"C:\Users\Public\ag_bridge_out.txt"
APX_PATH = r"C:\Users\Public\ag_bridge_path.apx"

APX = '''<?xml version="1.0" encoding="ISO-8859-1"?>
<AmiBroker-Analysis CompactMode="0">
<General>
<FormatVersion>1</FormatVersion>
<Symbol>VCB</Symbol>
<FormulaPath>Custom\\ami_bridge.afl</FormulaPath>
<FormulaContent></FormulaContent>
<ApplyTo>0</ApplyTo>
<RangeType>0</RangeType>
<RangeAmount>1</RangeAmount>
<FromDate>2020-01-01 00:00:00</FromDate>
<ToDate>2026-12-31</ToDate>
<SyncOnSelect>0</SyncOnSelect>
<RunEvery>0</RunEvery>
<RunEveryInterval>5min</RunEveryInterval>
<IncludeFilter>
<ExcludeMode>0</ExcludeMode>
<OrSelection>0</OrSelection>
<Favourite>0</Favourite>
<Index>0</Index>
<Type0>0</Type0><Category0>-1</Category0>
<Type1>1</Type1><Category1>-1</Category1>
<Type2>2</Type2><Category2>-1</Category2>
<Type3>3</Type3><Category3>-1</Category3>
<Type4>4</Type4><Category4>-1</Category4>
<Type5>5</Type5><Category5>-1</Category5>
<Type6>6</Type6><Category6>-1</Category6>
</IncludeFilter>
<ExcludeFilter>
<ExcludeMode>1</ExcludeMode>
<OrSelection>0</OrSelection>
<Favourite>0</Favourite>
<Index>0</Index>
<Type0>0</Type0><Category0>-1</Category0>
<Type1>1</Type1><Category1>-1</Category1>
<Type2>2</Type2><Category2>-1</Category2>
<Type3>3</Type3><Category3>-1</Category3>
<Type4>4</Type4><Category4>-1</Category4>
<Type5>5</Type5><Category5>-1</Category5>
<Type6>6</Type6><Category6>-1</Category6>
</ExcludeFilter>
</General>
<BacktestSettings>
<InitialEquity>10000</InitialEquity>
<TradeFlags>1</TradeFlags>
<RangeType>0</RangeType>
<RangeLength>0</RangeLength>
<RangeFromDate>2020-01-01 00:00:00</RangeFromDate>
<RangeToDate>2026-12-31</RangeToDate>
<ApplyTo>0</ApplyTo>
</BacktestSettings>
</AmiBroker-Analysis>'''

# Write the .apx
with open(APX_PATH, "w", encoding="iso-8859-1") as f:
    f.write(APX)
print(f"Created: {APX_PATH}")

# Clear old output
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

# Connect and run
ab = win32com.client.Dispatch("Broker.Application")
print("Version:", ab.Version)

doc = ab.AnalysisDocs.Open(APX_PATH)
print("Opened OK")

print("Running Scan (FormulaPath=Custom\\ami_bridge.afl, ApplyTo=0)...")
doc.Run(1)

for i in range(60):
    time.sleep(1)
    busy = doc.IsBusy
    print(f"  [{i+1}s] IsBusy={busy}")
    if not busy:
        break
    if os.path.exists(OUTPUT_FILE):
        print("  Output file appeared!")
        break

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE) as f:
        print("OUTPUT:")
        print(f.read())
else:
    print("No output file written")
