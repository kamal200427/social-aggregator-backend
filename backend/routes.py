# ./backend/routes.py
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from backend.channel import load_channel_state
from backend.models import Post, UserSource
from database.connection import get_db
 
router = APIRouter()  # No prefix here; prefix is applied in main.py

# -----------------------------
# GET Posts
# -----------------------------
@router.get("/posts")
def get_posts(source: Optional[str] = None , db: Session = Depends(get_db)):
    """
    Fetch posts from the database.
    Optional query parameter: source (youtube, twitter, facebook, linkedin, instagram)
    """
    posts = db.query(Post).first()
    print(posts.source)
    channel_id=load_channel_state(posts.source)
    query = db.query(Post)
    if channel_id:
        query = query.filter(Post.source_channel == channel_id)
    if source:
        query = query.filter(Post.source == source.lower())
    
    posts = query.order_by(Post.timestamp.desc()).all()
     
    return [
        {
            "id": p.id,
            "source": p.source,
            "author": p.author,
            "title": p.title,
            "url": p.url,
            "timestamp": p.timestamp.isoformat() if p.timestamp else None,
            "content": p.content,
            "media": p.media,
        }
    
        for p in posts
    ]

# -----------------------------
# POST New Post
# -----------------------------
@router.post("/posts")
def create_post(post: dict, db: Session = Depends(get_db)):
    existing = db.query(Post).filter(Post.url == post.get("url")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Post already exists")

    timestamp = post.get("timestamp")
    if timestamp:
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            timestamp = None

    new_post = Post(
        source=post.get("source"),
        author=post.get("author"),
        title=post.get("title"),
        source_channel=post.get("source_channel"),
        url=post.get("url"),
        timestamp=timestamp,
        content=post.get("content"),
        media=post.get("media"),
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "Post added", "id": new_post.id}

# -----------------------------
# Health Check
# -----------------------------
@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/add_source")
def add_source(platform: str, url: str, db: Session = Depends(get_db)):
    new_source = UserSource(platform=platform, url=url)
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return {"message": "Source added successfully!", "id": new_source.id}
