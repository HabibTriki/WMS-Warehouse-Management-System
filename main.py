from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from api.routes import fulfillment
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting WMS application...")
    print(f"Database: {settings.database_url}")
    print(f"ESB1 (IMS): {settings.esb1_base_url}")
    print(f"ESB3 (DMS): {settings.esb3_base_url}")
    
    create_db_and_tables()
    print("Database tables created")
    
    yield
    
    print("Shutting down WMS application...")
    

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

origins = [origin.strip() for origin in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fulfillment.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "ShipOra WMS",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "wms",
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
