from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.data.seed_data import seed_database
from app.api import (
    auth, projects, sources, claims, decisions,
    conflicts, gaps, handovers, chat, permissions,
    audit, analytics
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Seed with enterprise demo records on boot
try:
    with SessionLocal() as db:
        seed_database(db)
except Exception as e:
    print(f"Database seed notice: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Kartavya AI: Pass on what matters, with proof. Enterprise Knowledge Handover Platform.",
    version=settings.VERSION
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(sources.router, prefix=settings.API_V1_STR)
app.include_router(claims.router, prefix=settings.API_V1_STR)
app.include_router(decisions.router, prefix=settings.API_V1_STR)
app.include_router(conflicts.router, prefix=settings.API_V1_STR)
app.include_router(gaps.router, prefix=settings.API_V1_STR)
app.include_router(handovers.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(permissions.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "operational",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "kartavya-ai-core"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
