from fastapi import FastAPI, BackgroundTasks, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from database import get_latest_scores
import main_scorer
import asyncio
import os
import json
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Stock Scorer API Multi-Tab")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global status tracking per category
status = {
    "vn30": {"is_running": False, "progress": 0, "current_symbol": ""},
    "vn100": {"is_running": False, "progress": 0, "current_symbol": ""},
    "custom": {"is_running": False, "progress": 0, "current_symbol": ""}
}

@app.get("/api/scores")
async def read_scores(category: str = "vn30"):
    """Returns the latest scores for a specific category."""
    return get_latest_scores(category)

@app.get("/api/status")
async def get_status(category: str = "vn30"):
    """Returns the current status for a specific category."""
    return status.get(category, {"is_running": False})

async def run_refresh_task(category: str):
    global status
    status[category]["is_running"] = True
    try:
        await main_scorer.run_scoring(category=category)
    except Exception as e:
        print(f"Error in refresh task for {category}: {e}")
    finally:
        status[category]["is_running"] = False

@app.post("/api/refresh")
async def refresh_scores(background_tasks: BackgroundTasks, category: str = Query("vn30")):
    """Triggers a background refresh for a specific category."""
    print(f"Received refresh request for {category}")
    if category not in status:
        return {"error": "Invalid category"}
    
    if status[category]["is_running"]:
        return {"message": f"Scoring for {category} is already in progress"}
    
    background_tasks.add_task(run_refresh_task, category)
    return {"message": f"Scoring for {category} started in background"}

@app.post("/api/import")
async def import_symbols(data: dict = Body(...)):
    """Saves a custom list of symbols."""
    symbols = data.get("symbols", [])
    if not symbols:
        return {"error": "No symbols provided"}
    
    # Save to custom_symbols.json
    symbols_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'custom_symbols.json')
    os.makedirs(os.path.dirname(symbols_path), exist_ok=True)
    with open(symbols_path, 'w') as f:
        json.dump(symbols, f)
    
    return {"message": f"Imported {len(symbols)} symbols successfully", "count": len(symbols)}

# Serve static files from the frontend directory (để ở cuối cùng)
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), '..', 'frontend'), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
