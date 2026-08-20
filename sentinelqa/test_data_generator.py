from __future__ import annotations
from faker import Faker
from .models import GeneratedDatum, TestCaseSuite
fake = Faker()

class TestDataGenerator:
    def generate(self, suite: TestCaseSuite) -> list[GeneratedDatum]:
        output = []
        for case in suite.test_cases:
            base = dict(case.input)
            label = "valid" if case.category == "functional" else ("edge" if case.category in {"boundary","edge"} else "invalid")
            output.append(GeneratedDatum(test_case_id=case.id, category=label, values=base, rationale=f"Input generated from the {case.category} test case."))
            if "email" in base:
                output.extend([
                    GeneratedDatum(test_case_id=case.id, category="valid", values={**base,"email":fake.email()}, rationale="Schema-compatible synthetic email."),
                    GeneratedDatum(test_case_id=case.id, category="invalid", values={**base,"email":"not-an-email"}, rationale="Deliberately malformed email."),
                    GeneratedDatum(test_case_id=case.id, category="edge", values={**base,"email":"a+b@example.co"}, rationale="Valid but less typical email form."),
                ])
        return output
