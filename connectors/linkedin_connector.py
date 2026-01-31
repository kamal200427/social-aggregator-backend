# ./connectors/linkedin_connector.py

import requests
from datetime import datetime

# ===========================
# Option 1: LinkedIn API (Recommended)
# ===========================

# Replace with your LinkedIn access token
ACCESS_TOKEN = "YOUR_LINKEDIN_ACCESS_TOKEN"
BASE_URL = "https://api.linkedin.com/v2/"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0"
}


def fetch_linkedin_posts(organization_id, max_count=10):
    """
    Fetch latest posts from a LinkedIn company page using LinkedIn API.
    
    Args:
        organization_id (str): LinkedIn organization/company ID
        max_count (int): Maximum number of posts to fetch
        
    Returns:
        List[dict]: Normalized LinkedIn posts
    """
    url = f"{BASE_URL}ugcPosts?q=authors&authors=List(urn:li:organization:{organization_id})&count={max_count}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        posts = []
        for post in data.get("elements", []):
            content_text = ""
            if "specificContent" in post and "com.linkedin.ugc.ShareContent" in post["specificContent"]:
                share_content = post["specificContent"]["com.linkedin.ugc.ShareContent"]
                content_text = share_content.get("shareCommentary", {}).get("text", "")
            
            posts.append({
                "source": "linkedin",
                "author": organization_id,
                "title": content_text[:50] + "..." if len(content_text) > 50 else content_text,
                "url": f"https://www.linkedin.com/feed/update/{post.get('id', '')}",
                "timestamp": parse_linkedin_date(post.get("created", {})),
                "content": content_text,
                "media": get_linkedin_media(post)
            })
        
        return posts
    
    except Exception as e:
        print(f"Error fetching LinkedIn posts: {e}")
        return []


def parse_linkedin_date(date_dict):
    """Convert LinkedIn timestamp to ISO format"""
    try:
        if "time" in date_dict:
            ts = int(date_dict["time"]) / 1000  # LinkedIn timestamp is in ms
            return datetime.utcfromtimestamp(ts).isoformat()
    except Exception:
        pass
    return None


def get_linkedin_media(post):
    """Extract media URLs if available"""
    media_urls = []
    try:
        media_elements = post.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("media", [])
        for m in media_elements:
            if "media" in m and "com.linkedin.common.MediaProxyImage" in m["media"]:
                media_urls.append(m["media"]["com.linkedin.common.MediaProxyImage"]["url"])
    except Exception:
        pass
    return media_urls

# ===========================
# Option 2: Web scraping (Not recommended)
# ===========================
# You could use selenium + BeautifulSoup to fetch public posts, but LinkedIn actively blocks scrapers.
# This is less reliable and may break anytime.

# ===========================
# Example usage
# ===========================
if __name__ == "__main__":
    org_id = "12345678"  # LinkedIn company ID
    posts = fetch_linkedin_posts(org_id)
    for p in posts:
        print(p["title"], p["url"], p["timestamp"])
