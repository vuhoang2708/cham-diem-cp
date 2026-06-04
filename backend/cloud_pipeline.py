"""
Cloud-native data pipeline using vnstock + pandas-ta.
Replaces AmiBroker COM dependency for production deployment.
"""
from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import pandas_ta as ta

logger = logging.getLogger(__name__)


def _get_vnstock():
    """Lazy import vnstock to allow running without it installed."""
    try:
        from vnstock import Vnstock
        return Vnstock
    except ImportError as e:
        raise ImportError("vnstock not installed. Run: pip install vnstock") from e


def fetch_ohlcv(symbol: str, days: int = 60) -> pd.DataFrame:
    """Fetch OHLCV data for a symbol from TCBS via vnstock."""
    Vnstock = _get_vnstock()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        stock = Vnstock().stock(symbol=symbol, source="TCBS")
        df = stock.quote.history(start=start_date, end=end_date, interval="1D")
        df = df.rename(columns={
            "time": "date", "open": "open", "high": "high",
            "low": "low", "close": "close", "volume": "volume"
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        logger.error("Failed to fetch OHLCV for %s: %s", symbol, e)
        return pd.DataFrame()


def fetch_vnindex_ohlcv(days: int = 60) -> pd.DataFrame:
    """Fetch VNINDEX benchmark data."""
    return fetch_ohlcv("VNINDEX", days=days)


def compute_adx_indicators(df: pd.DataFrame, period: int = 14) -> dict:
    """
    Compute ADX, DI+, DI- and look-back values needed for scoring.
    Returns dict with: adx, di_plus, di_minus, adx_1d, adx_3d
    """
    if len(df) < period + 5:
        return {"adx": 0, "di_plus": 0, "di_minus": 0, "adx_1d": 0, "adx_3d": 0}

    adx_df = ta.adx(df["high"], df["low"], df["close"], length=period)
    if adx_df is None or adx_df.empty:
        return {"adx": 0, "di_plus": 0, "di_minus": 0, "adx_1d": 0, "adx_3d": 0}

    adx_col = f"ADX_{period}"
    dmp_col = f"DMP_{period}"
    dmn_col = f"DMN_{period}"

    adx_series = adx_df[adx_col].dropna()
    dmp_series = adx_df[dmp_col].dropna()
    dmn_series = adx_df[dmn_col].dropna()

    if len(adx_series) < 4:
        return {"adx": 0, "di_plus": 0, "di_minus": 0, "adx_1d": 0, "adx_3d": 0}

    return {
        "adx": round(float(adx_series.iloc[-1]), 6),
        "di_plus": round(float(dmp_series.iloc[-1]), 6),
        "di_minus": round(float(dmn_series.iloc[-1]), 6),
        "adx_1d": round(float(adx_series.iloc[-2]), 6),
        "adx_3d": round(float(adx_series.iloc[-4]), 6),
    }


def compute_rrg_indicators(stock_df: pd.DataFrame, bench_df: pd.DataFrame, tail_days: int = 5) -> dict:
    """
    Compute RRG quadrant using RS-Ratio and RS-Momentum methodology.
    Comparable to FA_RRG from FireAnt AFL.
    Returns dict: quadrant (1–4), rs_ratio, rs_mom, tail_5d
    """
    if stock_df.empty or bench_df.empty or len(stock_df) < 20 or len(bench_df) < 20:
        return {"quadrant": 3, "rs_ratio": 0.0, "rs_mom": 0.0, "tail_5d": 0.0}

    # Align on date
    stock_close = stock_df.set_index("date")["close"]
    bench_close = bench_df.set_index("date")["close"]
    aligned = pd.concat([stock_close, bench_close], axis=1, join="inner")
    aligned.columns = ["stock", "bench"]
    aligned = aligned.dropna()

    if len(aligned) < 14:
        return {"quadrant": 3, "rs_ratio": 0.0, "rs_mom": 0.0, "tail_5d": 0.0}

    # Relative strength ratio (normalized to bench)
    rs = aligned["stock"] / aligned["bench"] * 100
    rs_sma = rs.rolling(10).mean()
    rs_ratio = (rs.iloc[-1] / rs_sma.iloc[-1] - 1) * 100 if rs_sma.iloc[-1] != 0 else 0.0

    # RS Momentum: rate of change of RS-Ratio
    rs_ratio_series = (rs / rs_sma - 1) * 100
    rs_mom = rs_ratio_series.diff(3).iloc[-1] if len(rs_ratio_series) >= 4 else 0.0

    # Quadrant mapping
    if rs_ratio >= 0 and rs_mom >= 0:
        quadrant = 1  # TĂNG GIÁ / Leading
    elif rs_ratio < 0 and rs_mom >= 0:
        quadrant = 4  # TÍCH LŨY / Improving
    elif rs_ratio >= 0 and rs_mom < 0:
        quadrant = 2  # SUY YẾU / Weakening
    else:
        quadrant = 3  # GIẢM GIÁ / Lagging

    # Tail direction over last 5 days
    tail_5d = round(rs_ratio_series.iloc[-1] - rs_ratio_series.iloc[-min(tail_days + 1, len(rs_ratio_series))], 4)

    return {
        "quadrant": quadrant,
        "rs_ratio": round(float(rs_ratio), 6),
        "rs_mom": round(float(rs_mom), 6),
        "tail_5d": round(float(tail_5d), 6),
    }


def compute_net_buying_proxy(df: pd.DataFrame, period: int = 50) -> dict:
    """
    Proxy for MCDX Banker indicator using net buying volume analysis.

    Note: True MCDX uses FireAnt proprietary data. This is a volume-based
    approximation: accumulation strength = (close-low)/(high-low) weighted volume.
    Returns dict: banker_value, banker_left, banker_right
    """
    if df.empty or len(df) < period:
        return {"banker_value": 0.0, "banker_left": 0.0, "banker_right": 0.0}

    df = df.tail(period).copy()
    hl_range = df["high"] - df["low"]
    # Avoid division by zero
    hl_range = hl_range.replace(0, 0.0001)
    # Williams %R style: (close - low) / (high - low) → buying pressure 0–1
    buying_pressure = (df["close"] - df["low"]) / hl_range
    weighted_vol = buying_pressure * df["volume"]

    # Net buying = weighted vol - (1-pressure)*vol
    net = weighted_vol - (1 - buying_pressure) * df["volume"]
    net_cumsum = net.cumsum()

    # Normalize to 0–20 range (matching original MCDX scale)
    rolling_max = abs(net_cumsum).rolling(period, min_periods=5).max()
    if rolling_max.iloc[-1] == 0:
        normalized = 0.0
    else:
        normalized = float((net_cumsum.iloc[-1] / rolling_max.iloc[-1]) * 20)
        normalized = max(0.0, min(20.0, normalized))

    # Banker left/right: 5-day split
    half = len(df) // 2
    left_net = float(net.iloc[:half].sum())
    right_net = float(net.iloc[half:].sum())
    total = abs(left_net) + abs(right_net) + 1e-9
    banker_left = round(abs(left_net) / total * 20, 4)
    banker_right = round(abs(right_net) / total * 20, 4)

    return {
        "banker_value": round(normalized, 4),
        "banker_left": banker_left,
        "banker_right": banker_right,
    }


def score_symbol_cloud(symbol: str, bench_df: Optional[pd.DataFrame] = None) -> Optional[dict]:
    """
    Full cloud scoring pipeline for one symbol.
    Returns raw data dict ready for scoring.py / database.py
    """
    df = fetch_ohlcv(symbol, days=90)
    if df.empty:
        logger.warning("No OHLCV data for %s", symbol)
        return None

    if bench_df is None:
        bench_df = fetch_vnindex_ohlcv(days=90)

    adx_data = compute_adx_indicators(df)
    rrg_data = compute_rrg_indicators(df, bench_df)
    banker_data = compute_net_buying_proxy(df)

    return {
        "symbol": symbol,
        **banker_data,
        **rrg_data,
        **adx_data,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = score_symbol_cloud("VCB")
    if result:
        print(result)
    else:
        print("Failed to score VCB")
