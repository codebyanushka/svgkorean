#!/bin/sh
set -e

# Wait for Postgres to accept connections before migrating (db healthcheck in
# docker-compose already gates this, but retry here too in case of races).
python - <<'EOF'
import time
import sqlalchemy as sa
from app.core.config import get_settings

settings = get_settings()
for attempt in range(30):
    try:
        sa.create_engine(settings.database_url).connect().close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Database never became reachable")
EOF

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
