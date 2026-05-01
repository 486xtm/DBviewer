"""Fetch the SQLite Chinook database beside ``development.ini``."""

from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "Chinook_Sqlite.sqlite"
URL = (
    "https://github.com/lerocha/chinook-database/raw/"
    "refs/heads/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
)


def main() -> None:
    if DEST.exists():
        print(f"Already exists: {DEST}")
        return
    print(f"Downloading {URL}\n -> {DEST}")
    urllib.request.urlretrieve(URL, DEST)
    print("Done.")


if __name__ == "__main__":
    main()
