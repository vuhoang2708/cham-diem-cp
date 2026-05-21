import asyncio
import json
import os
from data_source import get_stock_data
from calculator_rrg import calculate_rrg
from database import init_db, save_score
from scoring import build_score_payload

USE_AMIBROKER = os.environ.get("DATA_SOURCE", "fireant").lower() == "amibroker"

async def run_scoring(category='vn30', symbols=None):
    print(f"Starting {category.upper()} Scoring Process...")
    init_db()

    if USE_AMIBROKER and category == 'vn30' and symbols is None:
        from run_amibroker_vn30 import run_vn30_scoring
        timeout = int(os.environ.get("AMIBROKER_TIMEOUT", "360"))
        saved = run_vn30_scoring(timeout=timeout)
        print(f"\nVN30 AmiBroker bridge finished. Successfully processed {saved}/30 stocks.")
        return
    
    # Load symbols dựa trên category nếu không được truyền vào
    if symbols is None:
        if category == 'vn30':
            symbols_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vn30_symbols.json')
        elif category == 'vn100':
            symbols_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vn100_symbols.json')
        else: # custom
            symbols_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'custom_symbols.json')
            
        if os.path.exists(symbols_path):
            with open(symbols_path, 'r') as f:
                symbols = json.load(f)
        else:
            print(f"Error: Symbols file not found at {symbols_path}")
            return

    # Get Benchmark data (VNINDEX) — only needed for Fireant/TCBS RRG mode
    df_index = None
    if not USE_AMIBROKER:
        print("Fetching VNINDEX data for RRG...")
        df_index = get_stock_data("VNINDEX", type='index')
        if df_index is None:
            print("Critical Error: Could not fetch VNINDEX data.")
            return

    # Setup data source
    if USE_AMIBROKER:
        from scraper_amibroker import AmiConnector
        connector = AmiConnector()
        if not connector.connect():
            print("Critical Error: Cannot connect to AmiBroker. Is it open?")
            return
    else:
        from scraper_mcdx import MCDXScraper
        scraper = MCDXScraper()
        connected = await scraper.connect()
        if not connected:
            print("Critical Error: Could not connect to Chrome CDP.")
            return

    results_count = 0
    total_symbols = len(symbols)

    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{total_symbols}] Processing {symbol} in {category}...")
        
        # 1. RRG Calculation (RS Ratio, RS Momentum, Score) — only for Fireant mode
        rrg_res = None
        if not USE_AMIBROKER:
            df_stock = get_stock_data(symbol)
            if df_stock is not None:
                rrg_res = calculate_rrg(df_stock, df_index)
            
        # 2. Lấy dữ liệu MCDX + RRG
        if USE_AMIBROKER:
            ami_res = connector.get_data(symbol)
            if ami_res:
                mcdx_res = ami_res
                rrg_res = {
                    "rrg_score": ami_res["rrg_score"],
                    "quadrant":  ami_res["quadrant"],
                    "rs_ratio":  ami_res["rs_ratio"],
                    "rs_mom":    ami_res["rs_mom"],
                    "tail_5d":   ami_res["tail_5d"],
                }
            else:
                mcdx_res = None
        else:
            mcdx_res = await scraper.get_banker_value(symbol)
        
        if rrg_res and mcdx_res:
            # 3. Combine score components
            extra_components = {}
            extra_component_maxes = {}
            if USE_AMIBROKER and ami_res and "adx_score" in ami_res:
                extra_components["adx"] = ami_res["adx_score"]
                extra_component_maxes["adx"] = 0.5

            score_payload = build_score_payload(
                mcdx_score=mcdx_res['mcdx_score'],
                rrg_score=rrg_res['rrg_score'],
                extra_components=extra_components,
                extra_component_maxes=extra_component_maxes,
            )
            
            data = {
                'symbol': symbol,
                **score_payload,
                'banker_value': mcdx_res['banker_value'],
                'banker_left': mcdx_res.get('banker_left', 0),
                'banker_right': mcdx_res.get('banker_right', 0),
                'quadrant': rrg_res['quadrant'],
                'rs_ratio': rrg_res['rs_ratio'],
                'rs_mom': rrg_res['rs_mom'],
                'tail_5d': rrg_res['tail_5d'],
                'adx_score': ami_res.get('adx_score', 0) if USE_AMIBROKER and ami_res else 0,
                'adx_value': ami_res.get('adx_value', 0) if USE_AMIBROKER and ami_res else 0,
                'di_plus': ami_res.get('di_plus', 0) if USE_AMIBROKER and ami_res else 0,
                'di_minus': ami_res.get('di_minus', 0) if USE_AMIBROKER and ami_res else 0,
                'adx_1d': ami_res.get('adx_1d', 0) if USE_AMIBROKER and ami_res else 0,
                'adx_3d': ami_res.get('adx_3d', 0) if USE_AMIBROKER and ami_res else 0,
            }
            
            # 4. Save to Database với category
            save_score(data, category=category)
            results_count += 1
            print(f"   Success: Total Score = {data['total_score']}")
        else:
            print(f"   Failed to process {symbol}")
            
        await asyncio.sleep(1)

    # Cleanup
    if USE_AMIBROKER:
        connector.disconnect()
    else:
        await scraper.disconnect()
    print(f"\n{category.upper()} process finished. Successfully processed {results_count}/{total_symbols} stocks.")
    
    # 5. Export to JSON for Vercel (theo category)
    from database import export_to_json
    export_to_json(category=category)
    
    # 6. Push to GitHub (nếu cần đồng bộ web)
    print("Pushing updated data to GitHub...")
    import subprocess
    try:
        filename = f"data_{category}.json"
        subprocess.run(["git", "add", f"frontend/{filename}"], check=True)
        subprocess.run(["git", "commit", "-m", f"data: update {category} scores"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("GitHub push successful.")
    except Exception as e:
        print(f"GitHub push skipped or failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_scoring())
