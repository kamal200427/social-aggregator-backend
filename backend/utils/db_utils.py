# ./backend/utils/db_utils.py
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import Post
from sqlalchemy.exc import OperationalError
import time

def safe_commit(db, retries=3):
    for i in range(retries):
        try:
            db.commit()
            return
        except OperationalError:
            db.rollback()
            print(f"⚠️ Database locked, retrying... ({i+1}/{retries})")
            time.sleep(1)
    raise

def save_ytvideos_to_db(db: Session, videos: list, channel_id: str):
    """
    Save YouTube videos to DB for a specific channel.
    Deletes old videos from other channels, keeps persistence for this channel.
    """
    if not videos:
        print("⚠️ No videos to save.")
        return
    print(f"💾 Saving {len(videos)} videos for channel {channel_id}")
    # ✅ Delete videos not belonging to this channel
    db.query(Post).filter(Post.source == "youtube", Post.source_channel !=channel_id).delete()
    print("check count",len(videos))
    count = 0
    for video in videos:
        print("check")
        existing = db.query(Post).filter(Post.url == video.get("url")).first()
        print(existing)
        if existing:
            continue
        print("1")
        ts = video.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.utcnow()
        print("hello2")
        post = Post(
            source="youtube",
            source_channel=channel_id,
            author=video.get("author"),
            title=video.get("title"),
            url=video.get("url"),
            timestamp=ts,
            content=video.get("content"),
            media=video.get("media") or video.get("thumbnail"),
        )
        print(post.url,post.content)
        print("just fun") 
        db.add(post)
        count += 1

    safe_commit(db)

     
