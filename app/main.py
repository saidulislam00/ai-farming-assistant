from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router
from app.routes.recommendation import router as recommend_router
from app.routes.voice import router as voice_router
from app.routes.dashboard import router as dashboard_router

app = FastAPI(title="AI Farming Assistant (Bangla)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for prototype/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api")
app.include_router(recommend_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

# Serve frontend + dashboard as static sites
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
