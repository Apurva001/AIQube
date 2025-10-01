from __future__ import annotations
from typing import Iterable, List
from ..core.base import Agent, Tooling
from ..core.types import ExecutionRequest, ExecutionResult, TestTarget


class RegressionAgent(Agent):
	def __init__(self, tooling: Tooling) -> None:
		super().__init__(name="regression", role="Regression Agent")
		self.tooling = tooling

	def can_handle(self, request: ExecutionRequest) -> bool:
		return True

	def select_targets(self, request: ExecutionRequest) -> List[TestTarget]:
		return [t for t in request.targets if t.kind in ("unit", "integration")]

	def execute(self, request: ExecutionRequest) -> Iterable[ExecutionResult]:
		return self.tooling.run_tests(self.select_targets(request))


class SanityAgent(Agent):
	def __init__(self, tooling: Tooling) -> None:
		super().__init__(name="sanity", role="Sanity Agent")
		self.tooling = tooling

	def can_handle(self, request: ExecutionRequest) -> bool:
		return True

	def select_targets(self, request: ExecutionRequest) -> List[TestTarget]:
		return [t for t in request.targets if t.kind in ("unit", "api")][:20]

	def execute(self, request: ExecutionRequest) -> Iterable[ExecutionResult]:
		return self.tooling.run_tests(self.select_targets(request))


class RiskDetectorAgent(Agent):
	def __init__(self, tooling: Tooling) -> None:
		super().__init__(name="risk", role="Risk-Detector")
		self.tooling = tooling

	def can_handle(self, request: ExecutionRequest) -> bool:
		return bool(request.risk and request.risk.overall_score >= 0.2)

	def select_targets(self, request: ExecutionRequest) -> List[TestTarget]:
		# prioritize targets if risk exists
		return request.targets

	def execute(self, request: ExecutionRequest) -> Iterable[ExecutionResult]:
		return self.tooling.run_tests(self.select_targets(request))


class APIValidatorAgent(Agent):
	def __init__(self, tooling: Tooling) -> None:
		super().__init__(name="api", role="API Validator")
		self.tooling = tooling

	def can_handle(self, request: ExecutionRequest) -> bool:
		return any(t.kind == "api" for t in request.targets)

	def select_targets(self, request: ExecutionRequest) -> List[TestTarget]:
		return [t for t in request.targets if t.kind == "api"]

	def execute(self, request: ExecutionRequest) -> Iterable[ExecutionResult]:
		return self.tooling.run_tests(self.select_targets(request))

