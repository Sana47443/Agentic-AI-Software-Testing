from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

Technique = Literal["equivalence_partitioning","boundary_value_analysis","decision_table","state_transition"]
Category = Literal["functional","boundary","negative","edge"]

class TestCase(BaseModel):
    id: str
    name: str
    category: Category
    technique: Technique
    rationale: str
    input: dict[str, Any] = Field(default_factory=dict)
    expected: dict[str, Any] = Field(default_factory=dict)
    source_evidence: list[str] = Field(default_factory=list)
    unsupported_assumptions: list[str] = Field(default_factory=list)
    requires_human_review: bool = False

class TestCaseSuite(BaseModel):
    requirement: str
    selected_techniques: list[Technique]
    test_cases: list[TestCase]

class GeneratedDatum(BaseModel):
    test_case_id: str
    category: Literal["valid","invalid","edge"]
    values: dict[str, Any]
    rationale: str

class RiskScore(BaseModel):
    module: str
    predicted_defects: float
    risk_score: float

class ScheduleDecision(BaseModel):
    should_run_regression: bool
    reason: str
    changed_modules: list[str]
    high_risk_changed_modules: list[str]
    threshold: float

class FunctionCoverage(BaseModel):
    function: str
    covered: bool
    matching_tests: list[str] = Field(default_factory=list)

class CoverageReport(BaseModel):
    total_functions: int
    covered_functions: int
    coverage_percent: float
    functions: list[FunctionCoverage]

class EvaluationResult(BaseModel):
    requirement: str
    runs: int
    gold_concepts: list[str]
    concepts_found: list[str]
    requirement_coverage: float
    unsupported_assumption_rate: float
    valid_case_rate: float
    consistency: float
    human_review_rate: float
