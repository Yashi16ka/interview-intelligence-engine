from pydantic import BaseModel, HttpUrl


class SourceResult(BaseModel):
    source: str
    title: str
    url: HttpUrl
    content: str


class CollectorError(BaseModel):
    source: str
    error_type: str
    message: str


class ResearchResults(BaseModel):
    results: list[SourceResult]
    errors: list[CollectorError]
