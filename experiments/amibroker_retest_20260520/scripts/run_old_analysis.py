#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def log(message: str) -> None:
    print(message, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formula", required=True, help="Absolute AFL formula path")
    parser.add_argument("--export", required=True, help="CSV export path")
    parser.add_argument("--apply-to", type=int, default=1, help="0=all, 1=current, 2=filter")
    parser.add_argument("--range-mode", type=int, default=1, help="0=all quotes, 1=N last quotes")
    parser.add_argument("--range-n", type=int, default=1)
    parser.add_argument("--action", choices=["explore", "scan"], default="explore")
    args = parser.parse_args()

    formula = Path(args.formula)
    if not formula.exists():
        log(f"ERROR: formula not found: {formula}")
        return 3

    export_path = Path(args.export)
    export_path.parent.mkdir(parents=True, exist_ok=True)

    log("step=import_win32com")
    import win32com.client  # type: ignore

    log("step=dispatch Broker.Application")
    ab = win32com.client.Dispatch("Broker.Application")
    analysis = ab.Analysis

    log(f"step=load_formula formula={formula}")
    load_result = analysis.LoadFormula(str(formula))
    log(f"LOAD_RESULT={load_result}")

    analysis.ApplyTo = args.apply_to
    analysis.RangeMode = args.range_mode
    analysis.RangeN = args.range_n
    log(
        "settings="
        f"apply_to={analysis.ApplyTo} range_mode={analysis.RangeMode} range_n={analysis.RangeN}"
    )

    if args.action == "explore":
        log("step=explore")
        run_result = analysis.Explore()
    else:
        log("step=scan")
        run_result = analysis.Scan()
    log(f"RUN_RESULT={run_result}")

    log(f"step=export path={export_path}")
    export_result = analysis.Export(str(export_path))
    log(f"EXPORT_RESULT={export_result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
