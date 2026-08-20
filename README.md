# SentinelQA — Agentic AI System for Intelligent Software Testing

A complete runnable reconstruction of an agentic software-testing project built around five cooperating components:

1. **Test Case Designer** — converts requirements into structured black-box test cases.
2. **Test Data Generator** — produces valid, invalid, and edge-case inputs.
3. **Defect Predictor** — uses supervised ML to rank modules by defect risk.
4. **Test Scheduler / Planner** — recommends regression runs when changed modules are high risk.
5. **Coverage Analyzer** — maps source functions to existing tests and identifies uncovered functions.

An additional **Evaluation Harness** measures generated test suites for requirement coverage, unsupported assumptions, validity, consistency, and human-review rate.

## Architecture

```text
Requirements / Jira / Gherkin
          |
          v
 Test Case Designer
          |
          v
 Test Data Generator
          |
          +--------------------+
                               |
Git / code metrics ---> Defect Predictor
                               |
                               v
                     Test Scheduler / Planner
                               |
                               v
                         CI/CD decision
                               |
                               v
                         Test Results
                               |
                               v
                     Coverage Analyzer
                               |
                               +----> uncovered behavior feedback
```

The design intentionally combines deterministic code, supervised ML, and generative AI rather than using an LLM for every task.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m sentinelqa.cli demo
```

The full demo runs without an API key using a deterministic local provider so the repository is immediately executable.

## Use a Real LLM

Copy the environment template:

```bash
cp .env.example .env
```

Add a Groq API key:

```text
GROQ_API_KEY=your_key_here
```

Optionally change the model:

```text
GROQ_MODEL=llama-3.3-70b-versatile
```

Then run:

```bash
python -m sentinelqa.cli design --requirement "As a user, I should be able to reset my password by entering my email address and receiving a reset link."
```

No credentials are embedded in this repository. Never commit `.env`.

## Main Commands

```bash
python -m sentinelqa.cli demo
python -m sentinelqa.cli design --requirement "Users may transfer between $1 and $5,000 per transaction."
python -m sentinelqa.cli generate-data --input outputs/test_cases.json
python -m sentinelqa.cli train-risk --input data/module_metrics.csv
python -m sentinelqa.cli schedule --risk outputs/risk_scores.json --changed data/changed_modules.json
python -m sentinelqa.cli coverage --src sample_app/src --tests sample_app/tests
python -m sentinelqa.cli evaluate --benchmark data/gold_benchmark.json --runs 3
```

## Evaluation

The evaluation layer answers four practical questions:

- **Requirement coverage:** how many human-defined testing concepts were generated?
- **Unsupported assumptions:** did the model invent behavior that was absent from the source requirement?
- **Validity:** are generated cases structurally usable?
- **Consistency:** does the same requirement produce the important concepts across repeated runs?

A deterministic grounding guardrail also flags numeric expected behavior that appears in generated output but not in the requirement. This is useful for catching plausible-looking inventions such as unsupported HTTP status codes.

## Project Structure

```text
SentinelQA_Agentic_AI_Testing/
├── sentinelqa/
│   ├── cli.py
│   ├── models.py
│   ├── llm.py
│   ├── test_case_designer.py
│   ├── test_data_generator.py
│   ├── defect_predictor.py
│   ├── scheduler.py
│   ├── coverage_analyzer.py
│   ├── evaluator.py
│   └── utils.py
├── data/
├── sample_app/
├── notebooks/
├── outputs/
├── requirements.txt
└── README.md
```

## Security

The included data is synthetic. The project deliberately does not connect to real Jira, GitHub Actions, Jenkins, Slack, email, or customer systems by default. Those integrations can be added later using authorized credentials and environment variables.
