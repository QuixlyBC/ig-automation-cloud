"""
Cloud-hosted Instagram Reel Automation.
Paste URLs, auto-post with random descriptions.

Run with:
    python app.py

Or on Heroku/Railway, set:
    IG_USERNAME=your_username
    IG_PASSWORD=your_password
"""

import os
from flask import Flask, render_template, request, jsonify

import config
import db
from worker import start_worker

app = Flask(__name__)

# Initialize database and start background worker
db.init_db()
start_worker()


@app.route("/")
def index():
    """Dashboard showing queue status."""
    items = db.get_all()
    stats = {
        "total": len(items),
        "posted": len([i for i in items if i["status"] == "posted"]),
        "pending": len([i for i in items if i["status"] == "pending"]),
        "failed": len([i for i in items if i["status"] == "failed"]),
    }
    return render_template("index.html", items=items, stats=stats, descriptions=config.DESCRIPTIONS)


@app.route("/api/add", methods=["POST"])
def api_add():
    """Add a reel URL to the queue."""
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    description = data.get("description", "").strip() or None
    
    if not url:
        return jsonify({"ok": False, "error": "No URL provided"}), 400
    
    if not url.startswith("http"):
        url = f"https://{url}"
    
    result = db.add_reel(url, description)
    if result["ok"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route("/api/queue")
def api_queue():
    """Get all queue items (for live updates)."""
    items = db.get_all()
    stats = {
        "total": len(items),
        "posted": len([i for i in items if i["status"] == "posted"]),
        "pending": len([i for i in items if i["status"] == "pending"]),
        "failed": len([i for i in items if i["status"] == "failed"]),
    }
    return jsonify({"items": items, "stats": stats})


@app.route("/api/delete/<int:item_id>", methods=["DELETE"])
def api_delete(item_id):
    """Remove an item from the queue."""
    db.delete_item(item_id)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
