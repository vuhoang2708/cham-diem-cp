#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path


def log(message: str) -> None:
    print(message, flush=True)


def export_results(doc, export_path: str | None) -> int:
    if not export_path:
        return 0

    path = Path(export_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    log(f"step=export path={path}")
    try:
        result = doc.Export(str(path))
    except Exception as exc:  # noqa: BLE001
        log(f"EXPORT_FAILED={type(exc).__name__}: {exc}")
        return 5

    log(f"EXPORT_RESULT={result}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apx", required=True, help="Absolute path to .apx file")
    parser.add_argument(
        "--action",
        choices=["scan", "explore", "backtest", "optimize", "walkforward"],
        default=None,
        help="AmiBroker AnalysisDoc.Run action. Use explore for AddColumn result lists.",
    )
    parser.add_argument(
        "--mode",
        choices=["scan", "backtest"],
        default=None,
        help="Legacy alias: scan means explore in this retest runner.",
    )
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument(
        "--idle-grace",
        type=int,
        default=5,
        help="Seconds to wait before accepting an immediate non-busy state as done.",
    )
    parser.add_argument("--export", help="Optional CSV export path after run completes.")
    parser.add_argument(
        "--wait-file",
        help="Optional output file to watch. If it exists and contains ready=1, return success.",
    )
    args = parser.parse_args()

    try:
        log("step=import_win32com")
        import win32com.client  # type: ignore
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR: cannot import win32com.client: {exc}")
        return 2

    apx = Path(args.apx)
    if not apx.exists():
        log(f"ERROR: APX not found: {apx}")
        return 3

    log("step=dispatch Broker.Application")
    ab = win32com.client.Dispatch("Broker.Application")

    log(f"step=open_analysis_doc apx={apx}")
    doc = ab.AnalysisDocs.Open(str(apx))

    if args.action:
        action = args.action
    elif args.mode == "backtest":
        action = "backtest"
    else:
        action = "explore"

    run_modes = {
        "scan": 0,
        "explore": 1,
        "backtest": 2,
        "optimize": 3,
        "walkforward": 4,
    }
    run_mode = run_modes[action]
    log(f"step=run action={action} run_mode={run_mode} apx={apx}")
    run_result = doc.Run(run_mode)
    log(f"step=run_returned result={run_result}")

    start = time.time()
    seen_busy = False
    while True:
        if args.wait_file:
            wait_path = Path(args.wait_file)
            if wait_path.exists():
                try:
                    wait_text = wait_path.read_text(encoding="utf-8", errors="replace")
                except Exception as exc:  # noqa: BLE001
                    log(f"WAIT_FILE_READ_FAILED={type(exc).__name__}: {exc}")
                    wait_text = ""
                if "ready=1" in wait_text:
                    log(f"WAIT_FILE_READY path={wait_path}")
                    return export_results(doc, args.export)

        log("step=read_is_busy")
        busy = bool(doc.IsBusy)
        elapsed = time.time() - start
        log(f"elapsed={elapsed:.1f}s busy={busy}")
        if busy:
            seen_busy = True
        if not busy and seen_busy:
            break
        if not busy and not seen_busy and elapsed >= args.idle_grace:
            log("DONE_NO_BUSY_SEEN")
            return export_results(doc, args.export)
        if elapsed > args.timeout:
            log("TIMEOUT")
            try:
                abort_result = doc.Abort
                log(f"ABORT_RESULT={abort_result}")
            except Exception as exc:  # noqa: BLE001
                log(f"ABORT_FAILED={type(exc).__name__}: {exc}")
            return 4
        time.sleep(1)

    log("DONE")
    return export_results(doc, args.export)


if __name__ == "__main__":
    raise SystemExit(main())
