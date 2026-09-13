# Architecture

## Overview

Hangugeo is a private, group-based Korean learning platform built around the
Sejong Korean 1A curriculum (textbook, workbook, vocab & grammar reference,
additional activities). Source PDFs are the sole source of truth for
curriculum content; the application determines *how* a learner interacts with
that content, never *what* the content says.

The instructor also provided the original textbook and workbook audio
recordings (`data/raw/audio/`). These are canonical source assets in the same
sense as the PDFs: original files and filenames are preserved, and they are
never replaced with generated TTS where a real recording exists.

```
data/raw (PDF + audio) -> content_pipeline (render -> OCR -> reconstruct ->
compare -> verify; audio mapped to unit/page during verification) ->
data/verified (canonical JSON, references audio files by relative path) ->
Postgres -> FastAPI -> React
```

## Components

- **frontend/**: React + Vite + TypeScript + Tailwind + React Router. Renders
  activities generically based on `type` - no lesson content is ever
  hardcoded into a component.
- **backend/**: FastAPI, layered as `api -> services -> repositories ->
  models`. Business logic (answer evaluation, progress, spaced review,
  analytics) lives in `services/`, never in route handlers.
- **content_pipeline/**: standalone Python tooling that turns scanned PDFs
  into verified, database-ready JSON. Runs independently of the web app.
- **data/**: `raw/` (original PDFs and audio), `extracted/` (unverified OCR
  drafts), `verified/` (human-approved canonical content - the only source
  used to seed the database).
- **data/raw/audio/**: instructor-provided original recordings.
  `textbook/` holds the 40 SJ_S_1A_* tracks (extracted from the instructor's
  zip, original zip kept in `textbook/archive/`); `workbook/` holds the 66
  SJ_W_1A_* tracks (project owner extracted the zip themselves and didn't
  retain the archive - see `docs/content-pipeline.md`). Audio is mapped to
  unit/lesson/page only through the same human-verification step as OCR
  text - never inferred from filename patterns alone without visual/
  listening confirmation.

## Auth & RBAC

JWT (HS256, python-jose) auth with three roles: `ADMIN`, `TEACHER`,
`STUDENT`. No public signup - accounts are created by an operator via
`backend/scripts/create_user.py`. `POST /api/v1/auth/login` (form-encoded,
`OAuth2PasswordRequestForm`) verifies the password (passlib/bcrypt) and
issues a token; `GET /api/v1/auth/me` resolves the current user from it.
`backend/app/api/deps.py` provides `get_current_user()` plus role-guard
dependencies (`require_admin`, `require_teacher`, `require_student`,
`require_staff` = admin+teacher) used to scope every `/api/v1/student/*`,
`/api/v1/teacher/*`, and `/api/v1/curation/*` route. A Teacher's "assigned
students" resolve through `Group.teacher_id` -> `GroupMember` -> `User`
(see `docs/database.md`) - teacher routes 403 on students outside their
groups. There is no lesson locking: all units are always visible to every
student.

## Current status

Backend: curriculum schema (`Unit`/`Lesson`/`Vocabulary`/`GrammarPoint`/
`Activity`, gated by `CurationStatus`), learning-tracking schema
(`Attempt`/`Mistake`/`Progress`/`VocabularyProgress`/`GrammarProgress`/
`Streak`), auth/RBAC, and a REST API skeleton
(`/api/v1/student/*`, `/api/v1/teacher/*`, `/api/v1/curation/*`) are all
implemented and tested (see `docs/database.md`). Layering is
`api/v1/endpoints -> services -> repositories -> models`, matching the plan
above. Server-side grading (`services/grading_service.py`) is exact/
case-insensitive matching against real `ActivityOption`/`AcceptedAnswer`
rows - never client-supplied correctness, and activities with no gradable
answer set (e.g. open-ended `speaking`) return HTTP 422 rather than a
fabricated result.

Frontend: an `AuthProvider`/`useAuth()` context, `ProtectedRoute` (redirects
to `/login` when unauthenticated, redirects home on a role mismatch), and
separate `StudentLayout`/`TeacherLayout` shells matching the nav structure
above are implemented and wired to the real backend API (no mocked data).
Most Student/Teacher pages beyond Home/Units/Students are still placeholders
awaiting the dashboards phase.

**Not yet implemented**: no curriculum content has been curated into
`Vocabulary`/`GrammarPoint`/`Activity` yet (all three tables are empty -
Unit 1's OCR-verified `ContentBlock` rows are the editorial candidates, not
published curriculum). Only `CANONICAL` rows are ever served to students,
and nothing may become `CANONICAL` without an explicit human review step
through `/api/v1/curation/*` - AI tooling may only create `DRAFT` rows.
Audio-to-lesson mapping, playback, and speaking/pronunciation features are
also not implemented.
