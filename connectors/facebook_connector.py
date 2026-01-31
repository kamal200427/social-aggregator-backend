import re
import requests
from datetime import datetime

# ===========================
# Facebook Graph API Setup
# ===========================
ACCESS_TOKEN = "EAAMTZBq3Sy9QBP9eTZCjZBZB5nifc5pWMhn2uQfJlLDyHUtc2BTcuGnhkbTyP6IEUTs72RhqU5JfrCbhEK9nFIXyBYoHQ8ny1Ifv7NFhIrA5OtAEj1QlyQF2TvhDskDyR1aGCX9l5XBg9gp2Sv0KM0xXFa5puvw7O2ZCTNZCIB64RrI3KVVM0p3lRaxdn95XzT1AARLepq84mcoUpcFzHLJ9Ha30NIUm7lgnYZCpYh5VW7KIwZDZD"
BASE_URL = "https://graph.facebook.com/v17.0/"  # Adjust version if needed


def extract_page_id_from_url(url_or_id):
    """
    Extracts Facebook Page, Photo, Video, or Reel IDs from a URL.
    Returns a tuple: (id, type)
    """
    if not url_or_id.startswith("http"):
        return url_or_id.strip(), "page"

    # 1️⃣ Photo
    fbid_match = re.search(r"[?&]fbid=(\d+)", url_or_id)
    if fbid_match:
        photo_id = fbid_match.group(1)
        print(f"📷 Detected Facebook photo ID: {photo_id}")
        return photo_id, "photo"

    # 2️⃣ Watch video
    watch_match = re.search(r"facebook\.com/watch\?v=(\d+)", url_or_id)
    if watch_match:
        video_id = watch_match.group(1)
        print(f"🎥 Detected Facebook Watch video ID: {video_id}")
        return video_id, "video"

    # 3️⃣ Reel
    reel_match = re.search(r"facebook\.com/reel/(\d+)", url_or_id)
    if reel_match:
        reel_id = reel_match.group(1)
        print(f"🎞️ Detected Facebook Reel ID: {reel_id}")
        return reel_id, "reel"

    # 4️⃣ Page
    page_match = re.search(r"facebook\.com/([^/?&]+)/", url_or_id)
    if page_match:
        page_name = page_match.group(1)
        print(f"👤 Detected Facebook Page: {page_name}")
        return page_name, "page"

    raise ValueError("Could not extract Facebook ID from the provided URL.")



def fetch_facebook_posts(page_input, max_count=10):
    """
    Fetch posts or media info from a Facebook URL.
    Supports Page, Photo, Video, and Reel.
    """
    try:
        print("hi checking")
        # Extract ID and type
        if isinstance(page_input, tuple):
            obj_id, obj_type = page_input
        else:
            obj_id, obj_type = extract_page_id_from_url(page_input)
        print(f"📘 Fetching Facebook {obj_type}: {obj_id}")
        print("running")
        if obj_type == "page":
            endpoint = f"{BASE_URL}{obj_id}/posts"
            params = {
                "fields": "id,message,created_time,permalink_url,full_picture",
                "limit": max_count,
                "access_token": ACCESS_TOKEN
            }

        elif obj_type in ["photo", "video", "reel"]:
            print("baseurl")
            endpoint = f"{BASE_URL}{obj_id}"
            print("baseurl after")
            params = {
                "fields": "id,permalink_url,created_time,full_picture,description",
                "access_token": ACCESS_TOKEN
            }

        else:
            raise ValueError(f"Unknown Facebook object type: {obj_type}")

        # Fetch from Facebook Graph API
        print("before")
        response = requests.get(endpoint, params=params)
        print(response)
        print("after")
        response.raise_for_status()
        print("response is comming")
        data = response.json()

        # Normalize
        posts = []
        if obj_type == "page":
            for post in data.get("data", []):
                posts.append({
                    "source": "facebook",
                    "author": obj_id,
                    "title": post.get("message", "")[:50],
                    "url": post.get("permalink_url", ""),
                    "timestamp": parse_facebook_date(post.get("created_time", "")),
                    "content": post.get("message", ""),
                    "media": post.get("full_picture", "")
                })
        else:
            posts.append({
                "source": "facebook",
                "author": obj_id,
                "title": data.get("description", "")[:50],
                "url": data.get("permalink_url", ""),
                "timestamp": parse_facebook_date(data.get("created_time", "")),
                "content": data.get("description", ""),
                "media": data.get("full_picture", "")
            })

        return posts

    except Exception as e:
        print(f"Error fetching Facebook posts: {e}")
        return []



def parse_facebook_date(date_str):
    """
    Convert Facebook timestamp to ISO format.
    Example: '2025-10-18T10:00:00+0000'
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.isoformat()
    except Exception:
        return date_str


# ===========================
# Example usage
# ===========================
if __name__ == "__main__":
    # You can pass a full video/post URL OR just the page name
    example_url = "https://www.facebook.com/bbcnews/videos/123456789/"
    posts = fetch_facebook_posts(example_url)

    for p in posts:
        print(p["title"], "|", p["url"], "|", p["timestamp"])
