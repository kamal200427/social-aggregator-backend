# ./connectors/twitter_connector.py
# Temporary fix for snscrape on Python 3.12+
# This connector MUST run with Python 3.11 when executed directly (NOT when imported)

import sys
import importlib
import importlib.machinery
from datetime import datetime


# ----- FIX: Remove version check from top-level -----
# Version check should not run during import.
# It will run ONLY when file is executed as __main__.


# Fix for missing find_module() in Python 3.12+
if not hasattr(importlib.machinery.FileFinder, "find_module"):
    def find_module(self, fullname, path=None):
        return None
    importlib.machinery.FileFinder.find_module = find_module


# Try loading snscrape
try:
    sntwitter = importlib.import_module("snscrape.modules.twitter")
except Exception:
    class _MissingScrapeModule:
        class TwitterUserScraper:
            def __init__(self, username):
                raise ImportError(
                    "snscrape is required for Twitter scraping. Install it with: pip install snscrape"
                )
    sntwitter = _MissingScrapeModule


# ===========================
# Fetch Tweets (using snscrape)
# ===========================
import sys
import json
import subprocess

def fetch_tweets(username):
    cmd = [
        "snscrape",
        "twitter-user",   # ✔ correct format
        username
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception("SNScrape failed: " + result.stderr)

    tweets = []
    for line in result.stdout.splitlines():
        tweets.append(json.loads(line))

    return tweets[:5]  # Return latest 5 tweets

if __name__ == "__main__":
    username = sys.argv[1]
    tweets = fetch_tweets(username)
    print(json.dumps(tweets))
