r"""
AmiBroker scraper — lấy FA_MCDX và FA_RRG qua COM automation.

Flow cho mỗi symbol:
1. Ghi AFL vào Formulas\CodexBridge\ag_bridge.afl
2. Tạo APX với Symbol=<symbol>, FormulaPath trỏ đến AFL trên
3. Xóa output file cũ
4. ab.Stocks(symbol) để set current symbol (nếu có)
5. doc = ab.AnalysisDocs.Open(apx)
6. doc.Run(1)  — Exploration mode
7. Poll output file cho đến khi có ready=1
8. Parse key=value;key=value
9. doc.Close()

Lessons from Codex retest 2026-05-20:
- fopen() works via COM — previous failures were APX encoding bugs
- FormulaContent must be real multiline text (no \\r\\n, no &#13;&#10;)
- No raw < in FormulaContent — use NOT logic
- Poll output file for ready=1, not IsBusy
- 64-bit Python works fine
"""
from __future__ import annotations

import time
from pathlib import Path

try:
    import win32com.client
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

try:
    from backend.create_apx import create_apx, OUTPUT_FILE
    from backend.scoring import score_banker, score_rrg
except ImportError:  # Allows running from the backend directory.
    from create_apx import create_apx, OUTPUT_FILE
    from scoring import score_banker, score_rrg

APX_PATH = r"C:\Users\Public\ag_bridge.apx"
POLL_INTERVAL = 0.5   # seconds between output-file polls
TIMEOUT = 60          # seconds before giving up on a single symbol


def _parse_output(text: str) -> dict:
    """Parse 'key=val;key=val;...' into dict."""
    result = {}
    for part in text.strip().split(";"):
        if "=" in part:
            k, _, v = part.partition("=")
            result[k.strip()] = v.strip()
    return result


class AmiConnector:
    def __init__(self):
        self.ab = None

    def connect(self) -> bool:
        if not HAS_PYWIN32:
            print("[AmiConnector] ERROR: pywin32 not installed.")
            return False
        try:
            self.ab = win32com.client.Dispatch("Broker.Application")
            print(f"[AmiConnector] Connected to AmiBroker v{self.ab.Version}")
            return True
        except Exception as e:
            print(f"[AmiConnector] Cannot connect: {e}")
            return False

    def disconnect(self):
        self.ab = None

    def get_data(self, symbol: str) -> dict | None:
        if not self.ab:
            return None

        out_path = Path(OUTPUT_FILE.replace("/", "\\"))

        # Delete stale output file
        try:
            out_path.unlink(missing_ok=True)
        except Exception:
            pass

        # Generate APX for this symbol
        try:
            create_apx(symbol, apx_path=APX_PATH, output_file=OUTPUT_FILE)
        except Exception as e:
            print(f"[AmiConnector] APX creation failed for {symbol}: {e}")
            return None

        doc = None
        try:
            doc = self.ab.AnalysisDocs.Open(APX_PATH)
            doc.Run(1)  # 1 = Exploration

            # Poll output file for ready=1
            start = time.time()
            while True:
                if out_path.exists():
                    try:
                        text = out_path.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        text = ""
                    if "ready=1" in text:
                        parsed = _parse_output(text)
                        return _build_result(parsed)

                if time.time() - start > TIMEOUT:
                    print(f"[AmiConnector] TIMEOUT for {symbol}")
                    try:
                        doc.Abort
                    except Exception:
                        pass
                    return None

                time.sleep(POLL_INTERVAL)

        except Exception as e:
            print(f"[AmiConnector] Error for {symbol}: {e}")
            return None
        finally:
            if doc is not None:
                try:
                    doc.Close()
                except Exception:
                    pass


def _build_result(parsed: dict) -> dict:
    def f(key: str, default: float = 0.0) -> float:
        try:
            return float(parsed.get(key, default))
        except ValueError:
            return default

    banker   = f("banker")
    hotmoney = f("hotmoney")
    rs_ratio = f("rs_ratio")
    rs_mom   = f("rs_mom")
    quadrant = int(f("quadrant", 3))
    tail_5d  = f("tail_5d")

    return {
        "symbol":       parsed.get("symbol", ""),
        "banker":       banker,
        "hotmoney":     hotmoney,
        "rs_ratio":     rs_ratio,
        "rs_mom":       rs_mom,
        "quadrant":     quadrant,
        "tail_5d":      tail_5d,
        "mcdx_score":   score_banker(banker),
        "rrg_score":    score_rrg(quadrant),
        "banker_left":  banker,
        "banker_right": hotmoney,
        "banker_value": banker,
    }
