import mysql.connector

from models.spotifyconnector import SpotifyConnector
from models.mysqlconnector import insert_history, insert_tracks


def main() -> None:
    sc = SpotifyConnector()
    db = mysql.connector.connect(
        host="localhost",
        user="spotify",
        password="SpotifyGeslo123!",
        database="spotify"
    )

    recent_tracks = sc.recently_played()
    rt_list = list()
    for track in recent_tracks:
        rt_list.append({
            "title": track["track"]["name"],
            "artists": [artist["id"] for artist in track["track"]["artists"]],
            "duration": track["track"]["duration_ms"],
            "played_at":track["played_at"],
            "track_id": track["track"]["id"],
        })

    insert_history(db, rt_list)
    insert_tracks(sc, db, rt_list)


if __name__ == "__main__":
    main()
