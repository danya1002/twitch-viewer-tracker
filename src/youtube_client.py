import requests


class YouTubeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()

    def get_stream(self, video_id):
        resp = self.session.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "liveStreamingDetails,snippet",
                "id": video_id,
                "key": self.api_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            return None
        item = items[0]
        live = item.get("liveStreamingDetails", {})
        snippet = item.get("snippet", {})
        if "concurrentViewers" not in live:
            return None
        return {
            "viewer_count": int(live["concurrentViewers"]),
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "is_live": True,
        }
