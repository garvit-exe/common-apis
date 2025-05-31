# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import text_manipulation, fun_creative, dev_utils, data_fetching # We'll create these soon

app = FastAPI(
    title="Common APIs Hub",
    description="A collection of commonly needed and fun API endpoints.",
    version="0.1.0",
    docs_url="/", # Serve docs at the root
    redoc_url="/redoc"
)

# CORS (Cross-Origin Resource Sharing)
# Allows requests from any origin. For production, you might want to restrict this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Or specify domains: ["http://localhost:3000", "https://your-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Include routers from different modules
app.include_router(text_manipulation.router, prefix="/text", tags=["Text Manipulation"])
app.include_router(fun_creative.router, prefix="/fun", tags=["Fun & Creative"])
app.include_router(dev_utils.router, prefix="/dev", tags=["Developer Utilities"])
app.include_router(data_fetching.router, prefix="/data", tags=["Data Fetching"])

# Simple root endpoint (optional, as docs are at root now)
# @app.get("/api-status", tags=["General"])
# async def api_status():
#     return {"status": "API is running smoothly!"}

# Note: For Vercel, the `app` instance is automatically picked up.
# For local development, you'd run: uvicorn api.index:app --reload