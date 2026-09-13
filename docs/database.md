# Database

PostgreSQL, managed via SQLAlchemy models + Alembic migrations
(`backend/app/models/`, `backend/alembic/`). 20 tables at the current head
migration (`1c885de625a8`).

## Auth & groups

- `users` - id (uuid), username (unique), hashed_password, role
  (`ADMIN`/`TEACHER`/`STUDENT` enum), created_at. No rows are seeded; no
  fake/placeholder users are created - see `backend/scripts/create_user.py`
  for manual account bootstrapping.
- `groups` - id (uuid), name (unique), `teacher_id` (nullable -> users.id -
  which teacher teaches this class/cohort), created_at.
- `group_members` - id (uuid), group_id -> groups, user_id -> users
  (unique), created_at. A Teacher's "assigned students" = the `User`s in
  `GroupMember` rows whose `Group.teacher_id` is that teacher.

## Curriculum (implemented, publishing gated by `CurationStatus`)

- `units`, `lessons` - curriculum structure. `Unit.number` is `"00"`..`"10"`.
  No lesson-locking concept exists anywhere in the schema or API - every
  unit is always visible to every student.
- `vocabulary`, `grammar_points` - candidate curriculum entries, each with a
  `source_block_id` FK back to the `ContentBlock` it was drafted from (OCR
  provenance) and a `curation_status` (`DRAFT` -> `NEEDS_REVIEW` ->
  `HUMAN_APPROVED` -> `CANONICAL`, or `-> REJECTED`) plus `proposed_by`/
  `reviewed_by`/`reviewed_at`. **Only `CANONICAL` rows are ever returned by
  the student API** - this is enforced in the repository query layer, not
  just convention. AI tooling may only ever create `DRAFT` rows; only a
  human operator (via `/api/v1/curation/*`, admin or teacher) may set
  `HUMAN_APPROVED`/`CANONICAL`.
- `activities`, `activity_options`, `accepted_answers` - data-driven
  exercises; `type` drives which frontend component renders it. Same
  `curation_status`/provenance columns as vocabulary/grammar. Note:
  `Activity` has no direct FK to a specific `Vocabulary`/`GrammarPoint` row -
  if per-word/per-grammar mastery tracking is wanted for an activity, the
  curator must set `vocabulary_id`/`grammar_point_id` inside its
  `metadata` JSONB.

This is distinct from `VerificationStatus` (`PENDING`/`APPROVED`/`EDITED`/
`REJECTED`/`NEEDS_REVIEW`), which stays on `content_blocks`/`audio_assets`
only and answers a different, earlier question: is the OCR text itself
correct? A `ContentBlock` can be `APPROVED` while the `Vocabulary` row later
drafted from it is still `DRAFT` - nothing is auto-promoted between the two
gates.

## Learning tracking (implemented)

- `attempts` - every submitted answer: user, activity, lesson, optional
  vocabulary/grammar_point + practice_mode, submitted/normalized answer,
  `is_correct`, score, hints_used, attempt_number, response_time_ms.
  Graded server-side only (`services/grading_service.py`) - never
  client-supplied correctness.
- `mistakes` - structured mistake categories derived from evaluation logic
  (vocabulary_recall, grammar_concept, spelling, spacing, sentence_order,
  comprehension, listening, pronunciation, recognition, application) -
  never randomly assigned, always tied to one `Attempt`.
- `vocabulary_progress` - per user + vocabulary + `PracticeMode`
  (recognition/recall_en_to_ko/recall_ko_to_en/listening/context) rollup -
  tracked separately per cognitive mode, not one blended score.
- `grammar_progress` - per user + grammar_point rollup.
- `progress` - per user + lesson rollup (what the Student Progress page
  renders); `streaks` - one row per user.

## Local setup

```bash
createdb hangugeo
# or: psql -c "CREATE DATABASE hangugeo;"
cd backend
cp .env.example .env   # adjust DATABASE_URL/credentials as needed
source .venv/bin/activate
alembic upgrade head
python scripts/create_user.py --username <you> --password <pw> --role ADMIN
```
