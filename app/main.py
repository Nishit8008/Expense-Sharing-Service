from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
import app.models  # Ensure all models are registered with Base metadata
from app.routers import (
    users_router,
    groups_router,
    expenses_router,
    balances_router,
    settlements_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="""
# Decentro SDE Intern Assignment — Expense Sharing Service

A high-performance, modular backend service to manage group expenses, calculate split balances, record settlements, and optimize repayments.

## Key Features
- **User Management**: Create and list users.
- **Group Management**: Create groups, add members, and query member rosters.
- **Expense Tracking**: Add shared expenses with equal splits or custom unequal splits.
- **Pairwise Balance Calculation**: Real-time netted debt balance between group members.
- **Settlement Recording**: Track payments that clear outstanding balances.
- **Product Enhancements**:
  - Category-based spending breakdown & analytics.
  - Smart Debt Simplification using greedy Min-Cash-Flow graph algorithm.
  - Multi-attribute expense search & filtering.
  - CSV report export.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(users_router)
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(balances_router)
app.include_router(settlements_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "documentation": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
