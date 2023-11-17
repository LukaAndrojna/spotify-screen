import mysql.connector

from models.mysqlconnector import (
    get_listening_minutes_daily,
    get_listening_minutes_weekly,
    get_top_artists_past_week,
    get_top_genres_past_week
)


def main() -> None:
    days = {
        0: "mon",
        1: "tue",
        2: "wed",
        3: "thu",
        4: "fri",
        5: "sat",
        6: "sun"
    }

    db = mysql.connector.connect(
        host="localhost",
        user="spotify",
        password="SpotifyGeslo123!",
        database="spotify"
    )

    weekly = get_listening_minutes_weekly(db)

    daily = get_listening_minutes_daily(db)
    daily_day = [days[row[0].weekday()] for row in daily]
    daily_minutes = [row[1] for row in daily]
    m = max(daily_minutes)
    daily_norm = [round(mins/m*18) for mins in daily_minutes]


    artists = [f"\n- {row[0]}" for row in get_top_artists_past_week(db)]
    genres = [f"\n- {row[0]}" for row in get_top_genres_past_week(db)]
    
    print(f"This weeks minutes: {weekly}\n"
        + "\n".join([f"{day}: {i*'*' + (18-i)*' '}" for day, i in zip(daily_day, daily_norm)])
        + f"\n\nTop artists:{''.join(artists)}"
        + f"\n\nTop genres:{''.join(genres)}")

if __name__ == "__main__":
    main()
