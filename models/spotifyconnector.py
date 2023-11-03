import requests

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyConnector:
    def __init__(self) -> None:
        username = "ForgottenLux"
        client_id = ""
        client_secret = ""
        redirect_uri = "http://localhost:7777/callback"

        self._token_top = util.prompt_for_user_token(
            username=username, 
            scope="user-top-read", 
            client_id=client_id,   
            client_secret=client_secret,     
            redirect_uri=redirect_uri
        )

        self._token_played = util.prompt_for_user_token(
            username=username, 
            scope="user-read-recently-played", 
            client_id=client_id,   
            client_secret=client_secret,     
            redirect_uri=redirect_uri
        )

    def get_features(self, track_id: str) -> dict:
        sp = spotipy.Spotify(auth=self._token_played)
        try:
            features = sp.audio_features([track_id])
            return features[0]
        except:
            return None

    def top_tracks(self) -> str:
        headers = {
            "Authorization": f"Bearer {self._token_top}",
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
            "Authorization": f"Bearer {self._token_played}",
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
            "Authorization": f"Bearer {self._token_played}",
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
            "Authorization": f"Bearer {self._token_played}",
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
