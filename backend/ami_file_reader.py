"""
Read AmiBroker export files from C:\\Users\\Public\\ami_<SYMBOL>.txt
Written by vn100_export.afl running on AmiBroker watchlist.
"""
import os
import glob
import json
from datetime import datetime

EXPORT_DIR = r"C:\Users\Public"
FILE_PREFIX = "ami_"
MAX_AGE_MINUTES = 30  # reject stale data older than this


def _parse_file(path: str) -> dict | None:
    data = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip()
    except Exception:
        return None
    if "symbol" not in data:
        return None
    return data


def get_symbol_data(symbol: str) -> dict | None:
    path = os.path.join(EXPORT_DIR, f"{FILE_PREFIX}{symbol}.txt")
    if not os.path.exists(path):
        return None
    # Check file age
    age_seconds = (datetime.now().timestamp() - os.path.getmtime(path))
    if age_seconds > MAX_AGE_MINUTES * 60:
        return None
    return _parse_file(path)


def get_all_data() -> dict[str, dict]:
    """Return dict of symbol -> data for all exported files."""
    result = {}
    pattern = os.path.join(EXPORT_DIR, f"{FILE_PREFIX}*.txt")
    for path in glob.glob(pattern):
        data = _parse_file(path)
        if data and "symbol" in data:
            result[data["symbol"]] = data
    return result


def get_banker_value(symbol: str) -> float:
    data = get_symbol_data(symbol)
    if not data:
        return 0.0
    try:
        return float(data.get("banker", 0))
    except ValueError:
        return 0.0


def get_rrg_data(symbol: str) -> dict:
    data = get_symbol_data(symbol)
    if not data:
        return {"rs_ratio": 100.0, "rs_mom": 100.0, "quadrant": 1, "tail_5d": 0.0}
    try:
        return {
            "rs_ratio": float(data.get("rs_ratio", 100)),
            "rs_mom":   float(data.get("rs_mom",   100)),
            "quadrant": int(float(data.get("quadrant", 1))),
            "tail_5d":  float(data.get("tail_5d",  0)),
        }
    except ValueError:
        return {"rs_ratio": 100.0, "rs_mom": 100.0, "quadrant": 1, "tail_5d": 0.0}


if __name__ == "__main__":
    print("All exported symbols:")
    all_data = get_all_data()
    for sym, d in sorted(all_data.items()):
        print(f"  {sym}: banker={d.get('banker')} rs_ratio={d.get('rs_ratio')} quad={d.get('quadrant')}")
    print(f"\nTotal: {len(all_data)} symbols")
