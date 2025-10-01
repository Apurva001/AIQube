VENV ?= .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: venv install smoke regression run format lint clean venv-clean

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -r requirements.txt

smoke: install
	$(PY) cli.py --suite suites/smoke.yaml --auto-approve

regression: install
	$(PY) cli.py --suite suites/regression.yaml --auto-approve

run:
	@if [ -z "$(SUITE)" ]; then echo "Usage: make run SUITE=path/to/suite.yaml"; exit 1; fi
	$(PY) cli.py run --suite $(SUITE)

clean:
	rm -rf .reports .artifacts .approvals baselines .pytest_cache

venv-clean:
	rm -rf $(VENV)
