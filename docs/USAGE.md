# Usage Guide

## Setup

1. Create and use the local virtual environment

```
make install
```

This creates `.venv` and installs dependencies inside it. All framework commands use `.venv/bin/python` automatically.

## Running suites

- Smoke:
```
make smoke
```

- Regression:
```
make regression
```

- Custom suite:
```
make run SUITE=suites/smoke.yaml
```

## Human-in-the-loop gating

If failures exceed thresholds, the run is blocked unless overridden.

- Auto-approve (CI): add `--auto-approve` or use `make smoke`/`make regression`.
- Human override: set env `HUMAN_APPROVED=1` or create `.approvals/<suite>.approved`.

## Adding tests

- Place tests under `tests/` (e.g., `tests/api/`, `tests/ui/`).
- Ensure they are discoverable by PyTest and referenced by a suite YAML `includes`.

## Adding/Editing suites

- Add YAML files under `suites/`:
```
name: smoke
includes:
  - tests/smoke/test_*.py
thresholds:
  allowed_failures: 0
pytest_args:
  - -q
```

## Reports and baselines

- JUnit XML: `.artifacts/<suite>/<timestamp>/junit.xml`
- HTML report: `.reports/<suite>_<timestamp>.html`
- Baselines: `baselines/<suite>.json` (auto-updated when approved)