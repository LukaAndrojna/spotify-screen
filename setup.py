import argparse

import mariadb

from models.mysqlconnector import create_tables, delete_tables


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up script settings.")
    parser.add_argument("--create", dest="create", action="store_const",
                        const=True, default=False,
                        help=f"Create tables.")
    parser.add_argument("--delete", dest="delete", action="store_const",
                        const=True, default=False,
                        help=f"Delete tables.")

    db = mariadb.connect(
        host="localhost",
        user="spotify",
        password="SpotifyGeslo123!",
        database="spotify"
    )

    args = parser.parse_args()

    if args.delete:
        delete_tables(db)
    
    if args.create:
        create_tables(db)


if __name__ == "__main__":
    main()
