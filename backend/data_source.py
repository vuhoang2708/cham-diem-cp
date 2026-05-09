import pandas as pd
from vnstock import stock_historical_data
from datetime import datetime, timedelta

def get_stock_data(symbol, days=100, type='stock'):
    """
    Fetch historical price data for a symbol.
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    try:
        # resolution='1D' for daily data
        df = stock_historical_data(symbol=symbol, 
                                   start_date=start_date, 
                                   end_date=end_date, 
                                   resolution='1D', 
                                   type=type)
        if df is None or df.empty:
            print(f"Warning: No data for {symbol}")
            return None
            
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

if __name__ == "__main__":
    # Test
    vcb_data = get_stock_data("VCB")
    if vcb_data is not None:
        print("VCB Data Head:")
        print(vcb_data.head())
        
    vnindex_data = get_stock_data("VNINDEX", type='index')
    if vnindex_data is not None:
        print("\nVNINDEX Data Head:")
        print(vnindex_data.head())
