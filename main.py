from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI(title="All-in-One Media Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoRequest(BaseModel):
  url: str


@app.get("/", response_class=HTMLResponse)
def serve_home():
  if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
      return f.read()
  return "<h1>Media Extractor API is Running</h1>"


@app.get("/{tool_name}", response_class=HTMLResponse)
def serve_tool_pages(tool_name: str):
  # SEO routes for target long-tail keywords
  valid_tools = [
      "youtube-downloader",
      "tiktok-downloader",
      "twitter-downloader",
      "instagram-downloader",
  ]
  if tool_name in valid_tools:
    if os.path.exists("index.html"):
      with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
  raise HTTPException(status_code=404, detail="Page not found")


@app.post("/api/extract")
def extract_video_info(data: VideoRequest):
  url = data.url.strip()
  if not url:
    raise HTTPException(status_code=400, detail="Please provide a valid URL.")

  ydl_opts = {
      "quiet": True,
      "no_warnings": True,
      "format": "best/bestvideo+bestaudio/worst",
      "skip_download": True,
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)

      return {
          "title": info.get("title", "No Title"),
          "thumbnail": info.get("thumbnail", ""),
          "duration": info.get("duration", 0),
          "download_url": info.get("url", ""),
          "platform": info.get("extractor_key", "Media"),
      }
  except Exception as e:
    raise HTTPException(
        status_code=500, detail=f"Failed to extract media info: {str(e)}"
    )