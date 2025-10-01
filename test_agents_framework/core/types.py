from __future__ import annotations
from typing import Literal, Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ChangeDelta(BaseModel):
	files_changed: List[str] = Field(default_factory=list)
	insertions: int = 0
	deletions: int = 0
	modules_touched: List[str] = Field(default_factory=list)


class RiskSignal(BaseModel):
	source: str
	score: float = Field(ge=0.0, le=1.0)
	reasons: List[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
	overall_score: float = Field(ge=0.0, le=1.0)
	signals: List[RiskSignal] = Field(default_factory=list)


class TestTarget(BaseModel):
	path: str
	kind: Literal["unit","integration","e2e","api"] = "unit"
	metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionRequest(BaseModel):
	agent: str
	targets: List[TestTarget] = Field(default_factory=list)
	delta: Optional[ChangeDelta] = None
	risk: Optional[RiskAssessment] = None
	context: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
	target: TestTarget
	success: bool
	duration_ms: int
	stdout: Optional[str] = None
	stderr: Optional[str] = None
	artifacts: Dict[str, str] = Field(default_factory=dict)
	telemetry: Dict[str, Any] = Field(default_factory=dict)


class AgentMessage(BaseModel):
	sender: str
	recipient: Optional[str] = None
	type: Literal["announce","request","result","broadcast"]
	payload: Dict[str, Any] = Field(default_factory=dict)
	correlation_id: Optional[str] = None
