from __future__ import annotations
import re
from statistics import mean
from .models import EvaluationResult
from .test_case_designer import TestCaseDesigner

def normalize(text:str)->str: return re.sub(r"[^a-z0-9 ]+"," ",text.lower())
def concept_present(concept:str,suite_text:str)->bool:
    tokens=[t for t in normalize(concept).split() if len(t)>2]
    if not tokens: return False
    hay=normalize(suite_text); hits=sum(t in hay for t in tokens)
    return hits/len(tokens)>=0.6

class Evaluator:
    def __init__(self,designer=None): self.designer=designer or TestCaseDesigner()
    def evaluate_requirement(self,requirement:str,gold_concepts:list[str],runs:int=3)->EvaluationResult:
        suites=[self.designer.design(requirement) for _ in range(runs)]
        run_found=[]; unsupported=[]; valid=[]; review=[]
        for suite in suites:
            txt=" ".join(c.name+" "+c.rationale+" "+str(c.input)+" "+str(c.expected) for c in suite.test_cases)
            found={c for c in gold_concepts if concept_present(c,txt)}; run_found.append(found)
            n=len(suite.test_cases) or 1
            unsupported.append(sum(bool(c.unsupported_assumptions) for c in suite.test_cases)/n)
            valid.append(sum(bool(c.name and c.category and c.technique and c.rationale) for c in suite.test_cases)/n)
            review.append(sum(c.requires_human_review for c in suite.test_cases)/n)
        all_found=set().union(*run_found) if run_found else set()
        coverage=len(all_found)/len(gold_concepts) if gold_concepts else 1.0
        consistency=1.0 if runs<=1 or not gold_concepts else mean(sum(concept in found for found in run_found)/runs for concept in gold_concepts)
        return EvaluationResult(requirement=requirement,runs=runs,gold_concepts=gold_concepts,concepts_found=sorted(all_found),requirement_coverage=round(coverage,3),unsupported_assumption_rate=round(mean(unsupported),3),valid_case_rate=round(mean(valid),3),consistency=round(consistency,3),human_review_rate=round(mean(review),3))
