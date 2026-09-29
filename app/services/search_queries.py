from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    purpose: str
    query: str


def build_interview_queries(
    company: str,
    role: str,
) -> list[SearchQuery]:
    company = company.strip()
    role = role.strip()

    return [
        SearchQuery(
            purpose="interview_experience",
            query=f'"{company}" "{role}" interview experience',
        ),
        SearchQuery(
            purpose="interview_questions",
            query=f'"{company}" "{role}" interview questions',
        ),
        SearchQuery(
            purpose="technical_interview",
            query=f'"{company}" software engineer technical interview',
        ),
    ]
