"""
Setup Option D: Tạo watchlist VN100 trong AmiBroker qua COM,
rồi chạy scan với vn100_export.afl để test fopen hoạt động không.
"""
import win32com.client, time, os, sys, json, glob

sys.stdout.reconfigure(line_buffering=True)

VN100 = [
    "ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG",
    "MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB",
    "TCB","TPB","VCB","VHM","VIB","VIC","VJC","VNM","VPB","VRE",
    "AAA","AGG","ANV","ASM","BCG","BMP","BSI","BWE","CII","CMG",
    "CRE","CSV","DBC","DCM","DGC","DGW","DIG","DPM","DXG","EIB",
    "EVF","FRT","FTS","GEX","GEG","GMD","HCM","HDC","HDG","HHV",
    "HHS","HT1","IDI","KBC","KDC","KDH","LPB","NKG","NLG","NT2",
    "OCB","PAN","PC1","PDR","PHR","PNJ","PTB","PVT","REE","SAM",
    "SBT","SCR","SJS","SZL","TDM","TIP","TLG","TMS","TNG","TV2",
    "VCI","VGC","VHC","VND","VPI","VSC","VSH","CTS","VIX",
]

EXPORT_DIR = r"C:\Users\Public"
APX_PATH   = os.path.join(EXPORT_DIR, "vn100_export.apx")
AFL_PATH   = r"Custom\vn100_export.afl"

# --- Tạo .apx với ApplyTo=3 (Watchlist index 0) ---
APX = '''<?xml version="1.0" encoding="ISO-8859-1"?>
<AmiBroker-Analysis CompactMode="0">
<General>
<FormatVersion>1</FormatVersion>
<Symbol>VCB</Symbol>
<FormulaPath>Custom\\vn100_export.afl</FormulaPath>
<FormulaContent></FormulaContent>
<ApplyTo>3</ApplyTo>
<WatchListIndex>0</WatchListIndex>
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
<Type4>4</Type4><Category4>10</Category4>
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
<ApplyTo>3</ApplyTo>
</BacktestSettings>
</AmiBroker-Analysis>'''

with open(APX_PATH, "w", encoding="iso-8859-1") as f:
    f.write(APX)
print(f"Created: {APX_PATH}")

# --- Kết nối AmiBroker ---
print("Connecting to AmiBroker...")
ab = win32com.client.Dispatch("Broker.Application")
print(f"Version: {ab.Version}")

# --- Thêm symbols vào Watchlist 0 (type=4 = Watchlist) ---
print(f"Adding {len(VN100)} symbols to Watchlist #0...")
added = 0
for sym in VN100:
    try:
        ab.CategoryAddSymbol(4, 0, sym)
        added += 1
    except Exception as e:
        print(f"  CategoryAddSymbol({sym}): {e}")
        break

if added == 0:
    print("CategoryAddSymbol not available — trying alternative...")
    # Fallback: dùng ApplyTo=0 (all symbols) nhưng filter trong AFL
    APX_ALL = APX.replace("<ApplyTo>3</ApplyTo>", "<ApplyTo>0</ApplyTo>")
    APX_ALL = APX_ALL.replace("<WatchListIndex>0</WatchListIndex>", "")
    with open(APX_PATH, "w", encoding="iso-8859-1") as f:
        f.write(APX_ALL)
    print("Switched to ApplyTo=0 (all symbols)")
else:
    print(f"Added {added} symbols to Watchlist #0")

# --- Xóa output cũ ---
for f in glob.glob(os.path.join(EXPORT_DIR, "ami_*.txt")):
    os.remove(f)
print("Cleared old output files")

# --- Chạy scan ---
print(f"Opening {APX_PATH}...")
doc = ab.AnalysisDocs.Open(APX_PATH)
print("Running scan...")
doc.Run(1)

for i in range(300):
    time.sleep(1)
    busy = doc.IsBusy
    if i % 15 == 0:
        files = glob.glob(os.path.join(EXPORT_DIR, "ami_*.txt"))
        print(f"  [{i+1}s] IsBusy={busy} | output files: {len(files)}")
    if not busy:
        print(f"  Done at {i+1}s")
        break

# --- Đọc kết quả ---
files = glob.glob(os.path.join(EXPORT_DIR, "ami_*.txt"))
print(f"\nOutput files found: {len(files)}")
for f in sorted(files)[:5]:
    print(f"\n--- {os.path.basename(f)} ---")
    print(open(f).read().strip())
