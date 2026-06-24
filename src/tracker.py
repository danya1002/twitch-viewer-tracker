import csv
import os
from datetime import datetime


class ViewerTracker:
    def __init__(self, base_dir: str = "."):
        self.log_dir = os.path.join(base_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)

    def _csv_path(self, platform: str) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"{platform}_{date_str}.csv")

    def log(self, platform: str, data: dict):
        filepath = self._csv_path(platform)
        is_new = not os.path.isfile(filepath)
        timestamp = datetime.now().isoformat()
        row = {"timestamp": timestamp, **data}
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if is_new:
                writer.writeheader()
            writer.writerow(row)

    def print_status(self, platform: str, data: dict):
        viewers = data.get("viewer_count", "N/A")
        title = data.get("title", "N/A")
        print(f"[{platform}] Viewers: {viewers} | Title: {title}")
