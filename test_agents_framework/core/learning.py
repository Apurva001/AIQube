from __future__ import annotations
import json
import os
import sqlite3
import time
from typing import Dict, Iterable, List, Optional, Tuple
from .types import ExecutionResult, TestTarget


class LearningStore:
	"""SQLite-backed store for test outcomes and heuristics queries."""

	def __init__(self, db_path: str) -> None:
		self.db_path = db_path
		self._ensure_schema()

	def _ensure_schema(self) -> None:
		os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
		with sqlite3.connect(self.db_path) as conn:
			conn.execute(
				"""
				CREATE TABLE IF NOT EXISTS test_results (
					id INTEGER PRIMARY KEY,
					timestamp INTEGER NOT NULL,
					target_path TEXT NOT NULL,
					kind TEXT NOT NULL,
					success INTEGER NOT NULL,
					duration_ms INTEGER NOT NULL,
					agent TEXT,
					commit_sha TEXT,
					delta_modules TEXT
				);
				"""
			)
			conn.execute(
				"""
				CREATE INDEX IF NOT EXISTS idx_results_target ON test_results(target_path);
				"""
			)

	def record_result(
		self,
		result: ExecutionResult,
		agent: str,
		commit_sha: Optional[str] = None,
		delta_modules: Optional[List[str]] = None,
	) -> None:
		with sqlite3.connect(self.db_path) as conn:
			conn.execute(
				"""
				INSERT INTO test_results (
					timestamp, target_path, kind, success, duration_ms, agent, commit_sha, delta_modules
				) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
				""",
				(
					int(time.time()),
					result.target.path,
					result.target.kind,
					1 if result.success else 0,
					result.duration_ms,
					agent,
					commit_sha,
					json.dumps(delta_modules or []),
				),
			)

	def get_failure_hotspots(self, modules: List[str], top_n: int = 20) -> List[str]:
		"""Return test paths frequently failing when modules are involved."""
		if not modules:
			return []
		module_like = [f"%{m}%" for m in modules]
		placeholders = ",".join(["?"] * len(module_like))
		query = f"""
			SELECT target_path, SUM(1 - success) AS failures, COUNT(*) AS runs
			FROM test_results
			WHERE " + " OR ".join([f"delta_modules LIKE {p}" for p in module_like]) + "
			GROUP BY target_path
			HAVING runs >= 2
			ORDER BY failures DESC, runs DESC
			LIMIT ?
		"""
		with sqlite3.connect(self.db_path) as conn:
			rows = conn.execute(query, (*module_like, top_n)).fetchall()
		return [r[0] for r in rows]

	def get_flaky_tests(self, min_runs: int = 5, failure_rate_gt: float = 0.3) -> List[str]:
		query = """
			SELECT target_path, SUM(1 - success) * 1.0 / COUNT(*) AS fail_rate, COUNT(*) AS runs
			FROM test_results
			GROUP BY target_path
			HAVING runs >= ? AND fail_rate >= ?
			ORDER BY fail_rate DESC
		"""
		with sqlite3.connect(self.db_path) as conn:
			rows = conn.execute(query, (min_runs, failure_rate_gt)).fetchall()
		return [r[0] for r in rows]

