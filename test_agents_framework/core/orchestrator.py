from __future__ import annotations
import uuid
from typing import Iterable, List
from .types import ExecutionRequest, ExecutionResult, AgentMessage, TestTarget
from .comms import MessageBus, Blackboard
from .learning import LearningStore
from .risk import RiskEngine
from .base import Agent


class Orchestrator:
	def __init__(self, bus: MessageBus, board: Blackboard, store: LearningStore, risk_engine: RiskEngine) -> None:
		self.bus = bus
		self.board = board
		self.store = store
		self.risk_engine = risk_engine
		self.agents: List[Agent] = []

	def register(self, agent: Agent) -> None:
		self.agents.append(agent)
		self.bus.publish(agent.announce())

	def plan(self, request: ExecutionRequest) -> List[Agent]:
		eligible = [a for a in self.agents if a.can_handle(request)]
		# dedupe by role: if multiple agents of same role, pick first
		seen_roles = set()
		planned: List[Agent] = []
		for a in eligible:
			if a.role in seen_roles:
				continue
			seen_roles.add(a.role)
			planned.append(a)
		return planned

	def execute(self, request: ExecutionRequest, commit_sha: str | None = None) -> List[ExecutionResult]:
		results: List[ExecutionResult] = []
		planned_agents = self.plan(request)
		for agent in planned_agents:
			corr = str(uuid.uuid4())
			self.bus.publish(
				AgentMessage(sender="orchestrator", recipient=agent.name, type="request", payload={"targets": len(request.targets)}, correlation_id=corr)
			)
			for result in agent.execute(request):
				results.append(result)
				self.store.record_result(result, agent=agent.name, commit_sha=commit_sha, delta_modules=(request.delta.modules_touched if request.delta else []))
			self.bus.publish(
				AgentMessage(sender=agent.name, recipient="orchestrator", type="result", payload={"results": len(results)}, correlation_id=corr)
			)
		return results

