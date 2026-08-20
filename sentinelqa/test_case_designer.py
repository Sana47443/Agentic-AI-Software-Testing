from __future__ import annotations
import re, uuid
from .llm import LLMProvider, get_provider
from .models import TestCase, TestCaseSuite

SYSTEM_PROMPT = """
You are a QA engineering agent that creates black-box software test cases.
Use these techniques when appropriate: equivalence_partitioning, boundary_value_analysis, decision_table, state_transition.
Generate functional, boundary, negative, and edge cases as justified by the requirement.
CRITICAL GROUNDING RULES:
1. Do not invent API status codes, timeouts, limits, business rules, or implementation details unless explicitly present.
2. If useful expected behavior is not specified, put the limitation in unsupported_assumptions and set requires_human_review=true.
3. source_evidence must contain short phrases copied or closely derived from the requirement.
4. Return JSON only with selected_techniques and test_cases.
"""

class TestCaseDesigner:
    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or get_provider()

    def design(self, requirement: str) -> TestCaseSuite:
        if not requirement.strip():
            raise ValueError("Requirement cannot be empty.")
        payload = self.provider.complete_json(SYSTEM_PROMPT, f"REQUIREMENT:\n{requirement}")
        cases = []
        for raw in payload.get("test_cases", []):
            raw = dict(raw)
            raw.setdefault("id", str(uuid.uuid4()))
            raw = self._apply_grounding_guardrails(requirement, raw)
            cases.append(TestCase.model_validate(raw))
        if not cases:
            raise ValueError("No test cases were generated.")
        return TestCaseSuite(requirement=requirement, selected_techniques=payload.get("selected_techniques", ["equivalence_partitioning"]), test_cases=cases)

    @staticmethod
    def _apply_grounding_guardrails(requirement: str, raw: dict) -> dict:
        req_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", requirement))
        expected_text = str(raw.get("expected", {}))
        expected_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", expected_text))
        unsupported_numbers = expected_numbers - req_numbers
        assumptions = list(raw.get("unsupported_assumptions") or [])
        if unsupported_numbers:
            assumptions.append("Expected behavior introduces numeric value(s) not present in the requirement: " + ", ".join(sorted(unsupported_numbers)))
        raw["unsupported_assumptions"] = list(dict.fromkeys(assumptions))
        raw["requires_human_review"] = bool(raw.get("requires_human_review") or raw["unsupported_assumptions"])
        return raw
