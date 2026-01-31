# ./connectors/instagram_connector.py

import requests
from datetime import datetime

# ===========================
# Instagram Graph API Setup
# ===========================
# You need:
# 1. Facebook Developer App
# 2. Instagram Business/Creator account
# 3. Access Token (long-lived recommended)
ACCESS_TOKEN = "EAAMTZBq3Sy9QBPyZAXSnqKyLzxqkfq5TZCnAcEF9IUAU9B6PaGSneJeHma4Mld2h7uXpnFZAnNxMASOQ8cQcG0cbVCZAZCiVCfJZCMdVrpWWewNBp445P8ZAQk2bH9PwAiZBEd18fZAVuO0KiYnXApi1WbTtsEvOrFZBbQ1ttsvh4KkEsiePfZAy6anAXZCCXm0TmrZCZAdZCtlKzJBfWLWmlPFcJZAxYNBOjFdInZCFwTRafwqeKk2VDwCiJxSvQ3Qns4xph6JcLfbNyviXPg4YLs6iha"
BASE_URL = "https://graph.facebook.com/v17.0/"  # Adjust version if needed


def fetch_instagram_posts(user_id, max_count=10):
    """
    Fetch latest posts from an Instagram Business/Creator account.
    
    Args:
        user_id (str): Instagram user ID (numeric, from Graph API)
        max_count (int): Number of posts to fetch

    Returns:
        List[dict]: Normalized Instagram posts
    """
    url = f"{BASE_URL}{user_id}/media?fields=id,caption,media_type,media_url,permalink,timestamp&access_token={ACCESS_TOKEN}&limit={max_count}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        posts = []
        for post in data.get("data", []):
            posts.append({
                "source": "instagram",
                "author": user_id,
                "title": post.get("caption", "")[:50] + "..." if post.get("caption", "") else "",
                "url": post.get("permalink", ""),
                "timestamp": parse_instagram_date(post.get("timestamp", "")),
                "content": post.get("caption", ""),
                "media": post.get("media_url", "")
            })
        
        return posts
    
    except Exception as e:
        print(f"Error fetching Instagram posts: {e}")
        return []


def parse_instagram_date(date_str):
    """Convert Instagram timestamp to ISO format"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.isoformat()
    except Exception:
        return date_str  # fallback if parsing fails


# ===========================
# Example usage
# ===========================
if __name__ == "__main__":
    user_id = "17841400000000000"  # Instagram Business/Creator numeric ID
    posts = fetch_instagram_posts(user_id)
    for p in posts:
        print(p["title"], p["url"], p["timestamp"])
