"""Bootstrap script for creating a user account.

There is no public HTTP admin-user-creation endpoint - this script is the
only way to create TEACHER accounts by hand. STUDENT accounts are normally
created directly by a teacher via POST /api/v1/teacher/students (see the
"Add Student" flow in the teacher dashboard). Run manually, never called by
the app itself.

Usage (from backend/, with .venv active):
    python scripts/create_user.py --username teacher1 --password <pw> --role TEACHER
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
