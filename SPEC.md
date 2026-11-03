# Pathways: Next-Step Slice Agent Specification

## 1. Outcome
Build a single-file Python application that acts as an AI guide for "Dani" (17, HS Senior). Do NOT build an interactive terminal menu or ask the user to select an interest ID from a list. Instead, hardcode Dani's pre-built local profile into the `main()` function: she prefers "hands-on work" and needs a next step "before winter break". The app must safely extract these preferences, process them against the synthetic data, and output a grounded recommendation.

## 2. Constraints & Rules (CRITICAL)
- **Minors' Data Boundary:** The user's name ("Dani"), age (17), and any raw free-text "Note to Advisor" MUST NOT be sent to the LLM. 
- **Payload Extraction:** Create a `sanitize_for_llm` function that takes the pre-built profile, strips the PII, and extracts only a safe `preference` (e.g., "hands-on") and `timeline` (e.g., "before winter break"). Pass ONLY these safe variables and the synthetic data table to the model.
- **No Forced Choice UI:** The system must use the LLM (not a user input menu) to evaluate the extracted timeline and preference against the program deadlines (specifically PRG-02's Nov 30 deadline) to make a recommendation.
- **Mocked LLM:** Do not use OpenAI/Anthropic APIs. Create a `mock_llm(safe_payload)` function that simulates rule-based routing based on the extracted timeline and preference. 
- **Audit Logging:** Every call to `mock_llm` must append the exact JSON payload and response to a local file named `model-calls.log`.
- **Grounded & Silent:** The LLM output must explicitly cite the `ID` and `Last checked` date (e.g., "(Source ID: PRG-02, Last checked: Oct 20, 2026)").
- **Handling Unknowns:** If a detail is missing (e.g., specific start dates not in the table, exact aid amounts), the system must state it cannot confirm and explicitly offer the advisor hand-off (ID: ADV-01).

## 3. Acceptance Criteria (Automated Checks)
The app must include a one-command test script (e.g., `pytest` or a custom test runner) that proves three things:
1. `test_minors_data_boundary`: Asserts that the string "Dani" and the free-text note are NOT present in the payload sent to the LLM.
2. `test_grounding_citations`: Asserts that the LLM output contains the correct source IDs (e.g., "PRG-02").
3. `test_unknowns_handling`: Asserts that when queried about unknown seat availability, the system falls back to "ADV-01".

## 4. Synthetic Data Set
| ID | Record | Facts you can rely on | Last checked |
|---|---|---|---|
| **PRG-01** | Cascade Community College, Medical Assistant Certificate | 3 quarters; day classes only; estimated total tuition 4,200 USD; next start Jan 6, 2027 | Oct 20, 2026 |
| **PRG-02** | Northline Electrical Apprenticeship | Paid; 4 years; starts at 55% of journey-level wage; applicants must be 18 by the program start date; HS diploma or GED required; applications close Nov 30, 2026; program starts Mar 1, 2027 | Oct 20, 2026 |
| **PRG-03** | Riverbend University, BS Computer Science | 4 years; FAFSA or state aid application required; priority deadline Feb 1, 2027 | Oct 18, 2026 |
| **PRG-04** | Cascade Community College, IT Support Certificate | 2 quarters; evening online option; estimated total tuition 2,100 USD; next start Jan 6, 2027 | Oct 20, 2026 |
| **PRG-05** | Harbor Workforce Center, CDL Class A Training | 6 weeks; evening cohort available; eligible for dislocated-worker training funds | Oct 15, 2026 |
| **AID-A** | Evergreen Opportunity Grant (state) | Income-based; apply through FAFSA or the state aid application; award amount varies | Oct 18, 2026 |
| **AID-B** | Dislocated Worker Training Funds | Requires a layoff notice; apply through Harbor Workforce Center; covers approved training | Oct 15, 2026 |
| **ADV-01** | Human advisor hand-off | Advisors confirm eligibility, seats, and award amounts. Response within 2 business days. | n/a |

*Anything not in this table (seat availability, a specific person's eligibility, exact aid amounts, start dates not listed) is unknown.*