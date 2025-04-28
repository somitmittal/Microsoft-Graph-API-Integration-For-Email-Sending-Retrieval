from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app import init_mongo_connection, close_mongo_connection
from app.api.routes import router
from app.exceptions import generic_exception_handler, http_exception_handler, validation_exception_handler
from app.schedulers.scheduler import start_scheduler
from config import settings


# Start the email retrieval scheduler when the app starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    start_scheduler()
    init_mongo_connection()

    yield

    # --- Shutdown (optional) ---
    close_mongo_connection()


app = FastAPI(title="Microsoft Graph API Integration", lifespan=lifespan, debug=True)

# Include API routes
app.include_router(router)

# Register error handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
