"""
Antigravity AmiBroker Connector - Test Script
=============================================
Purpose: Connect to a running AmiBroker instance via OLE COM,
         run the ami_bridge.afl formula for a given symbol,
         and read back the calculated values (MCDX Banker + RRG).

Pre-requisites:
    1. AmiBroker must be OPEN and running.
    2. Install: pip install pywin32
    3. The ami_bridge.afl file must be copied to AmiBroker's Formulas folder.
       Copy it from: backend/ami_bridge.afl
       Paste to:     C:\\Program Files (x86)\\AmiBroker\\Formulas\\Custom\\

Usage:
    python backend/test_ami_connector.py
"""

import sys
import os

# ---- Check pywin32 availability ----
try:
    import win32com.client
    import pywintypes
except ImportError:
    print("=" * 60)
    print("ERROR: pywin32 is not installed.")
    print("Please run: pip install pywin32")
    print("=" * 60)
    sys.exit(1)

# ---- Configuration ----
TEST_SYMBOL   = "VCB"          # Symbol to test
BRIDGE_AFL    = "Custom\\ami_bridge.afl"   # Relative path inside AmiBroker Formulas folder
OUTPUT_FILE   = r"C:\Windows\Temp\ag_bridge_out.txt"
TIMEOUT_SECS  = 30             # Max seconds to wait for result


def connect_amibroker():
    """Connect to the running AmiBroker instance via COM."""
    try:
        ab = win32com.client.Dispatch("Broker.Application")
        print(f"[OK] Connected to AmiBroker: version {ab.Version}")
        return ab
    except pywintypes.com_error as e:
        print("[FAIL] Cannot connect to AmiBroker.")
        print("       Make sure AmiBroker is OPEN before running this script.")
        print(f"       Error: {e}")
        return None


def get_stock_data(ab, symbol):
    """
    Tell AmiBroker to run the bridge AFL for the given symbol,
    then read back the results from the output file.
    """
    import time

    # 1. Get the Analysis object
    analysis = ab.AnalysisDocs.Open(BRIDGE_AFL)
    if analysis is None:
        print(f"[FAIL] Could not open '{BRIDGE_AFL}'. Check Formulas/Custom/ folder.")
        return None
    print(f"[DEBUG] Analysis opened OK")

    # 2. Delete old output file
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"[DEBUG] Deleted old output file")

    # 3. Set the filter to the specific symbol only
    analysis.SetFilterSymbol(symbol)
    print(f"[DEBUG] SetFilterSymbol({symbol}) called")

    # 4. Run Scan
    analysis.Run(0)
    print(f"[DEBUG] Run(0) called — waiting for output file ...")

    # 5. Wait for output file to appear
    start = time.time()
    while not os.path.exists(OUTPUT_FILE):
        elapsed = time.time() - start
        if elapsed > TIMEOUT_SECS:
            print(f"[WARN] Timeout after {TIMEOUT_SECS}s. Output file not created.")
            print(f"       Check AmiBroker: Analysis > Scan should have run for {symbol}")
            return None
        if int(elapsed) % 3 == 0 and elapsed > 0:
            print(f"[DEBUG] Waiting... {elapsed:.0f}s")
        time.sleep(0.5)

    time.sleep(0.2)  # ensure file fully written
    elapsed = time.time() - start
    print(f"[DEBUG] Output file found after {elapsed:.1f}s")

    # 6. Parse output file
    data = {"symbol": symbol}
    with open(OUTPUT_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()

    results = {
        "symbol":   symbol,
        "banker":   float(data.get("banker",   0)),
        "hotmoney": float(data.get("hotmoney", 0)),
        "rs_ratio": float(data.get("rs_ratio", 100)),
        "rs_mom":   float(data.get("rs_mom",   100)),
        "quadrant": int(float(data.get("quadrant", 3))),
        "tail_5d":  float(data.get("tail_5d",  0)),
    }

    return results


def quadrant_name(q):
    return {1: "LEADING (Tăng giá)", 2: "WEAKENING (Suy yếu)",
            3: "LAGGING (Giảm giá)", 4: "IMPROVING (Tích lũy)"}.get(q, "Unknown")


def score_banker(banker_value):
    """Nội suy tuyến tính theo thang điểm đã chốt."""
    breakpoints = [(0, 0.0), (3, 0.2), (8, 0.4), (12, 0.6), (16, 0.8), (20, 1.0)]
    if banker_value >= 20:
        return 1.0
    if banker_value <= 0:
        return 0.0
    for i in range(len(breakpoints) - 1):
        x0, y0 = breakpoints[i]
        x1, y1 = breakpoints[i + 1]
        if x0 <= banker_value <= x1:
            ratio = (banker_value - x0) / (x1 - x0)
            return round(y0 + ratio * (y1 - y0), 4)
    return 0.0


def score_rrg(quadrant):
    return {1: 1.0, 4: 0.75, 2: 0.5, 3: 0.25}.get(quadrant, 0.0)


def main():
    print("=" * 60)
    print("  ANTIGRAVITY — AmiBroker Connection Test")
    print("=" * 60)

    # 1. Connect to AmiBroker
    ab = connect_amibroker()
    if ab is None:
        sys.exit(1)

    # 2. Fetch data for test symbol
    print(f"\n[INFO] Fetching data for symbol: {TEST_SYMBOL} ...")
    data = get_stock_data(ab, TEST_SYMBOL)

    # 3. Calculate scores
    mcdx_score = score_banker(data["banker"])
    rrg_score  = score_rrg(data["quadrant"])
    total_score = round(mcdx_score + rrg_score, 4)

    # 4. Print results
    print("\n" + "=" * 60)
    print(f"  Kết quả cho mã: {data['symbol']}")
    print("=" * 60)
    print(f"  MCDX Banker Value : {data['banker']:.4f}")
    print(f"  MCDX HotMoney     : {data['hotmoney']:.4f}")
    print(f"  MCDX Score        : {mcdx_score} / 1.0")
    print("-" * 60)
    print(f"  RRG RS-Ratio (X)  : {data['rs_ratio']:.4f}")
    print(f"  RRG RS-Mom   (Y)  : {data['rs_mom']:.4f}")
    print(f"  RRG Quadrant      : {quadrant_name(data['quadrant'])}")
    print(f"  RRG Score         : {rrg_score} / 1.0")
    print(f"  RRG Tail 5D       : {data['tail_5d']:.4f} (tham khảo)")
    print("-" * 60)
    print(f"  TỔNG ĐIỂM         : {total_score} / 2.0")
    print("=" * 60)
    print("\n[SUCCESS] AmiBroker connection test passed!")


if __name__ == "__main__":
    main()
