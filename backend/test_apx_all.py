"""Test AnalysisDocs.Open + Run with ApplyTo=0 (all symbols) to confirm formula executes."""
import win32com.client, time, os, sys, html

sys.stdout.reconfigure(line_buffering=True)

OUTPUT_FILE = r"C:\Users\Public\ag_bridge_out.txt"

FORMULA = (
    r'mcdx_Banker   = FA_MCDX(50, 1.5, 50, 20);\r\n'
    r'mcdx_HotMoney = FA_MCDX(40, 0.7, 30, 20);\r\n'
    r'bc       = Foreign("VNINDEX", "C");\r\n'
    r'rs_ratio = FA_RRG(C, bc, 1);\r\n'
    r'rs_mom   = FA_RRG(C, bc, 0);\r\n'
    r'bk   = LastValue(mcdx_Banker);\r\n'
    r'hm   = LastValue(mcdx_HotMoney);\r\n'
    r'rsr  = LastValue(rs_ratio);\r\n'
    r'rsm  = LastValue(rs_mom);\r\n'
    r'quad = IIf(rsr>=100 AND rsm>=100,1,IIf(rsr>=100 AND rsm<100,2,IIf(rsr<100 AND rsm<100,3,4)));\r\n'
    r'dx = rs_ratio - Ref(rs_ratio,-1);\r\n'
    r'dy = rs_mom   - Ref(rs_mom,-1);\r\n'
    r'tail5d = LastValue(Sum(sqrt(dx*dx+dy*dy),5));\r\n'
    r'fh = fopen("C:\\Users\\Public\\ag_bridge_out.txt","w");\r\n'
    r'if(fh){\r\n'
    r'fputs("symbol="+Name()+"\n",fh);\r\n'
    r'fputs("banker="+NumToStr(bk,1.6)+"\n",fh);\r\n'
    r'fputs("hotmoney="+NumToStr(hm,1.6)+"\n",fh);\r\n'
    r'fputs("rs_ratio="+NumToStr(rsr,1.6)+"\n",fh);\r\n'
    r'fputs("rs_mom="+NumToStr(rsm,1.6)+"\n",fh);\r\n'
    r'fputs("quadrant="+NumToStr(quad,1.0)+"\n",fh);\r\n'
    r'fputs("tail_5d="+NumToStr(tail5d,1.6)+"\n",fh);\r\n'
    r'fputs("ready=1\n",fh);\r\n'
    r'fclose(fh);\r\n'
    r'}\r\n'
    r'Filter=1;\r\n'
)

APX_TEMPLATE = '''<?xml version="1.0" encoding="ISO-8859-1"?>
<AmiBroker-Analysis CompactMode="0">
<General>
<FormatVersion>1</FormatVersion>
<Symbol>VCB</Symbol>
<FormulaPath></FormulaPath>
<FormulaContent>{formula}</FormulaContent>
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

APX_PATH = r"C:\Users\Public\ag_bridge_all.apx"

# Write the .apx
escaped = html.escape(FORMULA, quote=False)
content = APX_TEMPLATE.format(formula=escaped)
with open(APX_PATH, "w", encoding="iso-8859-1") as f:
    f.write(content)
print(f"Created: {APX_PATH}")

# Clear old output
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

# Connect and run
ab = win32com.client.Dispatch("Broker.Application")
print("Version:", ab.Version)

doc = ab.AnalysisDocs.Open(APX_PATH)
print("Opened OK")

print("Running Scan (ApplyTo=0, all symbols)...")
doc.Run(1)

for i in range(60):
    time.sleep(1)
    busy = doc.IsBusy
    print(f"  [{i+1}s] IsBusy={busy}")
    if not busy:
        break
    # Check if output appeared early
    if os.path.exists(OUTPUT_FILE):
        print("  Output file appeared!")
        break

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE) as f:
        print("OUTPUT:")
        print(f.read())
else:
    print("No output file written")
