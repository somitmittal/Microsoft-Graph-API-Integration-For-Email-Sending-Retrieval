from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from app.api.routes import router
from config import settings
from app.schedulers.scheduler import start_scheduler
from app import init_mongo_connection, close_mongo_connection

# Start the email retrieval scheduler when the app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    start_scheduler()
    init_mongo_connection()

    yield

    # --- Shutdown (optional) ---
    close_mongo_connection()

app = FastAPI(title="Microsoft Graph API Integration", lifespan=lifespan)

# Include API routes
app.include_router(router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("app:main", host=settings.HOST, port=settings.PORT, reload=True)