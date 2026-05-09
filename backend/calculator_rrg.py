import pandas as pd
import numpy as np

def calculate_wma(series, period):
    weights = np.arange(1, period + 1)
    return series.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def calculate_rrg(df_stock, df_index, period=14, tail_period=5):
    """
    Calculate RRG metrics: RS_Ratio, RS_Mom, Quadrant, and Tail Length.
    """
    try:
        # Merge on time to ensure alignment
        df_stock = df_stock[['time', 'close']].rename(columns={'close': 'close_stock'})
        df_index = df_index[['time', 'close']].rename(columns={'close': 'close_index'})
        
        df = pd.merge(df_stock, df_index, on='time')
        df = df.sort_values('time')
        
        # 1. Relative Strength (RS)
        df['rs'] = df['close_stock'] / df['close_index']
        
        # 2. RS-Ratio (X-axis)
        df['wma_rs'] = calculate_wma(df['rs'], period)
        df['rs_ratio'] = 100 * (df['rs'] / df['wma_rs'])
        
        # 3. RS-Momentum (Y-axis)
        df['wma_rs_ratio'] = calculate_wma(df['rs_ratio'], period)
        df['rs_mom'] = 100 * (df['rs_ratio'] / df['wma_rs_ratio'])
        
        # 4. Tail Length (Euclidean distance)
        df['dist_1d'] = np.sqrt((df['rs_ratio'] - df['rs_ratio'].shift(1))**2 + 
                                (df['rs_mom'] - df['rs_mom'].shift(1))**2)
        df['tail_length'] = df['dist_1d'].rolling(window=tail_period).sum()
        
        # Get latest values
        latest = df.iloc[-1]
        
        rs_ratio = latest['rs_ratio']
        rs_mom = latest['rs_mom']
        
        # Determine Quadrant
        if rs_ratio >= 100 and rs_mom >= 100:
            quadrant = "TĂNG GIÁ" # Leading
            score = 1.0
        elif rs_ratio >= 100 and rs_mom < 100:
            quadrant = "SUY YẾU" # Weakening
            score = 0.5
        elif rs_ratio < 100 and rs_mom < 100:
            quadrant = "GIẢM GIÁ" # Lagging
            score = 0.25
        else: # rs_ratio < 100 and rs_mom >= 100
            quadrant = "TÍCH LŨY" # Improving
            score = 0.75
            
        return {
            'rs_ratio': round(rs_ratio, 2),
            'rs_mom': round(rs_mom, 2),
            'quadrant': quadrant,
            'rrg_score': score,
            'tail_5d': round(latest['tail_length'], 2)
        }
    except Exception as e:
        print(f"Error calculating RRG: {e}")
        return None

if __name__ == "__main__":
    from data_source import get_stock_data
    vcb = get_stock_data("VCB")
    index = get_stock_data("VNINDEX", type='index')
    if vcb is not None and index is not None:
        result = calculate_rrg(vcb, index)
        print("RRG Result for VCB:")
        print(result)
