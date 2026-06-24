import time
import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)

sys.path.insert(0, BASE_DIR)


def load_config():
    json_path = os.path.join(BASE_DIR, "config.json")
    py_path = os.path.join(BASE_DIR, "config.py")
    if os.path.isfile(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    if os.path.isfile(py_path):
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


import importlib.util

from src.twitch_client import TwitchClient
from src.youtube_client import YouTubeClient
from src.tracker import ViewerTracker


def main():
    config = load_config()
    if config is None:
        print("Ошибка: создайте config.json или config.py на основе config.example.*")
        sys.exit(1)

    twitch = TwitchClient(config["TWITCH_CLIENT_ID"], config["TWITCH_CLIENT_SECRET"])
    youtube = YouTubeClient(config["YOUTUBE_API_KEY"])
    tracker = ViewerTracker(base_dir=BASE_DIR)
    interval = config.get("POLL_INTERVAL", 30)

    print(f"Запуск отслеживания (интервал: {interval}с)")
    print("Нажмите Ctrl+C для остановки\n")

    while True:
        try:
            twitch_data = twitch.get_stream_info(config["TWITCH_CHANNEL"])
            if twitch_data:
                tracker.print_status("Twitch", twitch_data)
                tracker.log("twitch", twitch_data)
            else:
                print("[Twitch] Стрим не найден или офлайн")

            youtube_data = youtube.get_live_stats(config["YOUTUBE_VIDEO_ID"])
            if youtube_data and youtube_data.get("is_live"):
                tracker.print_status("YouTube", youtube_data)
                tracker.log("youtube", youtube_data)
            else:
                print("[YouTube] Трансляция не найдена или не в эфире")

            print("-" * 40)
            time.sleep(interval)

        except KeyboardInterrupt:
            print("\nОстановка...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(interval)


if __name__ == "__main__":
    main()
