import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import init_db, get_session, USE_ASYNC
from app.core.ollama_client import ollama_client
from app.db.seed_data import seed_palghar_data
from app.db.models import CoastalLocation, MarineWeatherRecord, FishMarketPriceRecord, GovtFisheryScheme
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.vision import router as vision_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database tables and Seed Data
    print("Initializing AquaPulse Database...")
    await init_db()
    print("Checking and seeding Palghar baseline data...")
    await seed_palghar_data()
    yield
    print("Shutting down AquaPulse...")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Smart Fisheries & Coastal Safety System for Palghar, Maharashtra",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(vision_router, prefix="/api/v1")

# Mount React Production Frontend if built
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
async def root(request: Request = None):
    index_file = os.path.join(frontend_dist, "index.html")
    if request and "text/html" in request.headers.get("accept", "") and os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "system": settings.APP_NAME,
        "region": f"{settings.DEFAULT_REGION}, {settings.DEFAULT_STATE}",
        "status": "operational",
        "docs_url": "/docs",
        "dashboard_url": "/dashboard"
    }

@app.get("/dashboard")
async def dashboard():
    index_file = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend build not found. Run 'npm run build' inside frontend directory."}

@app.get("/api/v1/health")
async def health_check():
    ollama_status = await ollama_client.check_health()
    return {
        "status": "healthy",
        "region": settings.DEFAULT_REGION,
        "ollama": ollama_status,
        "database": "connected"
    }

@app.get("/api/v1/info")
async def system_info():
    async with get_session() as session:
        if USE_ASYNC:
            loc_count = (await session.execute(select(func.count(CoastalLocation.id)))).scalar_one()
            weather_count = (await session.execute(select(func.count(MarineWeatherRecord.id)))).scalar_one()
            market_count = (await session.execute(select(func.count(FishMarketPriceRecord.id)))).scalar_one()
            scheme_count = (await session.execute(select(func.count(GovtFisheryScheme.id)))).scalar_one()
        else:
            loc_count = session.query(CoastalLocation).count()
            weather_count = session.query(MarineWeatherRecord).count()
            market_count = session.query(FishMarketPriceRecord).count()
            scheme_count = session.query(GovtFisheryScheme).count()

    return {
        "project": "AquaPulse",
        "geography": {
            "district": settings.DEFAULT_REGION,
            "state": settings.DEFAULT_STATE,
            "landing_centers_tracked": loc_count
        },
        "agents": [
            {"id": "weather", "name": "Weather Agent", "purpose": "Marine forecasts, sea condition & safe-to-sail advisory"},
            {"id": "fisheries", "name": "Fisheries Agent", "purpose": "PFZ, sustainable mesh rules & fish catch intelligence"},
            {"id": "disaster", "name": "Disaster Agent", "purpose": "High-priority cyclone, swell & storm surge alerts"},
            {"id": "market", "name": "Market Agent", "purpose": "Landing center wholesale prices & market trends"},
            {"id": "environment", "name": "Environment Agent", "purpose": "SST, Chlorophyll, salinity & water quality"},
            {"id": "scheme", "name": "Govt Scheme Agent", "purpose": "PMMSY, KCC & state subsidy RAG guidance"},
            {"id": "complaint", "name": "Complaint Agent", "purpose": "Illegal trawling & coastal grievance ticketing"}
        ],
        "database_records": {
            "locations": loc_count,
            "weather_observations": weather_count,
            "market_price_entries": market_count,
            "government_schemes": scheme_count
        }
    }
