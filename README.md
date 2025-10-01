# Test Agents Framework

A modular, multi-agent testing framework with local decision-making, inter-agent communication, and continuous learning.

## Features

- Specialized agents: Regression, Sanity, Risk-Detector, API Validator
- Local decision-making based on git deltas, risk signals, and telemetry
- Inter-agent communication via in-memory message bus and shared blackboard
- Continuous learning backed by SQLite: historical failures, hotspots, flakiness

## Quickstart

```bash
python3 -m venv .venv --without-pip
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
.venv/bin/python get-pip.py
.venv/bin/pip install -r requirements.txt

PYTHONPATH=. .venv/bin/python -m test_agents_framework.cli run --help
```

Example run (against current repo, no diff):
```bash
PYTHONPATH=. .venv/bin/python -m test_agents_framework.cli run --repo . --base-ref HEAD --head-ref HEAD --no-api
```

## Architecture

- `core/types.py`: Pydantic models for deltas, risk, targets, requests, results, messages
- `core/base.py`: `Agent` abstract base and `Tooling` execution facade
- `core/comms.py`: `MessageBus` (pub/sub with dedupe) and `Blackboard` (shared store)
- `core/learning.py`: SQLite-backed store for results, hotspots, flakiness queries
- `core/risk.py`: `DeltaAnalyzer` (git-based) and `RiskEngine` (simple aggregation)
- `core/orchestrator.py`: Plans eligible agents, dedupes by role, records telemetry
- `agents/specialized.py`: Regression, Sanity, Risk-Detector, API Validator agents
- `cli.py`: Typer-based CLI to wire everything together

## Notes

- The `Tooling` implementation is a placeholder; integrate your real test runner.
- Learning store grows over time; queries guide risk and target selection.
