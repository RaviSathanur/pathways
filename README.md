# Pathways

A dependency-free, non-interactive Python application that gives Dani a next-step recommendation from the synthetic data in `SPEC.md`.

Run the app with:

```powershell
python pathways.py
```

Run the acceptance tests with:

```powershell# Pathways: AI-Assisted Development Submission

## Section A: Build Summary

This Pathways slice serves Dani, a 17-year-old high school senior looking for a hands-on career step before winter break. The AI guide successfully evaluates her situation and routes her to the Northline Electrical Apprenticeship (PRG-02) because its November 30 deadline requires immediate action.

In this build, the data boundary enforcement, payload sanitization, orchestration logic, and evaluation harness are entirely real. The LLM inference itself is mocked locally. This ensures a zero-dependency, one-command execution for reviewers without requiring paid API keys or network calls.

The biggest trade-off made in this 30-minute window was prioritizing backend privacy architecture over a frontend mobile UI. By building a CLI application rather than a deployed React Native app, I guaranteed bulletproof deterministic data sanitization and a robust automated testing harness, which are critical for state agency approval.

The three automated checks prove that: 1) the Minors' Data Boundary is strictly enforced (PII never enters the model payload), 2) grounding is maintained (the model cites correct Source IDs and dates), and 3) the system safely routes unverified questions to a human advisor (ADV-01). However, one thing these string-matching tests would miss is a prompt injection attack (e.g., if a user typed 'ignore previous instructions' into their preferences).

The other persona, Marcus (34, laid off), would use this exact same planner. Because his profile indicates he is over 18, the sanitization layer would handle his payload differently, safely passing his adult financial context directly to the model to match him with the evening CDL training (PRG-05) and Dislocated Worker Funds (AID-B).

## Section B: AI Usage Log

**Interaction 1: The Initial Build and the Forced-Choice Mistake**
*   **What I asked the AI to help with:** I provided the `SPEC.md`, the synthetic data, and Dani's persona details, asking the AI to build the single-file Python app and mock LLM. 
*   **What it gave me:** A functional Python script that routed Dani to the Electrical Apprenticeship. However, the app included an interactive terminal menu forcing the user to choose an interest from a predefined list (e.g., "Press 2 for Electrical"). 
*   **What I kept, changed, or rejected, and why:** I **rejected** the multiple-choice UI. The prompt stated Dani was "torn" between options; forcing her to choose her path upfront defeated the entire purpose of an AI guide.

**Interaction 2: The Critical Redirection (Timeline/Preference Routing)**
*   **What I asked the AI to help with:** "Remove the multiple-choice UI. Dani is torn and should not pick the path herself. Update the app to take a pre-built profile, safely extract only her `preference` ('hands-on') and `timeline` ('before winter break'), and pass only those to the LLM so *it* can evaluate the deadlines and make the recommendation. Ensure PII is stripped."
*   **What it gave me:** A `sanitize_for_llm` function that acted as a middleman. It successfully dropped her name and raw notes, extracted only the safe variables, and passed them to the mock model.
*   **What I kept, changed, or rejected, and why:** I **kept** this architecture. It solved two problems at once: it created a strict deterministic data boundary protecting the minor's PII, and it allowed the model to accurately recommend PRG-02 based on the Nov 30 deadline without forcing the user to self-diagnose.

**Interaction 3: The Evaluation Harness**
*   **What I asked the AI to help with:** "Write three `pytest` functions that prove the data boundary works, grounding is enforced, and unknowns route to ADV-01."
*   **What it gave me:** Functional assertions checking the model payloads and responses. 
*   **What I kept, changed, or rejected, and why:** I **kept** the logic but **changed** the assertion failure messages to be highly descriptive (e.g., `FAIL: Minor's name leaked into model payload!`) so any state agency running the test would immediately understand the exact privacy failure without digging through a stack trace.
python -m unittest -v
```

The local profile's name, age, and advisor note are never included in the model payload. Only the allowlisted preference, timeline, and synthetic data table are passed to the rule-based mock model. Each call appends its exact JSON payload and response to `model-calls.log` in the current directory.