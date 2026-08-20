from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from pydantic import TypeAdapter
from .coverage_analyzer import CoverageAnalyzer
from .defect_predictor import DefectPredictor
from .evaluator import Evaluator
from .models import RiskScore, TestCaseSuite
from .scheduler import TestScheduler
from .test_case_designer import TestCaseDesigner
from .test_data_generator import TestDataGenerator
from .utils import read_json, write_json
OUTPUTS=Path("outputs"); OUTPUTS.mkdir(exist_ok=True)

def suite_to_dataframe(suite):
    rows=[]
    for c in suite.test_cases:
        row={"id":c.id,"name":c.name,"category":c.category,"technique":c.technique,"rationale":c.rationale,"requires_human_review":c.requires_human_review,"unsupported_assumptions":" | ".join(c.unsupported_assumptions)}
        row.update({f"input.{k}":v for k,v in c.input.items()}); row.update({f"expected.{k}":v for k,v in c.expected.items()}); rows.append(row)
    return pd.DataFrame(rows)

def command_design(requirement):
    suite=TestCaseDesigner().design(requirement); write_json(OUTPUTS/"test_cases.json",suite); df=suite_to_dataframe(suite); df.to_csv(OUTPUTS/"test_cases.csv",index=False); print(df.to_string(index=False)); print("\nSaved outputs/test_cases.json and outputs/test_cases.csv")

def command_generate_data(input_path):
    suite=TestCaseSuite.model_validate(read_json(input_path)); data=TestDataGenerator().generate(suite); write_json(OUTPUTS/"test_data.json",data); pd.DataFrame([x.model_dump() for x in data]).to_csv(OUTPUTS/"test_data.csv",index=False); print(f"Generated {len(data)} rows.")

def command_train_risk(input_path):
    p=DefectPredictor(); scores=p.train_and_score(input_path); p.save_model(OUTPUTS/"defect_predictor.joblib"); write_json(OUTPUTS/"risk_scores.json",scores); print(pd.DataFrame([x.model_dump() for x in scores]).to_string(index=False))

def command_schedule(risk_path,changed_path,threshold):
    scores=TypeAdapter(list[RiskScore]).validate_python(read_json(risk_path)); decision=TestScheduler().decide(read_json(changed_path),scores,threshold); write_json(OUTPUTS/"schedule_decision.json",decision); print(json.dumps(decision.model_dump(),indent=2))

def command_coverage(src,tests):
    report=CoverageAnalyzer().analyze(src,tests); write_json(OUTPUTS/"coverage_report.json",report); print(json.dumps(report.model_dump(),indent=2))

def command_evaluate(benchmark_path,runs):
    benchmark=read_json(benchmark_path); ev=Evaluator(); results=[ev.evaluate_requirement(x["requirement"],x["gold_concepts"],runs) for x in benchmark]; write_json(OUTPUTS/"evaluation_results.json",results); df=pd.DataFrame([x.model_dump() for x in results]); cols=["requirement_coverage","unsupported_assumption_rate","valid_case_rate","consistency","human_review_rate"]; print(df[cols].to_string(index=False)); summary={c:round(float(df[c].mean()),3) for c in cols}; write_json(OUTPUTS/"evaluation_summary.json",summary); print("\nSummary:\n"+json.dumps(summary,indent=2))

def command_demo():
    req=read_json("data/sample_requirements.json")[0]["requirement"]
    print("\n=== 1. TEST CASE DESIGN ==="); suite=TestCaseDesigner().design(req); write_json(OUTPUTS/"test_cases.json",suite); df=suite_to_dataframe(suite); df.to_csv(OUTPUTS/"test_cases.csv",index=False); print(df.to_string(index=False))
    print("\n=== 2. TEST DATA GENERATION ==="); data=TestDataGenerator().generate(suite); write_json(OUTPUTS/"test_data.json",data); pd.DataFrame([x.model_dump() for x in data]).to_csv(OUTPUTS/"test_data.csv",index=False); print(f"Generated {len(data)} rows.")
    print("\n=== 3. DEFECT PREDICTION ==="); p=DefectPredictor(); scores=p.train_and_score("data/module_metrics.csv"); p.save_model(OUTPUTS/"defect_predictor.joblib"); write_json(OUTPUTS/"risk_scores.json",scores); print(pd.DataFrame([x.model_dump() for x in scores]).to_string(index=False))
    print("\n=== 4. RISK-BASED SCHEDULING ==="); decision=TestScheduler().decide(read_json("data/changed_modules.json"),scores); write_json(OUTPUTS/"schedule_decision.json",decision); print(json.dumps(decision.model_dump(),indent=2))
    print("\n=== 5. COVERAGE ANALYSIS ==="); report=CoverageAnalyzer().analyze("sample_app/src","sample_app/tests"); write_json(OUTPUTS/"coverage_report.json",report); print(json.dumps(report.model_dump(),indent=2))
    print("\n=== 6. AI EVALUATION ==="); command_evaluate("data/gold_benchmark.json",3)
    print("\nDemo complete. See outputs/.")

def main():
    parser=argparse.ArgumentParser(description="Agentic AI software-testing system")
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("design"); p.add_argument("--requirement",required=True)
    p=sub.add_parser("generate-data"); p.add_argument("--input",default="outputs/test_cases.json")
    p=sub.add_parser("train-risk"); p.add_argument("--input",default="data/module_metrics.csv")
    p=sub.add_parser("schedule"); p.add_argument("--risk",default="outputs/risk_scores.json"); p.add_argument("--changed",default="data/changed_modules.json"); p.add_argument("--threshold",type=float,default=0.65)
    p=sub.add_parser("coverage"); p.add_argument("--src",default="sample_app/src"); p.add_argument("--tests",default="sample_app/tests")
    p=sub.add_parser("evaluate"); p.add_argument("--benchmark",default="data/gold_benchmark.json"); p.add_argument("--runs",type=int,default=3)
    sub.add_parser("demo")
    a=parser.parse_args()
    {"design":lambda:command_design(a.requirement),"generate-data":lambda:command_generate_data(a.input),"train-risk":lambda:command_train_risk(a.input),"schedule":lambda:command_schedule(a.risk,a.changed,a.threshold),"coverage":lambda:command_coverage(a.src,a.tests),"evaluate":lambda:command_evaluate(a.benchmark,a.runs),"demo":command_demo}[a.command]()

if __name__=="__main__": main()
