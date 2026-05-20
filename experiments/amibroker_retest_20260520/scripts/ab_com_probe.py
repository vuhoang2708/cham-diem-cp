#!/usr/bin/env python3
"""Probe AmiBroker COM surface and persist structured output.

Run on Windows 32-bit Python with pywin32.
"""
from __future__ import annotations

import argparse
import json
import platform
from datetime import datetime, UTC
from pathlib import Path


def safe_getattr(obj, name: str):
    try:
        value = getattr(obj, name)
        return {"ok": True, "type": type(value).__name__, "repr": repr(value)[:200]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/com_probe.json")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "python_bitness": platform.architecture()[0],
        "probe": {},
    }

    try:
        import win32com.client  # type: ignore
    except Exception as exc:  # noqa: BLE001
        result["fatal_error"] = f"Cannot import win32com.client: {exc}"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 2

    try:
        ab = win32com.client.Dispatch("Broker.Application")
    except Exception as exc:  # noqa: BLE001
        result["fatal_error"] = f"Cannot dispatch Broker.Application: {exc}"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 3

    probe_names = [
        "Version",
        "AnalysisDocs",
        "Stocks",
        "Documents",
        "ActiveWindow",
        "ActiveDocument",
        "LoadDatabase",
        "SaveDatabase",
        "RefreshAll",
        "Import",
        "Log",
        "Quit",
        "CategoryAddSymbol",
        "CategoryGetSymbols",
        "SendCommand",
        "ExecuteFormula",
    ]

    for name in probe_names:
        result["probe"][name] = safe_getattr(ab, name)

    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote probe to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
