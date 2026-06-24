import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import (
        TWITCH_CLIENT_ID,
        TWITCH_CLIENT_SECRET,
        TWITCH_CHANNEL,
        YOUTUBE_API_KEY,
        YOUTUBE_VIDEO_ID,
        POLL_INTERVAL,
    )
except ImportError:
    print("Ошибка: создайте config.py на основе config.example.py")
    sys.exit(1)

from src.twitch_client import TwitchClient
from src.youtube_client import YouTubeClient
from src.tracker import ViewerTracker


def main():
    twitch = TwitchClient(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    youtube = YouTubeClient(YOUTUBE_API_KEY)
    tracker = ViewerTracker()

    print(f"Запуск отслеживания (интервал: {POLL_INTERVAL}с)")
    print("Нажмите Ctrl+C для остановки\n")

    while True:
        try:
            twitch_data = twitch.get_stream_info(TWITCH_CHANNEL)
            if twitch_data:
                tracker.print_status("Twitch", twitch_data)
                tracker.log("twitch", twitch_data)
            else:
                print("[Twitch] Стрим не найден или офлайн")

            youtube_data = youtube.get_live_stats(YOUTUBE_VIDEO_ID)
            if youtube_data and youtube_data.get("is_live"):
                tracker.print_status("YouTube", youtube_data)
                tracker.log("youtube", youtube_data)
            else:
                print("[YouTube] Трансляция не найдена или не в эфире")

            print("-" * 40)
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\nОстановка...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
