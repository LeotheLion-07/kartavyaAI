from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal, sync_database_schema
from app.data.seed_data import seed_database
from app.api import (
    auth, projects, sources, claims, decisions,
    conflicts, gaps, handovers, chat, permissions,
    audit, analytics
)

# Initialize database tables
Base.metadata.create_all(bind=engine)
# Ensure schema backward-compatibility for enhanced columns
sync_database_schema(engine)

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
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers under /api/v1 and fallback /v1
for prefix in [settings.API_V1_STR, "/v1"]:
    app.include_router(auth.router, prefix=prefix)
    app.include_router(projects.router, prefix=prefix)
    app.include_router(sources.router, prefix=prefix)
    app.include_router(claims.router, prefix=prefix)
    app.include_router(decisions.router, prefix=prefix)
    app.include_router(conflicts.router, prefix=prefix)
    app.include_router(gaps.router, prefix=prefix)
    app.include_router(handovers.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(permissions.router, prefix=prefix)
    app.include_router(audit.router, prefix=prefix)
    app.include_router(analytics.router, prefix=prefix)

@app.get("/")
@app.get("/api")
@app.get("/api/v1")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "operational",
        "docs_url": "/docs"
    }

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "kartavya-ai-core"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
