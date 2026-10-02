from app.models.intelligence import (
    InterviewIntelligence,
    KeyTopic,
    LikelyQuestion,
    PreparationPriority,
    StudyPlanItem,
)


def test_interview_intelligence_preserves_grounding() -> None:
    source_url = "https://example.com/interview"

    intelligence = InterviewIntelligence(
        key_topics=[
            KeyTopic(
                topic="System design",
                reason="Appears in interview evidence.",
                evidence_urls=[source_url],
            ),
        ],
        likely_questions=[
            LikelyQuestion(
                question="How would you design a scalable API?",
                rationale="The evidence emphasizes system design.",
                evidence_urls=[source_url],
            ),
        ],
        preparation_priorities=[
            PreparationPriority(
                priority="Practice system design",
                reason="Multiple interview signals emphasize it.",
                evidence_urls=[source_url],
            ),
        ],
        study_plan=[
            StudyPlanItem(
                action="Complete one system design exercise.",
                focus="System design",
                evidence_urls=[source_url],
            ),
        ],
    )

    assert intelligence.key_topics[0].topic == "System design"
    assert str(
        intelligence.key_topics[0].evidence_urls[0]
    ).startswith(source_url)
    assert (
        intelligence.likely_questions[0].question
        == "How would you design a scalable API?"
    )
    assert (
        intelligence.preparation_priorities[0].priority
        == "Practice system design"
    )
    assert intelligence.study_plan[0].focus == "System design"


def test_interview_intelligence_allows_empty_sections() -> None:
    intelligence = InterviewIntelligence()

    assert intelligence.key_topics == []
    assert intelligence.likely_questions == []
    assert intelligence.preparation_priorities == []
    assert intelligence.study_plan == []
