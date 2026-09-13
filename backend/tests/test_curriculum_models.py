"""Tests for curriculum/audio schema relationships and DB-level constraints.

These run against a disposable `hangugeo_test` Postgres database (created and
dropped by the `db_engine` fixture in conftest.py) - never the dev `hangugeo`
database, and never any curriculum content from data/verified/.
"""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.activity import AcceptedAnswer, Activity, ActivityOption
from app.models.audio import AudioAsset
from app.models.content_source import ContentBlock, ContentSource
from app.models.curriculum import GrammarPoint, Lesson, Unit, Vocabulary
from app.models.enums import ActivityType, CurationStatus, SourceType, VerificationStatus
from app.models.group import Group, GroupMember
from app.models.user import Role, User


def _make_unit(db_session, number="01") -> Unit:
    unit = Unit(number=number, title_ko="안녕하세요? 저는 안나예요", title_en="Hi, I'm Anna")
    db_session.add(unit)
    db_session.flush()
    return unit


def _make_lesson(db_session, unit: Unit) -> Lesson:
    lesson = Lesson(unit_id=unit.id, title="Lesson 1")
    db_session.add(lesson)
    db_session.flush()
    return lesson


def test_unit_number_unique_constraint(db_session):
    db_session.add(Unit(number="01"))
    db_session.flush()

    db_session.add(Unit(number="01"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_lesson_requires_valid_unit_foreign_key(db_session):
    db_session.add(Lesson(unit_id=uuid.uuid4(), title="Orphan lesson"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_unit_lesson_vocabulary_grammar_relationships(db_session):
    unit = _make_unit(db_session)
    lesson = _make_lesson(db_session, unit)

    vocab = Vocabulary(lesson_id=lesson.id, korean="안나", english="Anna")
    grammar = GrammarPoint(lesson_id=lesson.id, name_ko="이에요/예요", name_en="to be (copula)")
    db_session.add_all([vocab, grammar])
    db_session.flush()
    db_session.refresh(unit)
    db_session.refresh(lesson)

    assert unit.lessons[0].id == lesson.id
    assert lesson.unit.id == unit.id
    assert lesson.vocabulary[0].korean == "안나"
    assert lesson.grammar_points[0].name_ko == "이에요/예요"
    assert vocab.lesson.title == "Lesson 1"
    assert vocab.curation_status == CurationStatus.DRAFT


def test_vocabulary_source_block_provenance_link(db_session):
    source = ContentSource(
        source_type=SourceType.TEXTBOOK,
        title="Sejong Korean 1A Textbook",
        file_path="data/raw/685663101-Sejong-Korean-1A-Textbook-English (1).pdf",
    )
    db_session.add(source)
    db_session.flush()

    block = ContentBlock(
        source_id=source.id,
        page_number=40,
        block_index=0,
        language="ko",
        ocr_engine="tesseract",
        draft_text="안나",
        verification_status=VerificationStatus.APPROVED,
        verified_text="안나",
    )
    db_session.add(block)
    db_session.flush()

    unit = _make_unit(db_session)
    lesson = _make_lesson(db_session, unit)
    vocab = Vocabulary(
        lesson_id=lesson.id,
        korean="안나",
        english="Anna",
        source_block_id=block.id,
        curation_status=CurationStatus.HUMAN_APPROVED,
    )
    db_session.add(vocab)
    db_session.flush()

    assert source.blocks[0].id == block.id
    assert vocab.source_block_id == block.id


def test_content_source_block_cascade_delete(db_session):
    source = ContentSource(
        source_type=SourceType.WORKBOOK,
        title="Sejong Korean 1A Workbook",
        file_path="data/raw/638111818-Sejong-Korean-1A-workbook-1.pdf",
    )
    db_session.add(source)
    db_session.flush()
    db_session.add(ContentBlock(source_id=source.id, page_number=27, block_index=0, language="ko", draft_text="x"))
    db_session.flush()

    block_id = source.blocks[0].id
    db_session.delete(source)
    db_session.flush()

    assert db_session.get(ContentBlock, block_id) is None


def test_activity_options_and_accepted_answers_relationship(db_session):
    unit = _make_unit(db_session)
    lesson = _make_lesson(db_session, unit)
    activity = Activity(
        lesson_id=lesson.id,
        type=ActivityType.MULTIPLE_CHOICE,
        prompt="저는 안나___.",
        activity_metadata={"choices": ["이에요", "예요"]},
    )
    db_session.add(activity)
    db_session.flush()

    db_session.add(ActivityOption(activity_id=activity.id, text="이에요", is_correct=True))
    db_session.add(ActivityOption(activity_id=activity.id, text="예요", is_correct=False))
    db_session.add(AcceptedAnswer(activity_id=activity.id, answer_text="이에요"))
    db_session.flush()
    db_session.refresh(activity)

    assert len(activity.options) == 2
    assert activity.accepted_answers[0].answer_text == "이에요"
    assert activity.activity_metadata == {"choices": ["이에요", "예요"]}

    activity_id = activity.id
    db_session.delete(activity)
    db_session.flush()
    remaining_options = db_session.query(ActivityOption).filter_by(activity_id=activity_id).all()
    assert remaining_options == []


def test_audio_asset_unit_and_lesson_links(db_session):
    unit = _make_unit(db_session)
    lesson = _make_lesson(db_session, unit)

    audio = AudioAsset(
        original_filename="SJ_S_1A_01_1.mp3",
        source_type=SourceType.TEXTBOOK,
        source_archive="기본교재_1A_음원.zip",
        file_path="data/raw/audio/textbook/SJ_S_1A_01_1.mp3",
        checksum="e79e19beb6c75450cf69f7bb14c07a05",
        format="mp3",
        unit_id=unit.id,
        lesson_id=lesson.id,
    )
    db_session.add(audio)
    db_session.flush()
    db_session.refresh(audio)

    assert audio.unit.id == unit.id
    assert audio.lesson.id == lesson.id
    assert audio.verification_status == VerificationStatus.PENDING


def test_audio_asset_unit_lesson_are_optional(db_session):
    audio = AudioAsset(
        original_filename="SJ_W_1A_01_1.mp3",
        source_type=SourceType.WORKBOOK,
        file_path="data/raw/audio/workbook/SJ_W_1A_01_1.mp3",
        checksum="04307c1deb9be0e2356d6bbf8f8647ea",
        format="mp3",
    )
    db_session.add(audio)
    db_session.flush()

    assert audio.unit_id is None
    assert audio.lesson_id is None


def test_username_unique_constraint(db_session):
    db_session.add(User(username="admin1", hashed_password="x", role=Role.ADMIN))
    db_session.flush()

    db_session.add(User(username="admin1", hashed_password="y", role=Role.STUDENT))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_group_member_user_unique_constraint(db_session):
    group_a = Group(name="Group A")
    group_b = Group(name="Group B")
    student = User(username="student1", hashed_password="x", role=Role.STUDENT)
    db_session.add_all([group_a, group_b, student])
    db_session.flush()

    db_session.add(GroupMember(group_id=group_a.id, user_id=student.id))
    db_session.flush()

    db_session.add(GroupMember(group_id=group_b.id, user_id=student.id))
    with pytest.raises(IntegrityError):
        db_session.flush()
