import requests
import time


class TwitchClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expires_at = 0
        self._session = requests.Session()

    def _get_token(self) -> str:
        if time.time() < self._token_expires_at:
            return self._token
        resp = self._session.post(
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
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"] - 60
        return self._token

    def get_stream_info(self, channel: str) -> dict | None:
        token = self._get_token()
        resp = self._session.get(
            "https://api.twitch.tv/helix/streams",
            headers={
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {token}",
            },
            params={"user_login": channel.lower()},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        streams = data.get("data", [])
        if not streams:
            return None
        stream = streams[0]
        return {
            "viewer_count": stream["viewer_count"],
            "title": stream["title"],
            "game_name": stream.get("game_name", "N/A"),
            "started_at": stream["started_at"],
            "is_live": True,
        }
