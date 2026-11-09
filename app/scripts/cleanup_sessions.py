from datetime import datetime, timezone

from sqlalchemy import delete, or_

from app.database.database import SessionLocal
from app.models import LoginSession


def cleanup_sessions():
    now = datetime.now(timezone.utc)

    # Commit on success; automatically roll back on error
    with SessionLocal.begin() as db:
        result = db.execute(
            delete(LoginSession).where(
                or_(
                    LoginSession.expires_at <= now,
                    LoginSession.revoked_at.is_not(None),
                )
            )
        )
        deleted_count = result.rowcount

    print(f"Deleted {deleted_count} inactive sessions.")


if __name__ == "__main__":
    cleanup_sessions()