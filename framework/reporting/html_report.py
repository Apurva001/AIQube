from __future__ import annotations

import os
from typing import Dict
from jinja2 import Template


def render_html_report(
	output_path: str,
	suite_name: str,
	description: str,
	metrics: Dict[str, int],
	baseline_metrics: Dict[str, int],
	junit_path: str,
	attempts: int,
	approved: bool,
	reason: str,
) -> None:
	template = Template(
		"""
		<!doctype html>
		<html>
		<head>
			<meta charset="utf-8" />
			<title>{{ suite_name }} - Test Report</title>
			<style>
				body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 2rem; }
				h1 { margin-bottom: 0; }
				.status { padding: .25rem .5rem; border-radius: 6px; display: inline-block; }
				.ok { background: #e6ffed; color: #1a7f37; }
				.fail { background: #ffebe9; color: #b62324; }
				.grid { display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 1rem; margin-top: 1rem; }
				.card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; }
				pre { background: #f6f8fa; padding: 1rem; border-radius: 6px; overflow: auto; }
				a { color: #0969da; }
			</style>
		</head>
		<body>
			<h1>{{ suite_name }}</h1>
			<p>{{ description }}</p>
			<p>
				<span class="status {{ 'ok' if approved else 'fail' }}">{{ 'APPROVED' if approved else 'BLOCKED' }}</span>
				<span style="margin-left: .5rem; color: #57606a;">{{ reason }}</span>
			</p>
			<div class="grid">
				<div class="card"><strong>Total</strong><div>{{ metrics.total if metrics.total is defined else metrics['total'] }}</div></div>
				<div class="card"><strong>Passed</strong><div>{{ metrics.passed if metrics.passed is defined else metrics['passed'] }}</div></div>
				<div class="card"><strong>Failed</strong><div>{{ metrics.failed if metrics.failed is defined else metrics['failed'] }}</div></div>
				<div class="card"><strong>Skipped</strong><div>{{ metrics.skipped if metrics.skipped is defined else metrics['skipped'] }}</div></div>
			</div>
			<h3>Baseline</h3>
			<pre>{{ baseline_metrics | tojson(indent=2) }}</pre>
			<h3>JUnit XML</h3>
			<p>Saved at: <code>{{ junit_path }}</code></p>
			<h3>Attempts</h3>
			<p>{{ attempts }}</p>
		</body>
		</html>
		"""
	)
	content = template.render(
		suite_name=suite_name,
		description=description,
		metrics=metrics,
		baseline_metrics=baseline_metrics,
		junit_path=junit_path,
		attempts=attempts,
		approved=approved,
		reason=reason,
	)
	os.makedirs(os.path.dirname(output_path), exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as f:
		f.write(content)

