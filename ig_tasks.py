"""
Instagram tasks: download, overlay thumbnail, post.
"""

import os
import random
import uuid
from yt_dlp import YoutubeDL
from PIL import Image
from instagrapi import Client

import config
import db


def download_reel(url: str) -> str:
    """Download a reel using yt-dlp."""
    os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
    out_id = str(uuid.uuid4())[:8]
    out_template = os.path.join(config.DOWNLOAD_DIR, f"{out_id}.%(ext)s")

    import re
    url_to_use = url
    if "instagram.com" in url and "reel" in url:
        match = re.search(r'/reel/([a-zA-Z0-9_-]+)', url)
        if match:
            reel_id = match.group(1)
            url_to_use = f"https://www.instagram.com/reel/{reel_id}/"

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': out_template,
            'quiet': False,
            'no_warnings': False,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_to_use])
    except Exception as e:
        raise RuntimeError(f"Download failed: {str(e)}")

    for fname in os.listdir(config.DOWNLOAD_DIR):
        if fname.startswith(out_id):
            return os.path.join(config.DOWNLOAD_DIR, fname)

    raise RuntimeError("Download succeeded but file not found")


def add_black_fade(video_path: str, fade_seconds: float = 0.5, position: str = "start") -> str:
    """
    Add a black screen fade at the start or end of the video.
    This changes the file hash (so Instagram doesn't flag it as a duplicate)
    without cutting any actual content from the meme.
    
    position: "start" or "end"
    """
    import subprocess
    import json

    # Get video duration and properties
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,stream=width,height",
        "-of", "json",
        video_path
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    duration = float(data["format"]["duration"])
    # Get video dimensions from first video stream
    stream = next((s for s in data["streams"] if s.get("width")), None)
    if not stream:
        raise RuntimeError("Could not detect video dimensions")
    width, height = stream["width"], stream["height"]

    out_path = os.path.splitext(video_path)[0] + "_faded.mp4"

    if position == "start":
        # Create black video, concat: [black] + [original]
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:d={fade_seconds}",
            "-i", video_path,
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[outv]",
            "-map", "[outv]",
            "-c:v", "libx264", "-crf", "23",
            out_path
        ]
    else:  # end
        # Concat: [original] + [black]
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:d={fade_seconds}",
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[outv]",
            "-map", "[outv]",
            "-c:v", "libx264", "-crf", "23",
            out_path
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg fade failed: {result.stderr}")

    return out_path


def get_thumbnail_path(video_path: str, thumbnail_image_path: str) -> str:
    """Ensure thumbnail is JPEG format."""
    img = Image.open(thumbnail_image_path).convert("RGB")
    out_path = os.path.splitext(video_path)[0] + "_thumb.jpg"
    img.save(out_path, "JPEG", quality=95)
    return out_path


def pick_description(override: str = None) -> str:
    """Pick a random description, or use override."""
    if override:
        return override
    return random.choice(config.DESCRIPTIONS)


def get_client() -> Client:
    """Log into Instagram."""
    cl = Client()
    if os.path.exists(config.SESSION_FILE):
        try:
            cl.load_settings(config.SESSION_FILE)
            cl.login(config.IG_USERNAME, config.IG_PASSWORD)
        except Exception:
            cl.login(config.IG_USERNAME, config.IG_PASSWORD)
    else:
        cl.login(config.IG_USERNAME, config.IG_PASSWORD)
    cl.dump_settings(config.SESSION_FILE)
    return cl


def post_reel(video_path: str, description: str = None) -> dict:
    """Download thumbnail, pick description, and post."""
    description = pick_description(description)
    thumb_path = get_thumbnail_path(video_path, config.DEFAULT_THUMBNAIL_PATH)
    
    cl = get_client()
    media = cl.clip_upload(
        path=video_path,
        caption=description,
        thumbnail=thumb_path,
    )
    
    return {
        "media_id": str(media.pk),
        "description": description,
        "url": f"https://www.instagram.com/reel/{media.code}/",
    }


def process_queue():
    """
    Worker: grab next pending item, download, post, update status.
    Call this in a loop from a background thread.
    """
    item = db.get_pending()
    if not item:
        return  # Nothing to do
    
    item_id = item["id"]
    url = item["url"]
    description = item["description"]
    
    try:
        # Download
        video_path = download_reel(url)
        db.update_status(item_id, "downloading", video_path=video_path)

        # Trim/re-encode so it's not flagged as a duplicate of the original
        try:
            video_path = add_black_fade(video_path, fade_seconds=config.TRIM_SECONDS, position="end")
        except Exception as trim_err:
            # If ffmpeg isn't available or trim fails, fall back to original file
            print(f"Trim failed, posting original file: {trim_err}")

        # Post
        result = post_reel(video_path, description)
        db.update_status(item_id, "posted", posted_url=result["url"])
        
        return {"ok": True, "id": item_id, "url": result["url"]}
    except Exception as e:
        error_msg = str(e)
        db.update_status(item_id, "failed", error_msg=error_msg)
        return {"ok": False, "id": item_id, "error": error_msg}
