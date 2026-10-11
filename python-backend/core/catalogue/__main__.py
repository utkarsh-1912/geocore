# Author: Utkarsh Gupta
# License: GPL v3
"""
    python -m core.catalogue            # validate the catalogue and write the desktop navigation copy
    python -m core.catalogue --check    # exit 1 if the navigation copy is out of date
"""
import sys

from core.catalogue import APP_NAVIGATION_PATH, load_catalogue, navigation_json


def main(argv):
    load_catalogue()  # raises CatalogueError on any structural problem
    content = navigation_json()
    try:
        with open(APP_NAVIGATION_PATH, encoding="utf-8") as f:
            current = f.read()
    except FileNotFoundError:
        current = None
    if "--check" in argv:
        if current != content:
            print(f"{APP_NAVIGATION_PATH} is out of date: run python -m core.catalogue")
            return 1
        print("catalogue navigation is up to date")
        return 0
    with open(APP_NAVIGATION_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"wrote {APP_NAVIGATION_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
