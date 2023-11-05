import requests

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

import config


class SpotifyConnector:
    def __init__(self) -> None:
        self._token = util.prompt_for_user_token(
            username=config.username, 
            scope=config.scope,
            client_id=config.client_id,   
            client_secret=config.client_secret,     
            redirect_uri=config.redirect_uri,
            cache_path=config.cache_path
        )

    def get_features(self, track_id: str) -> dict:
        sp = spotipy.Spotify(auth=self._token)
        try:
            features = sp.audio_features([track_id])
            return features[0]
        except:
            return None

    def top_tracks(self) -> str:
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        try:
            response = requests.get(
                "https://api.spotify.com/v1/me/top/tracks",
                headers=headers,
                timeout = 5
            )
            return response.json()["items"]
        except:
            return None

    def recently_played(self) -> str:
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        try:
            response = requests.get(
                "https://api.spotify.com/v1/me/player/recently-played",
                headers=headers,
                timeout = 5
            )
            return response.json()["items"]
        except:
            return None

    def get_track_info(self, track_id: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        try:
            response = requests.get(
                f"https://api.spotify.com/v1/tracks/{track_id}",
                headers=headers,
                timeout = 5
            )
            return response.json()
        except:
            return None

    def get_artist_info(self, artist_id: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._token}",
        }
        try:
            response = requests.get(
                f"https://api.spotify.com/v1/artists/{artist_id}",
                headers=headers,
                timeout = 5
            )
            return response.json()
        except:
            return None
