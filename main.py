from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

@app.post("/api/extract")
async def extract_media(req: URLRequest):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        # YouTube bot detection bypass karne ke liye ye options zaroori hain
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=False)
            return {
                "title": info.get('title', 'No Title'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": info.get('url', '')
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract media info: {str(e)}")

@app.get("/")
async def read_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "API is running"}