from pydantic import BaseModel, HttpUrl

from app.models.source import SourceResult


class BrowserFetchResult(BaseModel):
    requested_url: HttpUrl
    result: SourceResult
