import csv
import os
from datetime import datetime


class Tracker:
    def __init__(self, base_dir):
        self.log_dir = os.path.join(base_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)

    def log(self, platform, data):
        path = os.path.join(self.log_dir, f"{platform}_{datetime.now():%Y-%m-%d}.csv")
        new = not os.path.isfile(path)
        row = {"time": datetime.now().isoformat()}
        for k, v in data.items():
            if v is not None:
                row[k] = str(v)
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=row.keys())
            if new:
                w.writeheader()
            w.writerow(row)

    def show(self, platform, data):
        now = datetime.now().strftime("%H:%M:%S")
        viewers = data.get("viewer_count", 0)
        if viewers:
            viewers = f"{viewers:>6,}"
        else:
            viewers = "    --"
        title = (data.get("title") or "")[:55]
        game = data.get("game") or data.get("channel") or ""
        print(f"  {now}  {platform.upper():>7} | {viewers}  | {title}")
