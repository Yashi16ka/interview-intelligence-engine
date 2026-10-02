from pydantic import BaseModel, Field


class SynthesisKeyTopic(BaseModel):
    topic: str
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)


class SynthesisLikelyQuestion(BaseModel):
    question: str
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)


class SynthesisPreparationPriority(BaseModel):
    priority: str
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)


class SynthesisStudyPlanItem(BaseModel):
    action: str
    focus: str
    evidence_ids: list[str] = Field(default_factory=list)


class SynthesisResponse(BaseModel):
    key_topics: list[SynthesisKeyTopic] = Field(
        default_factory=list
    )
    likely_questions: list[
        SynthesisLikelyQuestion
    ] = Field(default_factory=list)
    preparation_priorities: list[
        SynthesisPreparationPriority
    ] = Field(default_factory=list)
    study_plan: list[SynthesisStudyPlanItem] = Field(
        default_factory=list
    )
