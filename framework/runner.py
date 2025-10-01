from __future__ import annotations

import os
import sys
import time
import glob
import pathlib
from typing import List, Dict, Any

from rich.console import Console
from junitparser import JUnitXml

from .config import load_suite_config, load_baseline, save_baseline
from .agents.human_gate import HumanGateAgent
from .reporting.html_report import render_html_report

console = Console()


def _collect_test_files(includes: List[str]) -> List[str]:
	files: List[str] = []
	for pattern in includes:
		matches = glob.glob(pattern, recursive=True)
		files.extend(sorted(matches))
	return files


def _run_pytest(pytest_args: List[str]) -> int:
	# Import late to avoid making it a hard dependency at import time
	import pytest
	return pytest.main(pytest_args)


def _parse_junit(junit_path: str) -> Dict[str, Any]:
	xml = JUnitXml.fromfile(junit_path)
	total = xml.tests
	failures = xml.failures + xml.errors
	skipped = xml.skipped
	passed = total - failures - skipped
	return {
		"total": int(total),
		"passed": int(passed),
		"failed": int(failures),
		"skipped": int(skipped),
	}


def run_suite(suite_path: pathlib.Path, retries: int = 0, workers: int = 0, auto_approve: bool = False) -> int:
	config = load_suite_config(str(suite_path))
	stamp = time.strftime("%Y%m%d-%H%M%S")
	suite_name = config.name
	artifacts_dir = pathlib.Path(".artifacts") / suite_name / stamp
	reports_dir = pathlib.Path(".reports")
	artifacts_dir.mkdir(parents=True, exist_ok=True)
	reports_dir.mkdir(parents=True, exist_ok=True)

	# Select tests
	selected_files = _collect_test_files(config.includes)
	if not selected_files:
		console.print(f"[yellow]No test files matched includes for suite '{suite_name}'.[/yellow]")

	junit_path = artifacts_dir / "junit.xml"
	pytest_args: List[str] = [*selected_files, "-q", f"--junitxml={junit_path}", *config.pytest_args]

	attempt = 0
	last_code = 0
	while attempt <= retries:
		if attempt > 0:
			console.print(f"[cyan]Retry attempt {attempt} for suite '{suite_name}'[/cyan]")
		last_code = _run_pytest(pytest_args)
		metrics = _parse_junit(str(junit_path)) if junit_path.exists() else {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
		if metrics.get("failed", 0) == 0:
			break
		attempt += 1

	# Metrics after final attempt
	metrics = _parse_junit(str(junit_path)) if junit_path.exists() else {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
	baseline_path = os.path.join("baselines", f"{suite_name}.json")
	baseline_metrics = load_baseline(baseline_path)

	agent = HumanGateAgent(suite_name=suite_name)
	approved, reason = agent.evaluate_and_gate(
		current_metrics=metrics,
		baseline_metrics=baseline_metrics,
		thresholds={
			"allowed_failures": getattr(config.thresholds, "allowed_failures", 0),
			"allowed_new_failures": getattr(config.thresholds, "allowed_new_failures", 0),
		},
		auto_approve=auto_approve,
	)

	# Render HTML report
	report_path = reports_dir / f"{suite_name}_{stamp}.html"
	render_html_report(
		output_path=str(report_path),
		suite_name=suite_name,
		description=config.description,
		metrics=metrics,
		baseline_metrics=baseline_metrics,
		junit_path=str(junit_path),
		attempts=attempt + 1,
		approved=approved,
		reason=reason,
	)
	console.print(f"[green]HTML report:[/green] {report_path}")

	# Update baseline if approved and different
	if approved and (baseline_metrics != metrics):
		save_baseline(baseline_path, metrics)
		console.print(f"[green]Baseline updated:[/green] {baseline_path}")

	# Exit code: 0 if within thresholds or approved; otherwise 1
	if approved:
		return 0
	return 1

