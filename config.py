"""
Cloud version config — all secrets from environment variables.
"""

import os

# --- Instagram credentials (set these as env vars) ---
IG_USERNAME = os.environ.get("IG_USERNAME", "")
IG_PASSWORD = os.environ.get("IG_PASSWORD", "")

if not IG_USERNAME or not IG_PASSWORD:
    raise ValueError("Set IG_USERNAME and IG_PASSWORD as environment variables")

SESSION_FILE = "ig_session.json"

# --- Descriptions (4 random picks) ---
DESCRIPTIONS = [
    "Check this out 🔥",
    "Thoughts? 👀",
    "Who else sees this? 💯",
    "This hits different 🎯",
]

# --- Thumbnail (upload once, reuse for all posts) ---
DEFAULT_THUMBNAIL_PATH = "thumbnail.jpg"

# --- Folders ---
DOWNLOAD_DIR = "downloads"
DB_PATH = "queue.db"

# --- Flask server ---
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# --- Background worker (check queue every N seconds) ---
WORKER_INTERVAL = 60  # Check queue every 60 seconds

# --- Video trimming (helps avoid duplicate-content detection) ---
TRIM_SECONDS = 0.5  # Black screen duration added at end (doesn't cut content)
