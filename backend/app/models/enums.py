import enum


class SourceType(str, enum.Enum):
    TEXTBOOK = "TEXTBOOK"
    WORKBOOK = "WORKBOOK"
    VOCAB_GRAMMAR = "VOCAB_GRAMMAR"
    ADDITIONAL_ACTIVITIES = "ADDITIONAL_ACTIVITIES"


class VerificationStatus(str, enum.Enum):
    """OCR-text-level review outcome on a ContentBlock/AudioAsset - is the
    extracted text/mapping itself correct? See CurationStatus for the
    separate, later question of whether a curriculum row built from a block
    is approved for students to see."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class CurationStatus(str, enum.Enum):
    """Curriculum-row-level publishing gate for Vocabulary/GrammarPoint/
    Activity. Distinct from VerificationStatus: a ContentBlock can be
    APPROVED (text is correct) while the Vocabulary/Activity row proposed
    from it is still DRAFT (nobody has confirmed it belongs in the
    curriculum in this shape yet).

    DRAFT -> NEEDS_REVIEW -> HUMAN_APPROVED -> CANONICAL
                          -> REJECTED

    Only CANONICAL rows are ever served to students. AI-assisted tooling may
    create/propose DRAFT rows and may flag NEEDS_REVIEW, but only a human
    operator may set HUMAN_APPROVED or CANONICAL.
    """

    DRAFT = "DRAFT"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REJECTED = "REJECTED"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    CANONICAL = "CANONICAL"


class PracticeMode(str, enum.Enum):
    """A vocabulary/grammar item is tracked separately per cognitive mode -
    getting it right in one mode (e.g. multiple-choice recognition) does not
    imply mastery in another (e.g. unprompted Korean recall)."""

    RECOGNITION = "RECOGNITION"  # Korean shown, pick/confirm the meaning
    RECALL_EN_TO_KO = "RECALL_EN_TO_KO"  # English shown, produce Korean
    RECALL_KO_TO_EN = "RECALL_KO_TO_EN"  # Korean shown, produce English
    LISTENING = "LISTENING"  # audio shown, identify/produce the word
    CONTEXT = "CONTEXT"  # used correctly inside a sentence


class MasteryStatus(str, enum.Enum):
    NEEDS_REVIEW = "NEEDS_REVIEW"
    LEARNING = "LEARNING"
    MASTERED = "MASTERED"


class MistakeCategory(str, enum.Enum):
    """Structured mistake categories - always derived from evaluation logic
    in services/, never assigned arbitrarily."""

    VOCABULARY_RECALL = "VOCABULARY_RECALL"
    GRAMMAR_CONCEPT = "GRAMMAR_CONCEPT"
    SPELLING = "SPELLING"
    SPACING = "SPACING"
    SENTENCE_ORDER = "SENTENCE_ORDER"
    COMPREHENSION = "COMPREHENSION"
    LISTENING = "LISTENING"
    PRONUNCIATION = "PRONUNCIATION"
    RECOGNITION = "RECOGNITION"
    APPLICATION = "APPLICATION"


class ActivityType(str, enum.Enum):
    VOCABULARY_RECOGNITION = "vocabulary_recognition"
    VOCABULARY_RECALL = "vocabulary_recall"
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    KOREAN_TEXT_INPUT = "korean_text_input"
    SENTENCE_ORDERING = "sentence_ordering"
    MATCHING = "matching"
    TRANSLATION_TO_KOREAN = "translation_to_korean"
    LISTENING = "listening"
    READING = "reading"
    DIALOGUE_COMPLETION = "dialogue_completion"
    GRAMMAR_PRACTICE = "grammar_practice"
    WRITING = "writing"
    SPEAKING = "speaking"
