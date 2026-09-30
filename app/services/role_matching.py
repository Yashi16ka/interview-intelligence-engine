import re


IGNORED_ROLE_TERMS = {
    "intern",
    "internship",
    "junior",
    "senior",
}


def extract_role_terms(
    query: str,
) -> set[str]:
    quoted_terms = re.findall(r'"([^"]+)"', query)

    if len(quoted_terms) >= 2:
        role = quoted_terms[1]
    else:
        role = query

    return {
        term.lower()
        for term in re.findall(
            r"[a-zA-Z0-9+#.]+",
            role,
        )
        if len(term) > 2
        and term.lower() not in IGNORED_ROLE_TERMS
    }


def matches_role(
    title: str,
    role_terms: set[str],
) -> bool:
    if not role_terms:
        return True

    title_terms = {
        term.lower()
        for term in re.findall(
            r"[a-zA-Z0-9+#.]+",
            title,
        )
    }

    return role_terms.issubset(title_terms)
