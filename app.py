import uvicorn
from fastapi import FastAPI
from app.api.routes import router
from config import settings
from scheduler import start_scheduler

app = FastAPI(title="Microsoft Graph API Integration")

# Include API routes
app.include_router(router, prefix="/api")

# Start the email retrieval scheduler when the app starts
@app.on_event("startup")
async def startup_event():
    start_scheduler()

if __name__ == "__main__":
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)