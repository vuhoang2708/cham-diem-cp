from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from database import get_all_scores
import main_scorer
import asyncio

app = FastAPI(title="VN100 Stock Scorer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global status tracking
status = {
    "is_running": False,
    "last_run": None,
    "progress": 0,
    "current_symbol": ""
}

@app.get("/api/scores")
async def read_scores():
    """Returns the latest scores from the database."""
    return get_all_scores()

@app.get("/api/status")
async def get_status():
    """Returns the current background task status."""
    return status

async def run_refresh_task():
    global status
    status["is_running"] = True
    try:
        await main_scorer.run_scoring()
    except Exception as e:
        print(f"Error in refresh task: {e}")
    finally:
        status["is_running"] = False

@app.post("/api/refresh")
async def refresh_scores(background_tasks: BackgroundTasks):
    """Triggers a background refresh of the scoring database."""
    if status["is_running"]:
        return {"message": "Scoring is already in progress"}
    
    background_tasks.add_task(run_refresh_task)
    return {"message": "Scoring process started in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
