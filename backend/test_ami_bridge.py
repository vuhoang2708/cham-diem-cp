"""
Quick test: chạy AmiConnector.get_data("VCB") và in kết quả.
Chạy từ project root:
    python backend/test_ami_bridge.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scraper_amibroker import AmiConnector

def main():
    conn = AmiConnector()
    if not conn.connect():
        print("FAIL: cannot connect to AmiBroker")
        return 1

    for symbol in ["VCB", "ACB", "HPG"]:
        print(f"\n--- {symbol} ---")
        result = conn.get_data(symbol)
        if result:
            for k, v in result.items():
                print(f"  {k}: {v}")
        else:
            print("  FAIL: no result")

    conn.disconnect()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
