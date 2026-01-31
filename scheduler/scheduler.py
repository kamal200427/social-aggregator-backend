# ./scheduler/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sqlalchemy.orm import Session
from database.connection import get_db, init_db
from backend.models import Post
from backend.models import UserSource
# Import connectors
from connectors.youtube_connector import fetch_youtube_videos
# from connectors.twitter_connector import fetch_tweets
from connectors.facebook_connector import fetch_facebook_posts
from connectors.linkedin_connector import fetch_linkedin_posts
from connectors.instagram_connector import fetch_instagram_posts

# -----------------------------
# Initialize Database
# -----------------------------
init_db()

# -----------------------------
# Helper: Save posts to DB
# -----------------------------
def save_posts_to_db(posts):
    """
    Insert a list of posts into the database if they don't exist.
    """
    db: Session = next(get_db())
    for post in posts:
        # Skip if post already exists
        existing = db.query(Post).filter(Post.url == post.get("url")).first()
        if existing:
            continue

        # Parse timestamp
        ts = post.get("timestamp")
        if ts:
            try:
                ts = datetime.fromisoformat(ts)
            except:
                ts = None

        new_post = Post(
            source=post.get("source"),
            author=post.get("author"),
            title=post.get("title"),
            url=post.get("url"),
            timestamp=ts,
            content=post.get("content"),
            media=post.get("media")
        )
        db.add(new_post)
    db.commit()
    db.close()


# -----------------------------
# Job: Fetch all social media posts
# -----------------------------

def fetch_all_posts():
    print(f"[{datetime.now()}] Running scheduler job...")

    db: Session = next(get_db())
    sources = db.query(UserSource).all()   # Fetch all user-saved URLs
    db.close()

    for src in sources:
        try:
            if src.platform == "youtube":
                videos = fetch_youtube_videos(src.url)
                save_posts_to_db(videos)

            elif src.platform == "facebook":
                posts = fetch_facebook_posts(src.url)
                save_posts_to_db(posts)

            # elif src.platform == "twitter":
            #     tweets = fetch_tweets(src.url)
            #     save_posts_to_db(tweets)

            elif src.platform == "instagram":
                insta_posts = fetch_instagram_posts(src.url)
                save_posts_to_db(insta_posts)

            elif src.platform == "linkedin":
                linkedin_posts = fetch_linkedin_posts(src.url)
                save_posts_to_db(linkedin_posts)

        except Exception as e:
            print(f"Error fetching from {src.platform}: {e}")

    print(f"[{datetime.now()}] Scheduler job completed.")


# -----------------------------
# Setup Scheduler
# -----------------------------
def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 10 minutes
    scheduler.add_job(fetch_all_posts, 'interval', minutes=10)
    scheduler.start()
    print("Scheduler started. Fetching social media posts every 10 minutes.")

    # Keep script running
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


# -----------------------------
# Run Scheduler
# -----------------------------
if __name__ == "__main__":
    start_scheduler()
