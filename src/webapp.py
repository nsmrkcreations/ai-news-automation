"""
Development web server for serving the frontend
"""
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/", StaticFiles(directory="public", html=True), name="static")

# Serve index.html for the root path
@app.get("/")
async def read_root():
    return FileResponse("public/index.html")

# Get news data
@app.get("/api/news")
async def get_news():
    try:
        with open("public/data/news.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
