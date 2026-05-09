import asyncio
import json
import os
from data_source import get_stock_data
from calculator_rrg import calculate_rrg
from scraper_mcdx import MCDXScraper
from database import init_db, save_score

async def run_scoring():
    print("Starting VN100 Scoring Process...")
    init_db()
    
    # Load symbols
    symbols_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vn100_symbols.json')
    with open(symbols_path, 'r') as f:
        symbols = json.load(f)
    
    # Get Benchmark data (VNINDEX)
    print("Fetching VNINDEX data...")
    df_index = get_stock_data("VNINDEX", type='index')
    if df_index is None:
        print("Critical Error: Could not fetch VNINDEX data.")
        return

    # Setup Scraper
    scraper = MCDXScraper()
    connected = await scraper.connect()
    if not connected:
        print("Critical Error: Could not connect to Chrome CDP. Please run start_chrome.bat first.")
        return

    results_count = 0
    total_symbols = len(symbols)

    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{total_symbols}] Processing {symbol}...")
        
        # 1. RRG Calculation
        df_stock = get_stock_data(symbol)
        rrg_res = None
        if df_stock is not None:
            rrg_res = calculate_rrg(df_stock, df_index)
            
        # 2. MCDX Scraping
        mcdx_res = await scraper.get_banker_value(symbol)
        
        if rrg_res and mcdx_res:
            # 3. Combine and Score
            total_score = round(rrg_res['rrg_score'] + mcdx_res['mcdx_score'], 2)
            
            data = {
                'symbol': symbol,
                'total_score': total_score,
                'mcdx_score': mcdx_res['mcdx_score'],
                'banker_value': mcdx_res['banker_value'],
                'quadrant': rrg_res['quadrant'],
                'rs_ratio': rrg_res['rs_ratio'],
                'rs_mom': rrg_res['rs_mom'],
                'tail_5d': rrg_res['tail_5d']
            }
            
            # 4. Save to Database
            save_score(data)
            results_count += 1
            print(f"   Success: Total Score = {total_score}")
        else:
            print(f"   Failed to process {symbol}")
            
        # Optional: small delay to not overwhelm Fireant
        await asyncio.sleep(1)

    await scraper.disconnect()
    print(f"\nScoring process finished. Successfully processed {results_count}/{total_symbols} stocks.")
    
    # 5. Export to JSON for Vercel
    from database import export_to_json
    export_to_json()
    
    # 6. Push to GitHub
    print("Pushing updated data to GitHub...")
    import subprocess
    try:
        subprocess.run(["git", "add", "frontend/data.json"], check=True)
        subprocess.run(["git", "commit", "-m", "data: update scores after scoring run"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("GitHub push successful. Vercel will update shortly.")
    except Exception as e:
        print(f"Failed to push to GitHub: {e}")

if __name__ == "__main__":
    asyncio.run(run_scoring())
