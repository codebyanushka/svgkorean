"""Server-side answer grading. Deterministic exact/case-insensitive matching
against `ActivityOption`/`AcceptedAnswer` rows - never client-supplied
correctness, never an LLM judgment call on curriculum-critical grading."""

import uuid

from app.models.activity import Activity
from app.models.enums import ActivityType, MistakeCategory, PracticeMode

_VOCABULARY_PRACTICE_MODES: dict[ActivityType, PracticeMode] = {
    ActivityType.VOCABULARY_RECOGNITION: PracticeMode.RECOGNITION,
    ActivityType.MULTIPLE_CHOICE: PracticeMode.RECOGNITION,
    ActivityType.MATCHING: PracticeMode.RECOGNITION,
    ActivityType.VOCABULARY_RECALL: PracticeMode.RECALL_EN_TO_KO,
    ActivityType.KOREAN_TEXT_INPUT: PracticeMode.RECALL_EN_TO_KO,
    ActivityType.TRANSLATION_TO_KOREAN: PracticeMode.RECALL_EN_TO_KO,
    ActivityType.LISTENING: PracticeMode.LISTENING,
    ActivityType.FILL_BLANK: PracticeMode.CONTEXT,
    ActivityType.SENTENCE_ORDERING: PracticeMode.CONTEXT,
    ActivityType.READING: PracticeMode.CONTEXT,
    ActivityType.DIALOGUE_COMPLETION: PracticeMode.CONTEXT,
    ActivityType.WRITING: PracticeMode.CONTEXT,
}

_MISTAKE_CATEGORY_BY_ACTIVITY_TYPE: dict[ActivityType, MistakeCategory] = {
    ActivityType.VOCABULARY_RECOGNITION: MistakeCategory.RECOGNITION,
    ActivityType.VOCABULARY_RECALL: MistakeCategory.VOCABULARY_RECALL,
    ActivityType.MULTIPLE_CHOICE: MistakeCategory.RECOGNITION,
    ActivityType.FILL_BLANK: MistakeCategory.COMPREHENSION,
    ActivityType.KOREAN_TEXT_INPUT: MistakeCategory.SPELLING,
    ActivityType.SENTENCE_ORDERING: MistakeCategory.SENTENCE_ORDER,
    ActivityType.MATCHING: MistakeCategory.RECOGNITION,
    ActivityType.TRANSLATION_TO_KOREAN: MistakeCategory.VOCABULARY_RECALL,
    ActivityType.LISTENING: MistakeCategory.LISTENING,
    ActivityType.READING: MistakeCategory.COMPREHENSION,
    ActivityType.DIALOGUE_COMPLETION: MistakeCategory.APPLICATION,
    ActivityType.GRAMMAR_PRACTICE: MistakeCategory.GRAMMAR_CONCEPT,
    ActivityType.WRITING: MistakeCategory.APPLICATION,
    ActivityType.SPEAKING: MistakeCategory.PRONUNCIATION,
}


class NotAutoGradableError(Exception):
    """Raised when an activity has neither options nor accepted answers to
    grade against (e.g. open-ended SPEAKING) - never fabricate a result."""


def grade_submission(activity: Activity, submitted_answer: str) -> bool:
    normalized = submitted_answer.strip()

    if activity.options:
        correct = {o.text.strip().lower() for o in activity.options if o.is_correct}
        return normalized.lower() in correct

    if activity.accepted_answers:
        accepted = {a.answer_text.strip().lower() for a in activity.accepted_answers}
        return normalized.lower() in accepted

    raise NotAutoGradableError(f"Activity {activity.id} has no options or accepted answers to grade against")


def resolve_practice_mode(activity: Activity) -> PracticeMode | None:
    return _VOCABULARY_PRACTICE_MODES.get(activity.type)


def resolve_mistake_category(activity: Activity) -> MistakeCategory:
    return _MISTAKE_CATEGORY_BY_ACTIVITY_TYPE.get(activity.type, MistakeCategory.APPLICATION)


def resolve_vocabulary_id(activity: Activity) -> uuid.UUID | None:
    raw = (activity.activity_metadata or {}).get("vocabulary_id")
    return uuid.UUID(raw) if raw else None


def resolve_grammar_point_id(activity: Activity) -> uuid.UUID | None:
    raw = (activity.activity_metadata or {}).get("grammar_point_id")
    return uuid.UUID(raw) if raw else None
