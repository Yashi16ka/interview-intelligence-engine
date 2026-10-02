from pydantic import BaseModel, Field, HttpUrl


class KeyTopic(BaseModel):
    topic: str
    reason: str
    evidence_urls: list[HttpUrl] = Field(default_factory=list)


class LikelyQuestion(BaseModel):
    question: str
    rationale: str
    evidence_urls: list[HttpUrl] = Field(default_factory=list)


class PreparationPriority(BaseModel):
    priority: str
    reason: str
    evidence_urls: list[HttpUrl] = Field(default_factory=list)


class StudyPlanItem(BaseModel):
    action: str
    focus: str
    evidence_urls: list[HttpUrl] = Field(default_factory=list)


class InterviewIntelligence(BaseModel):
    key_topics: list[KeyTopic] = Field(default_factory=list)
    likely_questions: list[LikelyQuestion] = Field(
        default_factory=list
    )
    preparation_priorities: list[
        PreparationPriority
    ] = Field(default_factory=list)
    study_plan: list[StudyPlanItem] = Field(
        default_factory=list
    )
