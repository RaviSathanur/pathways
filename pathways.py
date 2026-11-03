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

INTERESTS = {
    "1": ("Medical assistant", "PRG-01"),
    "2": ("Electrical apprenticeship", "PRG-02"),
    "3": ("Computer science", "PRG-03"),
    "4": ("IT support", "PRG-04"),
    "5": ("CDL training", "PRG-05"),
}


@dataclass(frozen=True)
class LocalProfile:
    name: str
    age: int
    advisor_note: str


def classify_question(question: str) -> str:
    """Reduce free text locally to a controlled category before prompt creation."""
    normalized = question.casefold()
    if any(word in normalized for word in ("aid", "grant", "financial", "fund")):
        return "aid"
    if any(word in normalized for word in ("seat", "availability", "available", "open spot")):
        return "availability"
    if any(word in normalized for word in ("tuition", "cost", "price", "fee")):
        return "cost"
    if any(word in normalized for word in ("eligibility", "eligible", "qualify")):
        return "eligibility"
    if any(word in normalized for word in ("deadline", "close")):
        return "deadline"
    if any(word in normalized for word in ("start", "when")):
        return "start_date"
    return "overview"


def build_prompt(interest_id: str, question_type: str) -> str:
    selected_ids = {interest_id, "ADV-01"}
    if question_type == "aid":
        selected_ids.update(("AID-A", "AID-B"))
    sources = [source for source in SOURCES if source["id"] in selected_ids]
    return json.dumps(
        {
            "task": question_type,
            "selected_interest": interest_id,
            "synthetic_sources": sources,
            "rules": [
                "Use only the supplied synthetic sources.",
                "Cite each source ID and its last_checked date.",
                "For unknown details, say they cannot be confirmed and offer ADV-01.",
            ],
        },
        ensure_ascii=True,
    )


def mock_llm(prompt: str) -> str:
    """Generate a grounded deterministic response and append the exact exchange."""
    payload = json.loads(prompt)
    sources = {source["id"]: source for source in payload["synthetic_sources"]}
    task = payload["task"]
    interest = sources[payload["selected_interest"]]
    citation = f'Source: {interest["id"]}; Last checked: {interest["last_checked"]}.'

    if task == "availability":
        advisor = sources["ADV-01"]
        response = (
            f'Seat availability for {interest["record"]} cannot be confirmed from the available data. '
            f'Please ask an advisor to confirm. Source: {interest["id"]}; '
            f'Last checked: {interest["last_checked"]}. Source: {advisor["id"]}; '
            f'Last checked: {advisor["last_checked"]}. {advisor["facts"]}'
        )
    elif task == "aid":
        aid_sources = [sources[source_id] for source_id in ("AID-A", "AID-B")]
        aid_text = " ".join(
            f'{source["record"]}: {source["facts"]} '
            f'Source: {source["id"]}; Last checked: {source["last_checked"]}.'
            for source in aid_sources
        )
        advisor = sources["ADV-01"]
        response = (
            f'{interest["record"]}: {interest["facts"]} {citation} {aid_text} '
            f'Exact award amounts cannot be confirmed. Please ask an advisor. '
            f'Source: {advisor["id"]}; Last checked: {advisor["last_checked"]}. {advisor["facts"]}'
        )
    elif task == "cost":
        if "tuition" in interest["facts"].casefold():
            response = f'{interest["record"]}: {interest["facts"]}. {citation}'
        else:
            advisor = sources["ADV-01"]
            response = (
                f'An exact cost for {interest["record"]} cannot be confirmed from the available data. '
                f'Please ask an advisor. Source: {interest["id"]}; '
                f'Last checked: {interest["last_checked"]}. Source: {advisor["id"]}; '
                f'Last checked: {advisor["last_checked"]}. {advisor["facts"]}'
            )
    elif task in ("start_date", "deadline"):
        markers = ("start",) if task == "start_date" else ("close", "deadline")
        date_facts = [
            fact for fact in interest["facts"].split("; ")
            if any(marker in fact.casefold() for marker in markers)
        ]
        if date_facts:
            response = f'{interest["record"]}: {"; ".join(date_facts)}. {citation}'
        else:
            advisor = sources["ADV-01"]
            response = (
                f'A specific date for {interest["record"]} cannot be confirmed from the available data. '
                f'Please ask an advisor. Source: {interest["id"]}; '
                f'Last checked: {interest["last_checked"]}. Source: {advisor["id"]}; '
                f'Last checked: {advisor["last_checked"]}. {advisor["facts"]}'
            )
    elif task == "eligibility":
        advisor = sources["ADV-01"]
        response = (
            f'Individual eligibility for {interest["record"]} cannot be confirmed from the available data. '
            f'Please ask an advisor to confirm. Source: {interest["id"]}; '
            f'Last checked: {interest["last_checked"]}. Source: {advisor["id"]}; '
            f'Last checked: {advisor["last_checked"]}. {advisor["facts"]}'
        )
    else:
        response = f'{interest["record"]}: {interest["facts"]}. {citation}'

    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps({"prompt": prompt, "response": response}, ensure_ascii=True) + "\n")
    return response


def recommend(
    profile: LocalProfile,
    interest_id: str,
    question: str,
    llm: Callable[[str], str] | None = None,
) -> str:
    """Keep profile fields local and send only classified, synthetic payload data."""
    del profile
    safe_prompt = build_prompt(interest_id, classify_question(question))
    return (llm or mock_llm)(safe_prompt)


def main() -> None:
    print("Pathways | Next-step guide")
    name = input("Name for this local case [Dani]: ").strip() or "Dani"
    age_input = input("Age for this local case [17]: ").strip() or "17"
    try:
        age = int(age_input)
    except ValueError:
        print("Please enter an age as a whole number.")
        return
    advisor_note = input("Note to advisor (kept local): ")
    profile = LocalProfile(name=name, age=age, advisor_note=advisor_note)

    print("\nChoose an area of interest:")
    for key, (label, _) in INTERESTS.items():
        print(f"{key}. {label}")
    choice = input("Selection: ").strip()
    if choice not in INTERESTS:
        print("Please choose a listed interest.")
        return

    question = input("What would you like to know? ")
    print("\nRecommendation")
    print(recommend(profile, INTERESTS[choice][1], question))
    print("\nThe advisor note and profile were kept local.")


if __name__ == "__main__":
    main()