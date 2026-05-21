from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import win32com.client  # type: ignore
except ImportError:  # pragma: no cover - Windows runtime dependency
    win32com = None

from database import export_to_json, init_db, save_score
from scoring import build_base_score_from_raw, quadrant_name

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


REPO_ROOT = Path(__file__).resolve().parents[1]
VN30_SYMBOLS_PATH = REPO_ROOT / "data" / "vn30_symbols.json"

AMI_FORMULAS_DIR = Path(r"D:\MetakitData\AmibrokerFA\EOD\Formulas")
FORMULA_REL_PATH = r"Imported\ag_vn30_bridge.afl"
FORMULA_RUNTIME_PATH = AMI_FORMULAS_DIR / "Imported" / "ag_vn30_bridge.afl"

APX_PATH = Path(r"C:\Users\Public\ag_vn30_bridge.apx")
OUTPUT_DIR = Path(r"C:\Users\Public\ag_vn30_bridge")
OUTPUT_PREFIX = "ami_vn30_"


def log(message: str) -> None:
    print(message, flush=True)


def read_symbols() -> list[str]:
    return json.loads(VN30_SYMBOLS_PATH.read_text(encoding="utf-8"))


def format_afl(symbols: list[str]) -> str:
    symbol_filter = " OR ".join(f'Name() == "{symbol}"' for symbol in symbols)
    output_dir = OUTPUT_DIR.as_posix()
    return f"""\
is_target = {symbol_filter};

mcdx_Banker = FA_MCDX(50, 1.5, 50, 20);
mcdx_HotMoney = FA_MCDX(40, 0.7, 30, 20);

bc = Foreign("VNINDEX", "C");
rs_ratio = FA_RRG(C, bc, 1);
rs_mom = FA_RRG(C, bc, 0);

bk = LastValue(mcdx_Banker);
hm = LastValue(mcdx_HotMoney);
rsr = LastValue(rs_ratio);
rsm = LastValue(rs_mom);

rsr_hi = rsr >= 0;
rsm_hi = rsm >= 0;
quad = IIf(rsr_hi AND rsm_hi, 1, IIf(rsr_hi AND NOT rsm_hi, 2, IIf(NOT rsr_hi AND NOT rsm_hi, 3, 4)));

dx = rs_ratio - Ref(rs_ratio, -1);
dy = rs_mom - Ref(rs_mom, -1);
tail5d = LastValue(Sum(sqrt(dx * dx + dy * dy), 5));

fh_ok = 0;

if (is_target)
{{
    outfile = "{output_dir}/{OUTPUT_PREFIX}" + Name() + ".txt";
    fh = fopen(outfile, "w");
    if (fh)
    {{
        fh_ok = 1;
        out = "symbol=" + Name();
        out = out + ";banker=" + NumToStr(bk, 1.6);
        out = out + ";hotmoney=" + NumToStr(hm, 1.6);
        out = out + ";rs_ratio=" + NumToStr(rsr, 1.6);
        out = out + ";rs_mom=" + NumToStr(rsm, 1.6);
        out = out + ";quadrant=" + NumToStr(quad, 1.0);
        out = out + ";tail_5d=" + NumToStr(tail5d, 1.6);
        out = out + ";ready=1";
        fputs(out, fh);
        fclose(fh);
    }}
}}

Filter = is_target;
AddTextColumn(Name(), "symbol", 1.0);
AddColumn(bk, "banker", 1.6);
AddColumn(hm, "hotmoney", 1.6);
AddColumn(rsr, "rs_ratio", 1.6);
AddColumn(rsm, "rs_mom", 1.6);
AddColumn(quad, "quadrant", 1.0);
AddColumn(tail5d, "tail_5d", 1.6);
AddColumn(fh_ok, "fh_ok", 1.0);
"""


def format_apx(symbols: list[str], formula_content: str) -> str:
    return f"""\
<?xml version="1.0" encoding="ISO-8859-1"?>
<AmiBroker-Analysis CompactMode="0">
<General>
<FormatVersion>1</FormatVersion>
<Symbol>{symbols[0]}</Symbol>
<FormulaPath>{FORMULA_REL_PATH}</FormulaPath>
<FormulaContent>{formula_content}</FormulaContent>
<ApplyTo>0</ApplyTo>
<RangeType>1</RangeType>
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
<RangeType>1</RangeType>
<RangeLength>1</RangeLength>
<RangeFromDate>2020-01-01 00:00:00</RangeFromDate>
<RangeToDate>2026-12-31</RangeToDate>
<ApplyTo>0</ApplyTo>
</BacktestSettings>
</AmiBroker-Analysis>"""


def write_runtime_files(symbols: list[str]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FORMULA_RUNTIME_PATH.parent.mkdir(parents=True, exist_ok=True)

    for stale in OUTPUT_DIR.glob(f"{OUTPUT_PREFIX}*.txt"):
        stale.unlink()

    formula = format_afl(symbols)
    FORMULA_RUNTIME_PATH.write_text(formula, encoding="utf-8")
    APX_PATH.write_text(format_apx(symbols, formula), encoding="iso-8859-1")
    log(f"Wrote AFL: {FORMULA_RUNTIME_PATH}")
    log(f"Wrote APX: {APX_PATH}")


def parse_pairs(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in text.strip().split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    normalized = value.replace(",", "")
    try:
        parsed = float(normalized)
    except ValueError:
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def parse_int(value: str | None, default: int = 3) -> int:
    return int(round(parse_float(value, float(default))))


def output_path(symbol: str) -> Path:
    return OUTPUT_DIR / f"{OUTPUT_PREFIX}{symbol}.txt"


def ready_symbols(symbols: list[str]) -> set[str]:
    ready: set[str] = set()
    for symbol in symbols:
        path = output_path(symbol)
        if path.exists() and "ready=1" in path.read_text(encoding="utf-8", errors="replace"):
            ready.add(symbol)
    return ready


def run_amibroker(symbols: list[str], timeout: int) -> None:
    if win32com is None:
        raise RuntimeError("pywin32 is not installed; cannot automate AmiBroker")

    ab = win32com.client.Dispatch("Broker.Application")
    log(f"Connected AmiBroker v{ab.Version}")
    doc = ab.AnalysisDocs.Open(str(APX_PATH))
    run_result = doc.Run(1)
    log(f"AnalysisDoc.Run(1) result={run_result}")

    started = time.time()
    while True:
        ready = ready_symbols(symbols)
        elapsed = time.time() - started
        log(f"elapsed={elapsed:.1f}s ready={len(ready)}/{len(symbols)} busy={bool(doc.IsBusy)}")

        if len(ready) == len(symbols):
            if bool(doc.IsBusy):
                try:
                    log(f"Abort after all files ready: {doc.Abort}")
                except Exception as exc:  # noqa: BLE001
                    log(f"Abort failed: {type(exc).__name__}: {exc}")
            return

        if elapsed > timeout:
            try:
                log(f"Abort after timeout: {doc.Abort}")
            except Exception as exc:  # noqa: BLE001
                log(f"Abort failed: {type(exc).__name__}: {exc}")
            missing = sorted(set(symbols) - ready)
            raise TimeoutError(f"Timed out waiting for {len(missing)} symbols: {', '.join(missing)}")

        time.sleep(1)


def load_result(symbol: str) -> dict | None:
    path = output_path(symbol)
    if not path.exists():
        return None
    raw = parse_pairs(path.read_text(encoding="utf-8", errors="replace"))
    if raw.get("ready") != "1":
        return None

    banker = parse_float(raw.get("banker"))
    hotmoney = parse_float(raw.get("hotmoney"))
    rs_ratio = parse_float(raw.get("rs_ratio"))
    rs_mom = parse_float(raw.get("rs_mom"))
    tail_5d = parse_float(raw.get("tail_5d"))
    quadrant_num = parse_int(raw.get("quadrant"))

    score_payload = build_base_score_from_raw(banker, quadrant_num)
    return {
        "symbol": symbol,
        **score_payload,
        "banker_value": banker,
        "banker_left": banker,
        "banker_right": hotmoney,
        "quadrant": quadrant_name(quadrant_num),
        "rs_ratio": round(rs_ratio, 2),
        "rs_mom": round(rs_mom, 2),
        "tail_5d": round(tail_5d, 2),
    }


def save_dashboard(symbols: list[str]) -> int:
    init_db()
    saved = 0
    for symbol in symbols:
        data = load_result(symbol)
        if not data:
            log(f"Missing or invalid output for {symbol}")
            continue
        save_score(data, category="vn30")
        saved += 1
        log(
            f"{symbol}: total={data['total_score']:.2f} "
            f"banker={data['banker_value']:.4f} rrg={data['quadrant']}"
        )

    export_to_json(category="vn30")
    return saved


def run_vn30_scoring(timeout: int = 240, skip_run: bool = False) -> int:
    symbols = read_symbols()
    log(f"VN30 symbols: {len(symbols)}")

    if not skip_run:
        write_runtime_files(symbols)
        run_amibroker(symbols, timeout)

    saved = save_dashboard(symbols)
    log(f"Saved/exported {saved}/{len(symbols)} VN30 rows at {datetime.now():%Y-%m-%d %H:%M:%S}")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--skip-run", action="store_true", help="Only parse existing output files.")
    args = parser.parse_args()

    saved = run_vn30_scoring(timeout=args.timeout, skip_run=args.skip_run)
    return 0 if saved == len(read_symbols()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
