"""Bootstrap script for creating a user account.

There is no public signup and no HTTP user-creation endpoint yet (admin user
management is a separate, later API - see todo #4). This script is the only
way to create the first ADMIN account and any TEACHER/STUDENT accounts an
operator wants to add by hand. Run manually, never called by the app itself.

Usage (from backend/, with .venv active):
    python scripts/create_user.py --username admin --password <pw> --role ADMIN
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.repositories import user_repository  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a user account.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--role", required=True, choices=[r.value for r in Role])
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if user_repository.get_by_username(db, args.username) is not None:
            print(f"User '{args.username}' already exists - not creating a duplicate.")
            return
        user = User(
            username=args.username,
            hashed_password=hash_password(args.password),
            role=Role(args.role),
        )
        db.add(user)
        db.commit()
        print(f"Created user '{args.username}' with role {args.role}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
