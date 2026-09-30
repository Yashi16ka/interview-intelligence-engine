from pydantic import BaseModel, Field, HttpUrl


class ResearchRequest(BaseModel):
    company: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    role: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )


class ResearchStatsResponse(BaseModel):
    raw_count: int
    normalized_count: int
    unique_count: int
    relevant_count: int


class ResearchEvidenceResponse(BaseModel):
    source: str
    title: str
    url: HttpUrl
    purpose: str
    provider: str
    score: int
    matched_terms: list[str]


class ResearchResponse(BaseModel):
    company: str
    role: str
    status: str
    stats: ResearchStatsResponse
    evidence: list[ResearchEvidenceResponse]
