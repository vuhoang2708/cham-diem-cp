"""
AmiBroker Scraper — đọc dữ liệu giá trực tiếp từ AmiBroker Stocks API,
tính MCDX Banker và RRG hoàn toàn trong Python (không cần AFL/AnalysisDocs).
"""
import time
import math

try:
    import win32com.client
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

BENCHMARK = "VNINDEX"
RRG_PERIOD = 10       # smoothing period for RS-Ratio / RS-Momentum
MIN_BARS   = 120      # minimum bars needed for calculation


class AmiConnector:
    """Kết nối AmiBroker COM và lấy dữ liệu cho từng mã CP."""

    def __init__(self):
        self.ab     = None
        self.stocks = None
        self.bench_close = None  # cached VNINDEX close prices

    def connect(self) -> bool:
        if not HAS_PYWIN32:
            print("[AmiConnector] ERROR: pywin32 not installed.")
            return False
        try:
            self.ab = win32com.client.Dispatch("Broker.Application")
            print(f"[AmiConnector] Connected to AmiBroker v{self.ab.Version}")
            self.stocks = self.ab.Stocks
            print(f"[AmiConnector] Stocks loaded: {self.stocks.Count} symbols")
            # Pre-load benchmark
            self.bench_close = _get_close(self.stocks, BENCHMARK)
            if self.bench_close is None or len(self.bench_close) < MIN_BARS:
                print(f"[AmiConnector] WARN: Cannot load {BENCHMARK} data")
                return False
            print(f"[AmiConnector] {BENCHMARK} loaded: {len(self.bench_close)} bars")
            return True
        except Exception as e:
            print(f"[AmiConnector] Cannot connect: {e}")
            return False

    def disconnect(self):
        self.ab     = None
        self.stocks = None
        self.bench_close = None

    def get_data(self, symbol: str) -> dict | None:
        if not self.ab:
            return None
        try:
            close = _get_close(self.stocks, symbol)
            if close is None or len(close) < MIN_BARS:
                print(f"[AmiConnector] Not enough data for {symbol}")
                return None

            # Align lengths
            n = min(len(close), len(self.bench_close))
            c  = close[-n:]
            bc = self.bench_close[-n:]

            banker   = _calc_mcdx_banker(c)
            hotmoney = _calc_mcdx_hotmoney(c)
            rs_ratio, rs_mom = _calc_rrg(c, bc)
            quadrant = _rrg_quadrant(rs_ratio, rs_mom)
            tail_5d  = _rrg_tail(rs_ratio, rs_mom)

            return {
                "symbol":   symbol,
                "banker":   banker,
                "hotmoney": hotmoney,
                "rs_ratio": rs_ratio,
                "rs_mom":   rs_mom,
                "quadrant": quadrant,
                "tail_5d":  tail_5d,
                "mcdx_score":   _score_banker(banker),
                "rrg_score":    _score_rrg(quadrant),
                "banker_left":  banker,
                "banker_right": hotmoney,
                "banker_value": banker,
            }
        except Exception as e:
            print(f"[AmiConnector] Error for {symbol}: {e}")
            return None


# ── Data loading ──────────────────────────────────────────────────────────────

def _get_close(stocks, symbol: str):
    """Read all Close prices for a symbol from AmiBroker."""
    try:
        stock = stocks(symbol)
        if stock is None:
            return None
        q = stock.Quotations
        n = q.Count
        if n == 0:
            return None
        closes = [q(i).Close for i in range(n)]
        return closes
    except Exception:
        return None


# ── MCDX Banker calculation (mirrors FA_MCDX parameters) ─────────────────────

def _ema(data, period):
    k = 2.0 / (period + 1)
    result = [data[0]]
    for v in data[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result

def _rsi(data, period):
    gains, losses = [], []
    for i in range(1, len(data)):
        d = data[i] - data[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    if len(gains) < period:
        return [50.0] * len(data)
    avg_g = sum(gains[:period]) / period
    avg_l = sum(losses[:period]) / period
    rsi_vals = [50.0] * (period + 1)
    for i in range(period, len(gains)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
        rs = avg_g / avg_l if avg_l != 0 else 100
        rsi_vals.append(100 - 100 / (1 + rs))
    return rsi_vals

def _calc_mcdx_banker(close):
    """MCDX Banker: RSI(50) based, sensitivity 1.5, base 50, retailer 20."""
    period, sensitivity, base, retailer = 50, 1.5, 50, 20
    rsi_vals = _rsi(close, period)
    # Scale RSI deviation into 0-20 range
    last_rsi = rsi_vals[-1]
    raw = (last_rsi - base) * sensitivity
    # Clamp to 0-20
    return round(max(0.0, min(20.0, raw)), 4)

def _calc_mcdx_hotmoney(close):
    """MCDX HotMoney: RSI(40) based, sensitivity 0.7, base 30, retailer 20."""
    period, sensitivity, base, retailer = 40, 0.7, 30, 20
    rsi_vals = _rsi(close, period)
    last_rsi = rsi_vals[-1]
    raw = (last_rsi - base) * sensitivity
    return round(max(0.0, min(20.0, raw)), 4)


# ── RRG calculation ───────────────────────────────────────────────────────────

def _calc_rrg(close, bench_close, period=RRG_PERIOD):
    """Calculate RS-Ratio and RS-Momentum (last bar values)."""
    n = min(len(close), len(bench_close))
    c  = close[-n:]
    bc = bench_close[-n:]

    # Relative strength
    rs = [c[i] / bc[i] * 100 if bc[i] != 0 else 100 for i in range(n)]

    # RS-Ratio = EMA of RS normalized around 100
    rs_ema = _ema(rs, period)
    # Normalize: ratio of current RS to its own EMA
    rs_ratio_series = [rs[i] / rs_ema[i] * 100 if rs_ema[i] != 0 else 100
                       for i in range(n)]

    # RS-Momentum = EMA of RS-Ratio normalized
    rs_ratio_ema = _ema(rs_ratio_series, period)
    rs_mom_series = [rs_ratio_series[i] / rs_ratio_ema[i] * 100
                     if rs_ratio_ema[i] != 0 else 100
                     for i in range(n)]

    return round(rs_ratio_series[-1], 4), round(rs_mom_series[-1], 4)

def _rrg_quadrant(rs_ratio, rs_mom):
    if rs_ratio >= 100 and rs_mom >= 100: return 1  # Leading
    if rs_ratio >= 100 and rs_mom <  100: return 2  # Weakening
    if rs_ratio <  100 and rs_mom <  100: return 3  # Lagging
    return 4                                         # Improving

def _rrg_tail(rs_ratio_series, rs_mom_series, bars=5):
    """Euclidean tail length over last N bars — simplified single-point version."""
    return 0.0  # placeholder; full series needed for proper tail calc


# ── Scoring ───────────────────────────────────────────────────────────────────

def _score_banker(value: float) -> float:
    breakpoints = [(0, 0.0), (3, 0.2), (8, 0.4), (12, 0.6), (16, 0.8), (20, 1.0)]
    if value <= 0:  return 0.0
    if value >= 20: return 1.0
    for i in range(len(breakpoints) - 1):
        x0, y0 = breakpoints[i]
        x1, y1 = breakpoints[i + 1]
        if x0 <= value <= x1:
            return round(y0 + (y1 - y0) * (value - x0) / (x1 - x0), 4)
    return 0.0

def _score_rrg(quadrant: int) -> float:
    return {1: 1.0, 4: 0.75, 2: 0.5, 3: 0.25}.get(quadrant, 0.0)
