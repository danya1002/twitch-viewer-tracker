import time
import sys
import os
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)

from src.twitch_client import TwitchClient
from src.youtube_client import YouTubeClient
from src.tracker import ViewerTracker


def load_config():
    json_path = os.path.join(BASE_DIR, "config.json")
    if os.path.isfile(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    py_path = os.path.join(BASE_DIR, "config.py")
    if os.path.isfile(py_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", py_path)
        cfg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfg)
        return {
            "TWITCH_CLIENT_ID": cfg.TWITCH_CLIENT_ID,
            "TWITCH_CLIENT_SECRET": cfg.TWITCH_CLIENT_SECRET,
            "TWITCH_CHANNEL": cfg.TWITCH_CHANNEL,
            "YOUTUBE_API_KEY": cfg.YOUTUBE_API_KEY,
            "YOUTUBE_VIDEO_ID": cfg.YOUTUBE_VIDEO_ID,
            "POLL_INTERVAL": getattr(cfg, "POLL_INTERVAL", 30),
        }
    return None


def validate_config(config):
    errors = []
    if not config.get("TWITCH_CLIENT_ID") or "your_" in config.get("TWITCH_CLIENT_ID", ""):
        errors.append("  - TWITCH_CLIENT_ID is empty")
    if not config.get("TWITCH_CLIENT_SECRET") or "your_" in config.get("TWITCH_CLIENT_SECRET", ""):
        errors.append("  - TWITCH_CLIENT_SECRET is empty")
    if not config.get("TWITCH_CHANNEL") or "your_" in config.get("TWITCH_CHANNEL", ""):
        errors.append("  - TWITCH_CHANNEL is empty (channel name)")
    if not config.get("YOUTUBE_API_KEY") or "your_" in config.get("YOUTUBE_API_KEY", ""):
        errors.append("  - YOUTUBE_API_KEY is empty")
    if not config.get("YOUTUBE_VIDEO_ID") or "your_" in config.get("YOUTUBE_VIDEO_ID", ""):
        errors.append("  - YOUTUBE_VIDEO_ID is empty (video ID)")
    interval = config.get("POLL_INTERVAL", 30)
    if not isinstance(interval, (int, float)) or interval < 5:
        errors.append("  - POLL_INTERVAL must be >= 5 seconds")
    return errors


def print_header():
    sep = "=" * 54
    print()
    print(f"  {sep}")
    print(f"     Twitch & YouTube - Viewer Tracker Bot")
    print(f"     Monitoring live viewers in real time")
    print(f"  {sep}")
    print()


def print_help():
    print("  To configure, create config.json next to this program:")
    print(f"  {os.path.join(BASE_DIR, 'config.json')}")
    print("  Template: config.example.json")
    print()


def wait_and_exit(code=0):
    print()
    try:
        input("  Press Enter to exit...")
    except EOFError:
        pass
    sys.exit(code)


def main():
    print_header()
    config = load_config()
    if config is None:
        print("  [ERROR] config.json not found!")
        print_help()
        wait_and_exit(1)

    errors = validate_config(config)
    if errors:
        print("  [ERROR] Configuration errors:")
        for e in errors:
            print(e)
        print_help()
        wait_and_exit(1)

    interval = config.get("POLL_INTERVAL", 30)
    print(f"  [OK] Configuration loaded")
    print(f"  [OK] Poll interval: {interval}s")
    print()
    print("  --- Connecting to APIs... ---")
    print()

    try:
        twitch = TwitchClient(config["TWITCH_CLIENT_ID"], config["TWITCH_CLIENT_SECRET"])
        youtube = YouTubeClient(config["YOUTUBE_API_KEY"])
        tracker = ViewerTracker(base_dir=BASE_DIR)
    except Exception as e:
        print(f"  [ERROR] Initialization failed: {e}")
        wait_and_exit(1)

    channel = config["TWITCH_CHANNEL"]
    video_id = config["YOUTUBE_VIDEO_ID"]
    print(f"  Twitch  channel: {channel}")
    print(f"  YouTube video:  {video_id}")
    print()
    print("  " + "=" * 54)
    print("  Monitoring started. Press Ctrl+C to stop.")
    print("  " + "=" * 54)
    print()

    while True:
        try:
            try:
                twitch_data = twitch.get_stream_info(channel)
                if twitch_data:
                    tracker.print_status("twitch", twitch_data)
                    tracker.log("twitch", twitch_data)
                else:
                    now = datetime.now().strftime("%H:%M:%S")
                    print(f"  [{now}] TWITCH    |    -    | Channel offline")
            except requests.exceptions.Timeout:
                now = datetime.now().strftime("%H:%M:%S")
                print(f"  [{now}] TWITCH    |  ERROR  | Connection timeout")
            except requests.exceptions.ConnectionError:
                now = datetime.now().strftime("%H:%M:%S")
                print(f"  [{now}] TWITCH    |  ERROR  | No internet connection")
            except requests.exceptions.HTTPError as e:
                now = datetime.now().strftime("%H:%M:%S")
                print(f"  [{now}] TWITCH    |  ERROR  | HTTP {e.response.status_code} - check API keys")

            try:
                youtube_data = youtube.get_live_stats(video_id)
                if youtube_data and youtube_data.get("is_live"):
                    tracker.print_status("youtube", youtube_data)
                    tracker.log("youtube", youtube_data)
                else:
                    now = datetime.now().strftime("%H:%M:%S")
                    print(f"  [{now}] YOUTUBE   |    -    | Stream not live")
            except requests.exceptions.Timeout:
                now = datetime.now().strftime("%H:%M:%S")
                print(f"  [{now}] YOUTUBE   |  ERROR  | Connection timeout")
            except requests.exceptions.ConnectionError:
                now = datetime.now().strftime("%H:%M:%S")
                print(f"  [{now}] YOUTUBE   |  ERROR  | No internet connection")
            except requests.exceptions.HTTPError as e:
                now = datetime.now().strftime("%H:%M:%S")
                status = e.response.status_code
                if status == 403:
                    msg = "403 - invalid YouTube API key"
                elif status == 404:
                    msg = "404 - video not found"
                else:
                    msg = f"HTTP {status}"
                print(f"  [{now}] YOUTUBE   |  ERROR  | {msg}")

            print()
            time.sleep(interval)

        except KeyboardInterrupt:
            print("  " + "=" * 54)
            print("  Stopped. Logs saved in logs/ folder.")
            print("  " + "=" * 54)
            wait_and_exit(0)
        except Exception as e:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"  [{now}] ERROR     | Unexpected error: {e}")
            print()
            time.sleep(interval)


if __name__ == "__main__":
    from datetime import datetime
    import requests
    main()
