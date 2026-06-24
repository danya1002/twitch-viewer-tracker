import requests


class YouTubeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_live_stats(self, video_id: str) -> dict | None:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "liveStreamingDetails,statistics,snippet",
                "id": video_id,
                "key": self.api_key,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if not items:
            return None
        item = items[0]
        live_details = item.get("liveStreamingDetails", {})
        statistics = item.get("statistics", {})
        snippet = item.get("snippet", {})
        return {
            "viewer_count": live_details.get("concurrentViewers"),
            "title": snippet.get("title", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "like_count": statistics.get("likeCount"),
            "is_live": "concurrentViewers" in live_details,
        }
