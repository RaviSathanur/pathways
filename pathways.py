"""Private-by-design next-step guide using synthetic program data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


LOG_PATH = Path("model-calls.log")

SOURCES = [
    {
        "id": "PRG-01",
        "record": "Cascade Community College, Medical Assistant Certificate",
        "facts": "3 quarters; day classes only; estimated total tuition 4,200 USD; next start Jan 6, 2027",
        "last_checked": "Oct 20, 2026",
    },
    {
        "id": "PRG-02",
        "record": "Northline Electrical Apprenticeship",
        "facts": "Paid; 4 years; starts at 55% of journey-level wage; applicants must be 18 by the program start date; HS diploma or GED required; applications close Nov 30, 2026; program starts Mar 1, 2027",
        "last_checked": "Oct 20, 2026",
    },
    {
        "id": "PRG-03",
        "record": "Riverbend University, BS Computer Science",
        "facts": "4 years; FAFSA or state aid application required; priority deadline Feb 1, 2027",
        "last_checked": "Oct 18, 2026",
    },
    {
        "id": "PRG-04",
        "record": "Cascade Community College, IT Support Certificate",
        "facts": "2 quarters; evening online option; estimated total tuition 2,100 USD; next start Jan 6, 2027",
        "last_checked": "Oct 20, 2026",
    },
    {
        "id": "PRG-05",
        "record": "Harbor Workforce Center, CDL Class A Training",
        "facts": "6 weeks; evening cohort available; eligible for dislocated-worker training funds",
        "last_checked": "Oct 15, 2026",
    },
    {
        "id": "AID-A",
        "record": "Evergreen Opportunity Grant (state)",
        "facts": "Income-based; apply through FAFSA or the state aid application; award amount varies",
        "last_checked": "Oct 18, 2026",
    },
    {
        "id": "AID-B",
        "record": "Dislocated Worker Training Funds",
        "facts": "Requires a layoff notice; apply through Harbor Workforce Center; covers approved training",
        "last_checked": "Oct 15, 2026",
    },
    {
        "id": "ADV-01",
        "record": "Human advisor hand-off",
        "facts": "Advisors confirm eligibility, seats, and award amounts. Response within 2 business days.",
        "last_checked": "n/a",
    },
]

@dataclass(frozen=True)
class LocalProfile:
    name: str
    age: int
    advisor_note: str
    preference: str
    timeline: str


def sanitize_for_llm(profile: LocalProfile) -> dict[str, object]:
    """Allowlist non-identifying preferences and synthetic data for model use."""
    return {
        "preference": profile.preference,
        "timeline": profile.timeline,
        "synthetic_data": SOURCES,
    }


def mock_llm(safe_payload: dict[str, object]) -> str:
    """Route safe preferences against synthetic program deadlines and log the call."""
    sources = {
        source["id"]: source
        for source in safe_payload["synthetic_data"]
    }
    apprenticeship = sources["PRG-02"]
    advisor = sources["ADV-01"]
    preference = str(safe_payload["preference"]).casefold()
    timeline = str(safe_payload["timeline"]).casefold()
    program_facts = apprenticeship["facts"].split("; ")
    application_deadline = next(
        (fact for fact in program_facts if fact.startswith("applications close ")),
        None,
    )
    program_start = next(
        (fact for fact in program_facts if fact.startswith("program starts ")),
        None,
    )

    if (
        "hands-on" in preference
        and "before winter break" in timeline
        and application_deadline is not None
    ):
        response = (
            f'{apprenticeship["record"]} is a strong next step for a hands-on preference. '
            f'{application_deadline[0].upper() + application_deadline[1:]}, before winter break, '
            f'and the {program_start or "start date is not listed"}. '
            f'Applicants must be 18 by the program start date and have a high school diploma or GED. '
            '(Source ID: PRG-02, Last checked: Oct 20, 2026) '
            'Seat availability and individual eligibility cannot be confirmed. '
            f'Please contact an advisor (Source ID: ADV-01, Last checked: n/a). {advisor["facts"]}'
        )
    else:
        response = (
            'A recommendation cannot be confirmed for the supplied preference and timeline. '
            f'Please contact an advisor (Source ID: ADV-01, Last checked: n/a). {advisor["facts"]}'
        )

    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(
            json.dumps(
                {"payload": safe_payload, "response": response},
                ensure_ascii=True,
            )
            + "\n"
        )
    return response


def recommend(
    profile: LocalProfile,
    llm: Callable[[dict[str, object]], str] | None = None,
) -> str:
    return (llm or mock_llm)(sanitize_for_llm(profile))


def main() -> None:
    profile = LocalProfile(
        name="Dani",
        age=17,
        advisor_note="I would like to ask about workplace visits.",
        preference="hands-on work",
        timeline="before winter break",
    )
    print("Pathways | Next-step guide")
    print("\nProfile")
    print(f"Name: {profile.name}")
    print(f"Age: {profile.age}")
    print(f"Note to advisor: {profile.advisor_note}")
    print(f"Preference: {profile.preference}")
    print(f"Timeline: {profile.timeline}")
    print("\nRecommendation")
    print(recommend(profile))


if __name__ == "__main__":
    main()