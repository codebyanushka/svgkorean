# Hangugeo (한국어)

A private, group-based Korean learning web app built around the Sejong
Korean 1A curriculum. See [`docs/architecture.md`](docs/architecture.md) for
the full design, [`docs/content-pipeline.md`](docs/content-pipeline.md) for
how source PDFs become verified curriculum data, and
[`docs/database.md`](docs/database.md) for the schema.

**Status: Phase 1 - project skeleton.** No curriculum content, login flow,
or curriculum database tables exist yet.

> The source textbook/workbook PDFs are copyrighted material (National
> Institute of Korean Language / King Sejong Institute Foundation). This
> project is for private, personal/group use only - not for redistribution.
> The app's own branding is original and does not use the textbook's name,
> logo, or cover art.

## Project layout

```
frontend/          React + Vite + TypeScript + Tailwind
backend/            FastAPI + SQLAlchemy + Alembic
content_pipeline/    PDF -> OCR -> verification -> DB import tooling
data/raw/             Original source PDFs (gitignored)
data/extracted/        Unverified OCR drafts (gitignored)
data/verified/           Human-approved canonical content (gitignored)
docs/                     Architecture, content pipeline, database docs
```

## Run the frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL
npm run dev
```

## Run the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DATABASE_URL, JWT_SECRET_KEY
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`

## PostgreSQL

```bash
createdb hangugeo
cd backend
alembic upgrade head   # once a migration exists, see docs/database.md
```
