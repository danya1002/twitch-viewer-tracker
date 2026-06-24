import sys
import os
import json
import time
import requests
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.twitch_client import TwitchClient
from src.youtube_client import YouTubeClient
from src.tracker import Tracker


CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LINKS = {
    "twitch_app": "https://dev.twitch.tv/console/apps",
    "twitch_guide": "https://dev.twitch.tv/docs/authentication",
    "youtube_key": "https://console.cloud.google.com/apis/credentials",
    "youtube_guide": "https://developers.google.com/youtube/v3/getting-started",
}


def hr(title=""):
    print("  " + "=" * 56)
    if title:
        print(f"  {title}")
        print("  " + "=" * 56)


def load_config():
    if not os.path.isfile(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def validate(cfg):
    errors = []
    fields = [
        ("TWITCH_CLIENT_ID", "Twitch Client ID"),
        ("TWITCH_CLIENT_SECRET", "Twitch Client Secret"),
        ("TWITCH_CHANNEL", "Twitch channel name"),
        ("YOUTUBE_API_KEY", "YouTube API Key"),
        ("YOUTUBE_VIDEO_ID", "YouTube Video ID"),
    ]
    for key, label in fields:
        val = cfg.get(key, "")
        if not val or "your_" in val:
            errors.append(f"    {label} is empty or has placeholder value")
    interval = cfg.get("POLL_INTERVAL", 30)
    if not isinstance(interval, (int, float)) or interval < 5:
        errors.append(f"    POLL_INTERVAL must be >= 5 (got {interval})")
    return errors


def show_help():
    hr(" WELCOME TO VIEWER TRACKER BOT")
    print()
    print("  This program tracks live viewer counts from Twitch and YouTube.")
    print()
    hr(" SETUP INSTRUCTIONS")
    print()
    print("  1. Copy config.example.json -> config.json")
    print("  2. Open config.json and fill in your API credentials:")
    print()
    print("  --- Twitch ---")
    print(f"  Go to: {LINKS['twitch_app']}")
    print("  - Create an application (any name)")
    print("  - Copy the Client ID and Client Secret")
    print("  - Put them in config.json")
    print()
    print("  --- YouTube ---")
    print(f"  Go to: {LINKS['youtube_key']}")
    print("  - Create an API key (or use existing)")
    print("  - Make sure YouTube Data API v3 is enabled")
    print("  - Put the key in config.json")
    print()
    print("  3. Set the channel name and video ID you want to track")
    print("  4. Run the program again")
    print()
    hr()


def show_status(platform, data):
    now = datetime.now().strftime("%H:%M:%S")
    if data is None:
        print(f"  {now}  {platform:>7} |  OFFLINE  |")
        return
    viewers = data.get("viewer_count", 0)
    if viewers:
        viewers_str = f"{viewers:>6,}"
    else:
        viewers_str = "    --"
    title = (data.get("title") or "")[:55]
    print(f"  {now}  {platform:>7} | {viewers_str}  | {title}")


def main():
    show_help()
    cfg = load_config()
    if cfg is None:
        print("  [X] config.json not found!")
        print(f"  [i] Place it at: {CONFIG_PATH}")
        print()
        input("  Press Enter to exit...")
        sys.exit(1)

    errs = validate(cfg)
    if errs:
        hr(" CONFIGURATION ERRORS")
        for e in errs:
            print(e)
        print()
        print("  Fix the errors above, then run again.")
        print()
        input("  Press Enter to exit...")
        sys.exit(1)

    interval = int(cfg.get("POLL_INTERVAL", 30))
    channel = cfg["TWITCH_CHANNEL"]
    video_id = cfg["YOUTUBE_VIDEO_ID"]

    hr(" INITIALIZING")
    print(f"  Twitch channel : {channel}")
    print(f"  YouTube video  : {video_id}")
    print(f"  Poll interval  : {interval}s")
    print()

    try:
        twitch = TwitchClient(cfg["TWITCH_CLIENT_ID"], cfg["TWITCH_CLIENT_SECRET"])
        youtube = YouTubeClient(cfg["YOUTUBE_API_KEY"])
        tracker = Tracker(BASE_DIR)
    except Exception as e:
        print(f"  [X] Init error: {e}")
        input("  Press Enter to exit...")
        sys.exit(1)

    hr(" MONITORING")
    print("  Ctrl+C to stop")
    print()

    while True:
        try:
            tw_data = None
            try:
                tw_data = twitch.get_stream(channel)
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code
                if code == 401:
                    print(f"  {datetime.now():%H:%M:%S}  TWITCH | AUTH ERROR - check Client ID / Secret")
                elif code == 429:
                    print(f"  {datetime.now():%H:%M:%S}  TWITCH | RATE LIMITED - slow down")
                else:
                    print(f"  {datetime.now():%H:%M:%S}  TWITCH | HTTP {code}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print(f"  {datetime.now():%H:%M:%S}  TWITCH | NETWORK ERROR")
            except Exception as e:
                print(f"  {datetime.now():%H:%M:%S}  TWITCH | ERROR: {e}")
            else:
                show_status("TWITCH", tw_data)
                if tw_data:
                    tracker.log("twitch", tw_data)

            yt_data = None
            try:
                yt_data = youtube.get_stream(video_id)
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code
                if code == 403:
                    print(f"  {datetime.now():%H:%M:%S} YOUTUBE | KEY ERROR - check API key / enable YouTube Data API")
                elif code == 404:
                    print(f"  {datetime.now():%H:%M:%S} YOUTUBE | NOT FOUND - check video ID")
                else:
                    print(f"  {datetime.now():%H:%M:%S} YOUTUBE | HTTP {code}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print(f"  {datetime.now():%H:%M:%S} YOUTUBE | NETWORK ERROR")
            except Exception as e:
                print(f"  {datetime.now():%H:%M:%S} YOUTUBE | ERROR: {e}")
            else:
                show_status("YOUTUBE", yt_data)
                if yt_data:
                    tracker.log("youtube", yt_data)

            print()
            time.sleep(interval)

        except KeyboardInterrupt:
            print()
            hr(" STOPPED")
            print("  Logs saved in the logs/ folder.")
            print()
            input("  Press Enter to exit...")
            sys.exit(0)


if __name__ == "__main__":
    main()
