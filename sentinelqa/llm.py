from __future__ import annotations
import json, os, re
from typing import Protocol
import requests
from dotenv import load_dotenv
load_dotenv()

class LLMProvider(Protocol):
    def complete_json(self, system_prompt: str, user_prompt: str) -> dict: ...

class GroqProvider:
    """Minimal OpenAI-compatible Groq client."""
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=90,
        )
        response.raise_for_status()
        return json.loads(response.json()["choices"][0]["message"]["content"])

class DeterministicDemoProvider:
    """Offline stand-in that follows the same structured contract as the LLM."""
    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        req_match = re.search(r"REQUIREMENT:\s*(.*)", user_prompt, flags=re.I | re.S)
        requirement = req_match.group(1).strip() if req_match else user_prompt.strip()
        lower = requirement.lower()
        techniques = ["equivalence_partitioning"]
        if re.search(r"\b(min|max|between|range|characters?|days?|hours?|\$|%|\d+)\b", lower):
            techniques.append("boundary_value_analysis")
        if any(x in lower for x in ["if ", "unless", "role", "permission", "combination"]):
            techniques.append("decision_table")
        if any(x in lower for x in ["state", "status", "transition", "locked", "active", "inactive"]):
            techniques.append("state_transition")

        cases = []
        def add(name, category, technique, inp, expected, evidence, unsupported=None):
            cases.append({
                "name": name, "category": category, "technique": technique,
                "rationale": f"Exercise {category} behavior grounded in the requirement.",
                "input": inp, "expected": expected, "source_evidence": evidence,
                "unsupported_assumptions": unsupported or [],
                "requires_human_review": bool(unsupported),
            })

        if "email" in lower:
            add("Valid email address","functional","equivalence_partitioning",{"email":"user@example.com"},{"result":"request accepted and reset flow initiated"},["email address","reset link"] if "reset" in lower else ["email address"])
            add("Malformed email address","negative","equivalence_partitioning",{"email":"invalidemail"},{"result":"input rejected or validation requested"},["email address"])
            add("Email containing surrounding spaces","edge","equivalence_partitioning",{"email":" user@example.com "},{"result":"handle according to documented normalization policy"},["email address"],["Whitespace normalization behavior is not specified."])
            add("Missing email input","negative","equivalence_partitioning",{"email":""},{"result":"required input should not proceed"},["entering my email address"])

        nums = [int(x.replace(",", "")) for x in re.findall(r"\b\d[\d,]*\b", requirement)]
        if len(nums) >= 2:
            lo, hi = min(nums), max(nums)
            add(f"Lower boundary {lo}","boundary","boundary_value_analysis",{"value":lo},{"result":"accepted if boundary is inclusive"},[str(lo)],["Boundary inclusivity may require specification."] if "inclusive" not in lower else [])
            add(f"Below lower boundary {lo-1}","negative","boundary_value_analysis",{"value":lo-1},{"result":"rejected"},[str(lo)])
            add(f"Upper boundary {hi}","boundary","boundary_value_analysis",{"value":hi},{"result":"accepted if boundary is inclusive"},[str(hi)],["Boundary inclusivity may require specification."] if "inclusive" not in lower else [])
            add(f"Above upper boundary {hi+1}","negative","boundary_value_analysis",{"value":hi+1},{"result":"rejected"},[str(hi)])

        if "password" in lower and "reset" in lower:
            add("Registered user requests password reset","functional","equivalence_partitioning",{"email":"registered@example.com"},{"result":"reset link is sent"},["reset my password","receiving a reset link"])

        if not cases:
            add("Nominal valid scenario","functional",techniques[0],{"scenario":"valid input"},{"result":"requirement succeeds"},[requirement[:120]])
            add("Missing required input","negative",techniques[0],{"scenario":"missing input"},{"result":"operation should not incorrectly succeed"},[requirement[:120]])

        return {"selected_techniques": list(dict.fromkeys(techniques)), "test_cases": cases}

def get_provider() -> LLMProvider:
    return GroqProvider() if os.getenv("GROQ_API_KEY") else DeterministicDemoProvider()
