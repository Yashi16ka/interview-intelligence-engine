import re


COMPANY_SUFFIXES = {
    "inc",
    "incorporated",
    "corp",
    "corporation",
    "llc",
    "ltd",
    "limited",
    "ai",
}


def build_company_slugs(
    company: str,
) -> list[str]:
    words = re.findall(
        r"[a-z0-9]+",
        company.lower(),
    )

    if not words:
        return []

    candidates = [
        "".join(words),
        "-".join(words),
    ]

    trimmed_words = list(words)

    while (
        len(trimmed_words) > 1
        and trimmed_words[-1] in COMPANY_SUFFIXES
    ):
        trimmed_words.pop()

    if trimmed_words != words:
        candidates.extend(
            [
                "".join(trimmed_words),
                "-".join(trimmed_words),
            ]
        )

    unique: list[str] = []

    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)

    return unique
