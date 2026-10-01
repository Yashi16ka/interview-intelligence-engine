from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    purpose: str
    query: str
    company: str | None = None
    role: str | None = None


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
            company=company,
            role=role,
        ),
        SearchQuery(
            purpose="interview_questions",
            query=f'"{company}" "{role}" interview questions',
            company=company,
            role=role,
        ),
        SearchQuery(
            purpose="technical_interview",
            query=f'"{company}" "{role}" technical interview',
            company=company,
            role=role,
        ),
        SearchQuery(
            purpose="role_requirements",
            query=f'"{company}" "{role}" jobs requirements',
            company=company,
            role=role,
        ),
        SearchQuery(
            purpose="company_engineering",
            query=f'"{company}" engineering technology',
            company=company,
            role=role,
        ),
    ]
