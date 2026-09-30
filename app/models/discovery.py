from pydantic import BaseModel, HttpUrl


class DiscoveredSource(BaseModel):
    title: str
    url: HttpUrl
    purpose: str
    provider: str


class DiscoveryError(BaseModel):
    provider: str
    error_type: str
    message: str


class DiscoveryResults(BaseModel):
    sources: list[DiscoveredSource]
    errors: list[DiscoveryError]


class DiscoveredTarget(BaseModel):
    title: str
    url: HttpUrl
    purposes: list[str]
    providers: list[str]
