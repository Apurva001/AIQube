from __future__ import annotations
import json
import os
from typing import List, Tuple
from git import Repo
from .types import ChangeDelta, RiskAssessment, RiskSignal


class DeltaAnalyzer:
	def __init__(self, repo_path: str) -> None:
		self.repo_path = repo_path
		self.repo = Repo(repo_path)

	def compute_delta(self, base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> ChangeDelta:
		diff = self.repo.git.diff("--name-status", base_ref, head_ref)
		files_changed: List[str] = []
		modules: List[str] = []
		insertions = 0
		deletions = 0
		for line in diff.splitlines():
			parts = line.strip().split("\t")
			if len(parts) >= 2:
				status, path = parts[0], parts[-1]
				files_changed.append(path)
				segments = path.split("/")
				if segments:
					modules.append(segments[0])
		# Use numstat for insertions/deletions
		numstat = self.repo.git.diff("--numstat", base_ref, head_ref)
		for line in numstat.splitlines():
			p = line.split("\t")
			if len(p) >= 3 and p[0].isdigit() and p[1].isdigit():
				insertions += int(p[0])
				deletions += int(p[1])
		return ChangeDelta(files_changed=files_changed, insertions=insertions, deletions=deletions, modules_touched=sorted(set(modules)))


class RiskEngine:
	def assess(self, delta: ChangeDelta, hotspots: List[str]) -> RiskAssessment:
		signals: List[RiskSignal] = []
		# Churn-based risk
		churn = min(1.0, (delta.insertions + delta.deletions) / 1000.0)
		signals.append(RiskSignal(source="churn", score=churn, reasons=[f"{delta.insertions}+{delta.deletions} LOC changed"]))
		# Breadth of change
		breadth = min(1.0, len(delta.files_changed) / 50.0)
		signals.append(RiskSignal(source="breadth", score=breadth, reasons=[f"{len(delta.files_changed)} files changed"]))
		# Historical hotspots near change
		hotspot_boost = min(1.0, len(hotspots) / 20.0)
		if hotspots:
			signals.append(RiskSignal(source="hotspots", score=hotspot_boost, reasons=["historical failures near change area"]))
		# Simple aggregation
		overall = 1.0 - (1.0 - churn) * (1.0 - breadth) * (1.0 - hotspot_boost)
		return RiskAssessment(overall_score=overall, signals=signals)

