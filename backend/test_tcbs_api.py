import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from vnstock import *
import pandas as pd
import numpy as np

def calculate_wma(series, period):
    weights = np.arange(1, period + 1)
    return series.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def test_rrg(ticker="VCB", period=14, tail_period=5):
    print(f"Testing RRG calculation for {ticker} using vnstock 0.2.8.3...")
    
    # Get historical data for the ticker and VNINDEX (benchmark)
    df_stock = stock_historical_data(symbol=ticker, start_date='2025-01-01', end_date='2026-05-09', resolution='1D', type='stock')
    df_vnindex = stock_historical_data(symbol='VNINDEX', start_date='2025-01-01', end_date='2026-05-09', resolution='1D', type='index')
    
    # Merge on date
    df_stock['time'] = pd.to_datetime(df_stock['time']).dt.tz_localize(None)
    df_vnindex['time'] = pd.to_datetime(df_vnindex['time']).dt.tz_localize(None)
    
    df = pd.merge(df_stock[['time', 'close']], df_vnindex[['time', 'close']], on='time', suffixes=('_stock', '_index'))
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    
    # 2. TÍNH TỌA ĐỘ RRG
    # Tính Relative Strength (RS)
    df['rs'] = df['close_stock'] / df['close_index']
    
    # Tính JdK RS-Ratio (Trục X)
    df['wma_rs'] = calculate_wma(df['rs'], period)
    df['RS_Ratio'] = 100 * (df['rs'] / df['wma_rs'])
    
    # Tính JdK RS-Momentum (Trục Y)
    df['wma_RS_Ratio'] = calculate_wma(df['RS_Ratio'], period)
    df['RS_Mom'] = 100 * (df['RS_Ratio'] / df['wma_RS_Ratio'])
    
    # 3. TÍNH ĐỘ DÀI ĐUÔI THEO KHOẢNG CÁCH EUCLID
    df['Tail_1D'] = np.sqrt( (df['RS_Ratio'] - df['RS_Ratio'].shift(1))**2 + (df['RS_Mom'] - df['RS_Mom'].shift(1))**2 )
    df['Tail_ND'] = df['Tail_1D'].rolling(window=tail_period).sum()
    
    # Lấy ngày mới nhất
    latest = df.iloc[-1]
    
    rs_ratio = latest['RS_Ratio']
    rs_mom = latest['RS_Mom']
    
    quadrant = "UNKNOWN"
    if rs_ratio > 100 and rs_mom > 100: quadrant = "LEADING (TĂNG GIÁ)"
    elif rs_ratio > 100 and rs_mom < 100: quadrant = "WEAKENING (SUY YẾU)"
    elif rs_ratio < 100 and rs_mom < 100: quadrant = "LAGGING (GIẢM GIÁ)"
    elif rs_ratio < 100 and rs_mom > 100: quadrant = "IMPROVING (TÍCH LŨY)"
    
    print("\nKết quả mới nhất:")
    print(f"RS-Ratio (X): {rs_ratio:.2f}")
    print(f"RS-Mom (Y):   {rs_mom:.2f}")
    print(f"Góc phần tư:  {quadrant}")
    print(f"Độ dài đuôi (Tail_{tail_period}D): {latest['Tail_ND']:.2f}")

if __name__ == "__main__":
    test_rrg("VCB")
