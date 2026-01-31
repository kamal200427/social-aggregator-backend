import re
import requests
import feedparser
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re
import requests

def get_feed_url_from_video(video_url: str) -> str:
    """
    Extract YouTube channel feed URL from any valid video link.
    """
    try:
        if not isinstance(video_url, str):
            print("❌ Provided video_url is not a string:", type(video_url))
            return None

        video_id = None

        # Handle multiple YouTube URL formats
        if "youtu.be" in video_url:
            video_id = video_url.split("/")[-1].split("?")[0]
        elif "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "shorts/" in video_url:
            video_id = video_url.split("shorts/")[1].split("?")[0]

        if not video_id or not isinstance(video_id, str):
            print("❌ Could not extract valid video_id")
            return None

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(video_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print("❌ Failed to fetch HTML:", response.status_code)
            return None

        match = re.search(r'"channelId":"(UC[\w-]+)"', response.text)
        if match:
            channel_id = match.group(1)
            print(f"✅ Extracted channel ID: {channel_id}")
            return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        else:
            print("❌ No channelId found in HTML")
            return None

    except Exception as e:
        print(f"⚠️ Error extracting channel feed: {e}")
        return None



def convert_to_embed(url: str) -> str:
    """Convert a normal YouTube or Shorts URL into an embeddable format."""
    try:
        if "youtube.com/watch?v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
        elif "youtube.com/shorts/" in url:
            video_id = url.split("shorts/")[-1].split("?")[0]
        else:
            return None
        return f"https://www.youtube.com/embed/{video_id}"
    except Exception:
        return None


def parse_youtube_date(date_str):
    """Convert YouTube feed date string to ISO format."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.isoformat()
    except Exception:
        return date_str


def get_thumbnail_url(video_url):
    """Generate default YouTube thumbnail URL from video link."""
    try:
        parsed_url = urlparse(video_url)
        if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
            video_id = parse_qs(parsed_url.query).get("v")
            if video_id:
                return f"https://img.youtube.com/vi/{video_id[0]}/hqdefault.jpg"
        elif parsed_url.hostname == "youtu.be":
            video_id = parsed_url.path.lstrip("/")
            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    except Exception:
        pass
    return ""


def fetch_youtube_videos(feed_url, channel_id=None):
    """
    Fetch latest YouTube videos from a channel or playlist RSS feed.
    Returns a list of dicts ready for saving or display.
    """
    feed = feedparser.parse(feed_url)
    videos = []

    for entry in feed.entries:
        link = entry.get("link", "")
        video = {
            "source": "youtube",
            "source_channel": channel_id,
            "author": feed.feed.get("title", "Unknown"),
            "title": entry.get("title", ""),
            "url": link,
            "timestamp": parse_youtube_date(entry.get("published", "")),
            "content": entry.get("summary", ""),
            "thumbnail": get_thumbnail_url(link),
            # 🆕 Added fields
            "media": convert_to_embed(link),
            "media_type": "video"
        }
        videos.append(video)

    return videos
