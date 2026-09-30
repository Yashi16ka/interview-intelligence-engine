from pydantic import BaseModel

from app.models.source import SourceResult


class EvidenceItem(BaseModel):
    result: SourceResult
    purpose: str
    provider: str
