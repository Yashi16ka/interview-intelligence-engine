from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    company: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=150)


class ResearchResponse(BaseModel):
    company: str
    role: str
    status: str
