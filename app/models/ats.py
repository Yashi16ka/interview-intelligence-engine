from pydantic import BaseModel, HttpUrl


class ATSCandidate(BaseModel):
    provider: str
    board_url: HttpUrl
    slug: str
