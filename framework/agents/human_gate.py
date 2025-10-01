from __future__ import annotations

import os
from typing import Dict, Tuple
from rich.console import Console

console = Console()


class HumanGateAgent:
	"""Simple gate that compares current vs baseline and applies thresholds.

	Approval rules:
	- If failures <= allowed_failures, approve
	- Else if HUMAN_APPROVED=1 or .approvals/<suite>.approved exists, approve
	- Else if auto_approve flag is True, approve
	- Otherwise, block
	"""

	def __init__(self, suite_name: str) -> None:
		self.suite_name = suite_name

	def evaluate_and_gate(
		self,
		current_metrics: Dict[str, int],
		baseline_metrics: Dict[str, int],
		thresholds: Dict[str, int],
		auto_approve: bool = False,
	) -> Tuple[bool, str]:
		failed = int(current_metrics.get("failed", 0))
		allowed_failures = int(thresholds.get("allowed_failures", 0))

		if failed <= allowed_failures:
			return True, f"Failures {failed} within allowed {allowed_failures}"

		approval_file = os.path.join(".approvals", f"{self.suite_name}.approved")
		if os.environ.get("HUMAN_APPROVED") == "1" or os.path.exists(approval_file):
			console.print(f"[yellow]Human override detected for '{self.suite_name}'.[/yellow]")
			return True, "Human override"

		if auto_approve:
			console.print("[yellow]Auto-approve enabled; proceeding despite failures.[/yellow]")
			return True, "Auto approve"

		return False, f"Failed {failed} exceeds allowed {allowed_failures}"

