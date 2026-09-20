# Reel Automation — Cloud Version

Paste Instagram reel URLs. Auto-download, auto-post with random descriptions, all in the cloud.

## Features

- **Queue system** — Add URLs, they're processed in order
- **Background worker** — Runs 24/7, checking every 60 seconds
- **Dashboard** — See status of all posts (pending, posted, failed)
- **Auto-descriptions** — Picks randomly from 4 pre-written descriptions
- **Static thumbnail** — Same image on all posts
- **No manual steps** — Just paste and forget

## Local Setup (Windows/Mac/Linux)

### 1. Install Python 3.12+

https://www.python.org/downloads/

### 2. Clone/download this folder

```bash
cd ig-automation-cloud
```

### 3. Create virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set up credentials

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
```

### 6. Add thumbnail image

Place a `thumbnail.jpg` file in the project root. This image will be used as the thumbnail/cover for all posted reels.

### 7. Edit descriptions (optional)

Open `config.py` and change the 4 descriptions in `DESCRIPTIONS`:

```python
DESCRIPTIONS = [
    "Your description 1 🔥",
    "Your description 2 👀",
    "Your description 3 💯",
    "Your description 4 🎯",
]
```

### 8. Run

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

## Cloud Deployment

### Option 1: Railway (Recommended)

1. Create account at https://railway.app
2. Connect your GitHub (or upload this folder)
3. Set environment variables:
   - `IG_USERNAME`
   - `IG_PASSWORD`
4. Deploy — Railway will auto-detect Python and run `gunicorn app:app`

### Option 2: PythonAnywhere (Free)

1. Create account at https://pythonanywhere.com
2. Upload this folder via Web
3. Create new Python web app (3.12)
4. Point to `app.py` (WSGIHandler)
5. Set environment variables in Web tab
6. Reload

### Option 3: Heroku (Paid)

```bash
heroku login
heroku create your-app-name
heroku config:set IG_USERNAME=xxx IG_PASSWORD=xxx
git push heroku main
```

## How It Works

1. **You paste a reel URL** on the dashboard
2. **URL goes into SQLite queue** (stored locally or in cloud DB)
3. **Background worker** checks queue every 60 seconds
4. **Downloads the reel** using yt-dlp
5. **Picks random description** from your 4 options
6. **Posts to Instagram** via instagrapi
7. **Dashboard updates** with status (posted ✓, pending ⏳, failed ❌)

## Troubleshooting

### "Instagram blocked the download"
- Try the reel URL directly from the address bar
- Make sure it's a public reel
- Wait 5 minutes and retry (Instagram rate-limits)

### "Login failed"
- Double-check username/password
- Try logging in to Instagram manually first
- If using 2FA, disable it temporarily (or let the session cache)

### "No thumbnail found"
- Make sure `thumbnail.jpg` exists in the project root
- Use a JPEG or PNG image

### Videos not posting
- Check the queue — click on a failed item to see the error
- Make sure your Instagram account allows third-party apps
- Try one reel manually first to rule out account issues

## Customization

- **Change check interval**: Edit `WORKER_INTERVAL` in `config.py` (in seconds)
- **Add more descriptions**: Edit `DESCRIPTIONS` in `config.py`
- **Change thumbnail**: Replace `thumbnail.jpg` or update `DEFAULT_THUMBNAIL_PATH` in `config.py`

## Notes

- instagrapi (not official Meta API) — Instagram may occasionally flag automated logins
- Session file (`ig_session.json`) caches your login to reduce re-auth
- All data stored in SQLite locally (cloud services may need persistent storage)
- Worker runs in a background thread alongside Flask

Enjoy automation! 🚀
