# ./backend/main.py
import subprocess
import json
import os

def get_twitter_data(username):
    env_python = os.path.join("scrape-env", "Scripts", "python.exe")
    script_path = os.path.join("connectors", "twitter_connector.py")

    result = subprocess.run(
        [env_python, script_path, username],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("❌ Subprocess Error:", result.stderr)
        raise Exception("Twitter scraper execution failed")
    return json.loads(result.stdout)

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.utils.db_utils import save_ytvideos_to_db
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from flask import request
from database.connection import Base, engine, SessionLocal
from database.connection import get_db
from connectors.youtube_connector import get_feed_url_from_video, fetch_youtube_videos
from connectors.facebook_connector import extract_page_id_from_url,fetch_facebook_posts
from connectors.twitter_connector import fetch_tweets
from fastapi import Depends
from sqlalchemy.orm import Session

from urllib.parse import urlparse
import feedparser
from datetime import datetime
from backend.routes import router
from backend.channel import save_channel_state
import re
from backend.login import checking,login_user
from scheduler.scheduler import save_posts_to_db
from fastapi import Request

app = FastAPI(title="Social Media Aggregator API")

origins = ["http://127.0.0.1:3000", "http://localhost:3000"]
 


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)



app.include_router(router, prefix="/api") 
@app.get("/api/test")
def test():
    return {"message": "Router working!"}
print(app.routes)

@app.post("/api/fetch_from_url")
async def fetch_from_url(request: Request, background_tasks: BackgroundTasks):
     
    try:
        data = await request.json()
        print(data)
        url = data.get("url")
        db = SessionLocal()

        if "youtube.com" in url or "youtu.be" in url:
            feed_url = get_feed_url_from_video(url)
            print("🎯 Feed URL generated:", feed_url)
            if not feed_url:
                raise HTTPException(status_code=400, detail="Could not extract channel feed URL")
            videos = fetch_youtube_videos(feed_url)
            print("📹 Videos fetched:", len(videos))
            if not videos:
                raise HTTPException(status_code=404, detail="No videos found for this channel")

            # ✅ Extract channel_id from feed_url
            match = re.search(r"channel_id=([^&]+)", feed_url)
            channel_id = match.group(1) if match else None
            if channel_id:
                source="youtube"
                save_ytvideos_to_db(db, videos, channel_id)
                save_channel_state(channel_id,source)
                 
             
            videos = videos[:30]
            # print(videos)
            return videos
        elif "facebook.com" in url:
    
            print("📘 Fetching Facebook posts...")
            fb_obj = extract_page_id_from_url(url)  # returns (id, type)
            posts = fetch_facebook_posts(fb_obj)    # handle tuple directly
            print("post=",posts)
            obj_id, obj_type = fb_obj
            channel_id = obj_id
             
            if posts:
                source="facebook"
                print("hello world")
                save_posts_to_db(posts)
                save_channel_state(channel_id,source)
                print(f"✅ Saved {len(posts)} posts for {channel_id}")
            else:
                print(f"⚠️ No posts found for {channel_id}")

            return posts
        elif "twitter.com" in url or "x.com" in url:
            print("🐦 Fetching Twitter posts...")
            print("check_twitt")
            # Extract username
            parsed = urlparse(url)
            path_parts= parsed.path.strip("/").split("/")
            username = path_parts[0] if len(path_parts) > 0 else None
            print(username)
            if not username:
                raise HTTPException(status_code=400, detail="Invalid Twitter username")

            print(f"🐦 Username detected: {username}")

    # Run Python 3.11 scraper in subprocess
            try:
                posts = get_twitter_data(username)
                print(posts[0])
            except Exception as e:
                print("❌ Twitter scrape error:", e)
                raise HTTPException(status_code=500, detail="Twitter scraping failed")

            if not posts:
                raise HTTPException(status_code=404, detail="No tweets found")

            save_channel_state(username, "twitter")
            print(f"✅ Saved {len(posts)} tweets from {username}")
            return posts

    except Exception as e:
        print(f"❌ Internal error in fetch_from_url: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # 📰 RSS Fallback
    try:
        print("📰 Trying RSS feed fallback...")
        feed = feedparser.parse(url)
        if feed.entries:
            posts = []
            for entry in feed.entries[:5]:
                posts.append({
                    "source": "rss",
                    "title": entry.get("title", "Untitled"),
                    "content": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "timestamp": datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.now(),
                })
            return {"message": f"Fetched {len(posts)} RSS posts", "posts": posts}
        else:
            raise Exception("No entries found")
    except Exception as e:
        print("❌ Error fetching RSS:", e)
        raise HTTPException(status_code=400, detail="Could not fetch posts from this URL")
@app.post("/api/register")
async def register(data: dict,
    db: Session = Depends(get_db)):
    return checking(data["name"],data["email"],data["username"],data["password"],db)

@app.post("/api/login")
def login(data: dict, db: Session = Depends(get_db)):
    return login_user(
        data.get("username"),
        data.get("password"),
        db
    )