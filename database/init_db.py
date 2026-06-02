from pathlib import Path

from modules.application_tracker import ApplicationTracker


def main() -> None:
    db_path = Path(__file__).resolve().parent / "applications.db"
    tracker = ApplicationTracker(str(db_path))
    print(f"Database initialized at {db_path}")


if __name__ == "__main__":
    main()
