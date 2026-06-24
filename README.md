# Twitch & YouTube Viewer Tracker Bot

Monitors live viewer counts from Twitch and YouTube in real time.

## Quick Start (EXE)

1. Download `ViewerTracker.exe` and `config.example.json` from [Releases](https://github.com/danya1002/twitch-viewer-tracker/releases)
2. Rename `config.example.json` to `config.json` and edit it
3. Run `ViewerTracker.exe`

## Getting API Keys

### Twitch
1. Go to https://dev.twitch.tv/console/apps and log in
2. Click "Register Your Application"
3. Name: anything (e.g. "Viewer Tracker")
4. OAuth Redirect URL: `http://localhost`
5. Category: "Application Integration"
6. Copy the **Client ID** and click "New Secret" for **Client Secret**

### YouTube
1. Go to https://console.cloud.google.com/
2. Create a project (or select existing)
3. Go to APIs & Services > Library
4. Search for "YouTube Data API v3" and enable it
5. Go to APIs & Services > Credentials
6. Click "Create Credentials" > "API Key"
7. Copy the key

## config.json

```json
{
    "TWITCH_CLIENT_ID": "your_client_id",
    "TWITCH_CLIENT_SECRET": "your_client_secret",
    "TWITCH_CHANNEL": "forsen",
    "YOUTUBE_API_KEY": "your_api_key",
    "YOUTUBE_VIDEO_ID": "dQw4w9WgXcQ",
    "POLL_INTERVAL": 30
}
```

- `TWITCH_CHANNEL` — Twitch channel name (lowercase, no `@`)
- `YOUTUBE_VIDEO_ID` — the `v=` parameter from a YouTube live URL
- `POLL_INTERVAL` — seconds between checks (min 5)

## Run from Source

```bash
pip install -r requirements.txt
python src/main.py
```

## Project Structure

```
├── src/
│   ├── main.py           # entry point
│   ├── twitch_client.py  # Twitch API
│   ├── youtube_client.py # YouTube API
│   ├── tracker.py        # CSV logging
├── config.example.json   # config template
├── ViewerTracker.exe     # standalone exe
├── build_exe.bat         # rebuild exe
└── requirements.txt      # pip dependencies
```
