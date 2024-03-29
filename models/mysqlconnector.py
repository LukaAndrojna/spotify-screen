import sys
import datetime

import mysql.connector

from models.spotifyconnector import SpotifyConnector


def positive_hash(s: str) -> int:
    return hash(s) % ((sys.maxsize + 1) * 2)


def get_genre_id(genre: str) -> int:
    return positive_hash(genre)


def delete_tables(db: mysql.connector.connection_cext.CMySQLConnection) -> None:
    cursor = db.cursor()
    cursor.execute("DROP TABLE spotify.history,spotify.tracks,spotify.artists,spotify.genres,spotify.track_artist,spotify.artist_genre;")
    db.commit()


def create_tables(db: mysql.connector.connection_cext.CMySQLConnection) -> None:
    cursor = db.cursor()
    cursor.execute("CREATE TABLE spotify.history (id VARCHAR(255), track_id VARCHAR(255), played TIMESTAMP)")
    cursor.execute("CREATE TABLE spotify.tracks (track_id VARCHAR(255), title VARCHAR(255), duration INT)")
    cursor.execute("CREATE TABLE spotify.artists (artist_id VARCHAR(255), name VARCHAR(255))")
    cursor.execute("CREATE TABLE spotify.genres (genre_id VARCHAR(255), genre VARCHAR(255))")
    cursor.execute("CREATE TABLE spotify.track_artist (id VARCHAR(255), track_id VARCHAR(255), artist_id VARCHAR(255))")
    cursor.execute("CREATE TABLE spotify.artist_genre (id VARCHAR(255), artist_id VARCHAR(255), genre_id VARCHAR(255))")
    db.commit()


def get_last_track(db: mysql.connector.connection_cext.CMySQLConnection) -> list:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM history ORDER BY played DESC LIMIT 1")
    return cursor.fetchall()


def get_last_played(db: mysql.connector.connection_cext.CMySQLConnection) -> datetime.datetime:
    res = get_last_track(db)
    if len(res) == 0:
        return None
    return res[0][2]


def insert_history(db: mysql.connector.connection_cext.CMySQLConnection, rt_list: list) -> None:
    cursor = db.cursor()
    last_played = get_last_played(db)
    rows = list()
    for entry in rt_list:
        played = entry["played_at"].replace("T", " ").split(".")[0]
        
        if last_played is not None and datetime.datetime.strptime(played, "%Y-%m-%d %H:%M:%S") <= last_played:
            continue
        
        track_id = entry["track_id"]
        id = positive_hash(played)
        rows.append(f'("{id}","{track_id}","{played}")')
    if not rows:
        return
    rows = ",\n".join(rows)
    cursor.execute(f"INSERT INTO spotify.history (id, track_id, played) VALUES\n{rows};")
    db.commit()


def insert_tracks(sc: SpotifyConnector, db: mysql.connector.connection_cext.CMySQLConnection, rt_list: list) -> None:
    cursor = db.cursor()
    tracks = list()
    for entry in rt_list:
        track_id = entry["track_id"]
        tracks.append(f'"{track_id}"')
    tracks = ",".join(tracks)
    cursor.execute(f"SELECT track_id FROM spotify.tracks WHERE track_id IN ({tracks});")
    tracks = [track_id[0] for track_id in cursor.fetchall()]

    rows = list()
    for entry in rt_list:
        track_id = entry["track_id"]
        if track_id in tracks:
            continue
        title = entry["title"]
        duration = entry["duration"]
        rows.append(f'("{track_id}","{title}",{duration})')

        artists = entry["artists"]
        insert_artists(sc, db, artists)

        insert_track_artists(db, track_id, artists)

    if len(rows) == 0:
        return
    rows = ",\n".join(rows)
    cursor.execute(f"INSERT INTO spotify.tracks (track_id, title, duration) VALUES\n{rows};")
    db.commit()


def insert_artists(sc: SpotifyConnector, db: mysql.connector.connection_cext.CMySQLConnection, artists: list) -> None:
    cursor = db.cursor()
    artists_query = ",".join([f'"{artist}"' for artist in artists])
    cursor.execute(f"SELECT artist_id FROM spotify.artists WHERE artist_id IN ({artists_query});")
    artists_in_db = [artist_id[0] for artist_id in cursor.fetchall()]

    rows = list()

    for artist in artists:
        if artist in artists_in_db:
            continue
        resp = sc.get_artist_info(artist)
        name = resp["name"]
        rows.append(f'("{artist}","{name}")')

        genres = resp["genres"]
        insert_genres(db, genres)

        insert_artist_genres(db, artist, genres)

    if len(rows) == 0:
        return
    rows = ",\n".join(rows)
    cursor.execute(f"INSERT INTO spotify.artists (artist_id, name) VALUES\n{rows};")
    db.commit()


def insert_genres(db: mysql.connector.connection_cext.CMySQLConnection, genres: list) -> None:
    if not genres:
        return

    cursor = db.cursor()
    genres_query = ",".join([f'"{genre}"' for genre in genres])
    cursor.execute(f"SELECT genre FROM spotify.genres WHERE genre IN ({genres_query});")
    genres_in_db = [genre[0] for genre in cursor.fetchall()]

    rows = list()
    for genre in genres:
        if genre in genres_in_db:
            continue
        genre_id = get_genre_id(genre)
        rows.append(f'("{genre_id}","{genre}")')
    if len(rows) == 0:
        return
    rows = ",\n".join(rows)
    cursor.execute(f"INSERT INTO spotify.genres (genre_id, genre) VALUES\n{rows};")
    db.commit()


def insert_track_artists(db: mysql.connector.connection_cext.CMySQLConnection, track_id: str, artists: list) -> None:
    cursor = db.cursor()
    rows = list()
    for artist in artists:
        connection_id = positive_hash(track_id+artist)
        rows.append(f'("{connection_id}","{track_id}","{artist}")')

    if len(rows) == 0:
        return
    rows = ",\n".join(rows)
    cursor.execute(f"INSERT INTO spotify.track_artist (id, track_id, artist_id) VALUES\n{rows};")
    db.commit()


def insert_artist_genres(db: mysql.connector.connection_cext.CMySQLConnection, artist_id: str, genres: list) -> None:
    cursor = db.cursor()
    rows = list()
    for genre in genres:
        connection_id = positive_hash(artist_id+genre)
        genre_id = get_genre_id(genre)
        rows.append(f'("{connection_id}","{artist_id}","{genre_id}")')

    if len(rows) == 0:
        return
    rows = ",\n".join(rows)
    cursor.execute(f"INSERT INTO spotify.artist_genre (id, artist_id, genre_id) VALUES\n{rows};")
    db.commit()


def get_listening_minutes_daily(db: mysql.connector.connection_cext.CMySQLConnection) -> list:
    cursor = db.cursor()
    query = f"""
        SELECT
            DATE(played) as date,
            ROUND(SUM(duration)/60000) as minutes
        FROM
            history
        JOIN
            tracks
        ON
            history.track_id = tracks.track_id
            AND played > TIMESTAMP('{datetime.date.today() - datetime.timedelta(days=7)}')
        GROUP BY 1
        ORDER BY 1"""
    cursor.execute(query)
    return [(row[0], int(row[1])) for row in cursor.fetchall()]


def get_listening_minutes_weekly(db: mysql.connector.connection_cext.CMySQLConnection) -> int:
    return sum([row[1] for row in get_listening_minutes_daily(db)])


def get_top_artists_past_week(db: mysql.connector.connection_cext.CMySQLConnection) -> list:
    cursor = db.cursor()
    query = f"""
        SELECT
            artists.name,
            COUNT(1)
        FROM
            history
        JOIN
            track_artist
        ON
            history.track_id = track_artist.track_id
            AND played > TIMESTAMP('{datetime.date.today() - datetime.timedelta(days=7)}')
        JOIN
            artists
        ON
            track_artist.artist_id = artists.artist_id
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 5"""
    cursor.execute(query)
    return cursor.fetchall()


def get_top_genres_past_week(db: mysql.connector.connection_cext.CMySQLConnection) -> list:
    cursor = db.cursor()
    query = f"""
        SELECT
            genres.genre,
            COUNT(1)
        FROM
            history
        JOIN
            track_artist
        ON
            history.track_id = track_artist.track_id
            AND played > TIMESTAMP('{datetime.date.today() - datetime.timedelta(days=7)}')
        JOIN
            artist_genre
        ON
            track_artist.artist_id = artist_genre.artist_id
        JOIN
            genres
        ON
            artist_genre.genre_id = genres.genre_id
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 5"""
    cursor.execute(query)
    return cursor.fetchall()
