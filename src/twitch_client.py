import requests
import time
import json


class TwitchClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expires_at = 0
        self.session = requests.Session()

    def _refresh_token(self):
        resp = self.session.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access_token"]
        self.token_expires_at = time.time() + data["expires_in"] - 60

    def get_stream(self, channel):
        if time.time() >= self.token_expires_at:
            self._refresh_token()
        resp = self.session.get(
            "https://api.twitch.tv/helix/streams",
            headers={
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {self.token}",
            },
            params={"user_login": channel.lower()},
            timeout=15,
        )
        if resp.status_code == 401:
            self._refresh_token()
            resp = self.session.get(
                "https://api.twitch.tv/helix/streams",
                headers={
                    "Client-ID": self.client_id,
                    "Authorization": f"Bearer {self.token}",
                },
                params={"user_login": channel.lower()},
                timeout=15,
            )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            return None
        s = data[0]
        return {
            "viewer_count": s["viewer_count"],
            "title": s["title"],
            "game": s.get("game_name", ""),
            "started_at": s["started_at"],
            "is_live": True,
        }
