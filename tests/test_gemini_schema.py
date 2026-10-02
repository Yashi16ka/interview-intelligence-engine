import json

from app.models.synthesis import SynthesisResponse
from app.services.gemini_schema import flatten_json_schema


def test_flatten_json_schema_removes_defs_and_refs() -> None:
    schema = SynthesisResponse.model_json_schema()

    flattened = flatten_json_schema(schema)
    serialized = json.dumps(flattened)

    assert "$defs" not in serialized
    assert "$ref" not in serialized

    key_topic = (
        flattened["properties"]["key_topics"]["items"]
    )

    assert key_topic["type"] == "object"
    assert "topic" in key_topic["properties"]
    assert "reason" in key_topic["properties"]
    assert "evidence_ids" in key_topic["properties"]


def test_flatten_json_schema_preserves_all_sections() -> None:
    flattened = flatten_json_schema(
        SynthesisResponse.model_json_schema()
    )

    properties = flattened["properties"]

    assert set(properties) == {
        "key_topics",
        "likely_questions",
        "preparation_priorities",
        "study_plan",
    }
