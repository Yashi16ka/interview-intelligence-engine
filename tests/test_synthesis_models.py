from app.models.synthesis import SynthesisResponse


def test_synthesis_response_validates_structured_output() -> None:
    response = SynthesisResponse.model_validate(
        {
            "key_topics": [
                {
                    "topic": "System design",
                    "reason": "Appears in interview evidence.",
                    "evidence_ids": ["E1", "E2"],
                }
            ],
            "likely_questions": [
                {
                    "question": "How would you design an API?",
                    "rationale": "System design is emphasized.",
                    "evidence_ids": ["E1"],
                }
            ],
            "preparation_priorities": [
                {
                    "priority": "Practice system design",
                    "reason": "It appears across evidence.",
                    "evidence_ids": ["E1", "E2"],
                }
            ],
            "study_plan": [
                {
                    "action": "Complete one design exercise.",
                    "focus": "System design",
                    "evidence_ids": ["E1"],
                }
            ],
        }
    )

    assert response.key_topics[0].evidence_ids == [
        "E1",
        "E2",
    ]
    assert (
        response.likely_questions[0].question
        == "How would you design an API?"
    )


def test_synthesis_response_allows_empty_sections() -> None:
    response = SynthesisResponse()

    assert response.key_topics == []
    assert response.likely_questions == []
    assert response.preparation_priorities == []
    assert response.study_plan == []
