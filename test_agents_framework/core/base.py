from __future__ import annotations
import time
import uuid
from abc import ABC, abstractmethod
from typing import Iterable, List
from .types import ExecutionRequest, ExecutionResult, AgentMessage, TestTarget


class Agent(ABC):
	name: str
	role: str

	def __init__(self, name: str, role: str) -> None:
		self.name = name
		self.role = role

	@abstractmethod
	def can_handle(self, request: ExecutionRequest) -> bool:
		...

	@abstractmethod
	def select_targets(self, request: ExecutionRequest) -> List[TestTarget]:
		...

	@abstractmethod
	def execute(self, request: ExecutionRequest) -> Iterable[ExecutionResult]:
		...

	def announce(self) -> AgentMessage:
		return AgentMessage(
			sender=self.name,
			type="announce",
			payload={"role": self.role},
			correlation_id=str(uuid.uuid4()),
		)


class Tooling:
	"""Facade for running tests and system commands. Injectable for unit tests."""

	def run_tests(self, targets: List[TestTarget]) -> List[ExecutionResult]:
		results: List[ExecutionResult] = []
		start = time.time()
		for target in targets:
			# Placeholder execution: mark success and synthetic timing
			results.append(
				ExecutionResult(
					target=target,
					success=True,
					duration_ms=int((time.time() - start) * 1000),
					telemetry={"executor": "noop"},
				)
			)
		return results
